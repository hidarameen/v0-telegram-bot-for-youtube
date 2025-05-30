import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
import aiohttp
import aiofiles
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import sqlite3
from urllib.parse import urlencode

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class YouTubeTelegramBot:
    def __init__(self):
        # إعدادات البوت
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
        self.youtube_client_id = os.getenv('YOUTUBE_CLIENT_ID', 'YOUR_CLIENT_ID')
        self.youtube_client_secret = os.getenv('YOUTUBE_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8080/callback')
        
        # إعداد قاعدة البيانات
        self.init_database()
        
        # متغيرات مؤقتة لحفظ حالة المستخدمين
        self.user_states = {}
        self.pending_uploads = {}
        
        # نطاقات YouTube المطلوبة
        self.youtube_scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]

    def init_database(self):
        """إنشاء قاعدة البيانات وجداولها"""
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expiry TEXT,
                selected_channel_id TEXT,
                selected_channel_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل الرفع
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upload_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_title TEXT,
                video_id TEXT,
                upload_status TEXT,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_user_credentials(self, user_id: int) -> Optional[Credentials]:
        """جلب بيانات المصادقة للمستخدم"""
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT access_token, refresh_token, token_expiry 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            access_token, refresh_token, token_expiry = result
            if access_token:
                creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=self.youtube_client_id,
                    client_secret=self.youtube_client_secret
                )
                return creds
        return None

    def save_user_credentials(self, user_id: int, credentials: Credentials):
        """حفظ بيانات المصادقة للمستخدم"""
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, access_token, refresh_token, token_expiry)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            credentials.token,
            credentials.refresh_token,
            credentials.expiry.isoformat() if credentials.expiry else None
        ))
        
        conn.commit()
        conn.close()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        welcome_message = """
🎬 مرحباً بك في بوت رفع الفيديوهات إلى YouTube!

الميزات المتاحة:
📤 رفع الفيديوهات من التلقرام إلى YouTube
🔗 ربط حساب YouTube الخاص بك
📺 اختيار القناة المراد الرفع إليها
⚙️ إعدادات الفيديو (العنوان، الوصف، الخصوصية)

للبدء، اضغط على الأزرار أدناه:
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 ربط حساب YouTube", callback_data='connect_youtube')],
            [InlineKeyboardButton("📋 عرض الحالة", callback_data='show_status')],
            [InlineKeyboardButton("📺 اختيار القناة", callback_data='select_channel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    async def connect_youtube(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ربط حساب YouTube"""
        user_id = update.effective_user.id
        
        # إنشاء رابط المصادقة
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.youtube_client_id,
                    "client_secret": self.youtube_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.youtube_scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=str(user_id)
        )
        
        message = f"""
🔗 لربط حساب YouTube الخاص بك:

1️⃣ اضغط على الرابط أدناه
2️⃣ سجل الدخول إلى حساب Google
3️⃣ امنح الصلاحيات المطلوبة
4️⃣ انسخ الرمز الذي ستحصل عليه
5️⃣ أرسل الرمز هنا

🔗 رابط المصادقة:
{auth_url}

⚠️ بعد الموافقة، أرسل الرمز الذي ستحصل عليه.
        """
        
        # حفظ حالة المستخدم
        self.user_states[user_id] = 'waiting_auth_code'
        
        await update.callback_query.edit_message_text(message)

    async def handle_auth_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رمز المصادقة"""
        user_id = update.effective_user.id
        auth_code = update.message.text.strip()
        
        try:
            # إنشاء Flow للمصادقة
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.youtube_client_id,
                        "client_secret": self.youtube_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.youtube_scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # تبديل الرمز بالتوكن
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # حفظ بيانات المصادقة
            self.save_user_credentials(user_id, credentials)
            
            # إزالة حالة المستخدم
            if user_id in self.user_states:
                del self.user_states[user_id]
            
            await update.message.reply_text(
                "✅ تم ربط حساب YouTube بنجاح!\n\n"
                "يمكنك الآن اختيار القناة وبدء رفع الفيديوهات."
            )
            
        except Exception as e:
            logger.error(f"خطأ في المصادقة: {e}")
            await update.message.reply_text(
                "❌ حدث خطأ في المصادقة. تأكد من صحة الرمز وحاول مرة أخرى."
            )

    async def show_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة المستخدم"""
        user_id = update.effective_user.id
        
        # التحقق من ربط الحساب
        credentials = self.get_user_credentials(user_id)
        is_connected = credentials is not None
        
        # جلب معلومات القناة المختارة
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT selected_channel_name FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        selected_channel = result[0] if result and result[0] else None
        
        status_message = f"""
📊 حالة الحساب:

🔗 ربط YouTube: {'✅ مربوط' if is_connected else '❌ غير مربوط'}
📺 القناة المختارة: {selected_channel if selected_channel else '❌ لم يتم الاختيار'}

{'✅ يمكنك الآن رفع الفيديوهات!' if is_connected and selected_channel else '⚠️ أكمل الإعداد لبدء الرفع'}
        """
        
        keyboard = []
        if not is_connected:
            keyboard.append([InlineKeyboardButton("🔗 ربط حساب YouTube", callback_data='connect_youtube')])
        else:
            keyboard.append([InlineKeyboardButton("📺 اختيار قناة", callback_data='select_channel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(status_message, reply_markup=reply_markup)

    async def select_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار قناة YouTube"""
        user_id = update.effective_user.id
        
        credentials = self.get_user_credentials(user_id)
        if not credentials:
            await update.callback_query.answer("❌ يجب ربط حساب YouTube أولاً!")
            return
        
        try:
            # بناء خدمة YouTube
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # جلب قنوات المستخدم
            channels_response = youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            channels = channels_response.get('items', [])
            
            if not channels:
                await update.callback_query.edit_message_text(
                    "❌ لم يتم العثور على قنوات YouTube في حسابك."
                )
                return
            
            # إنشاء أزرار القنوات
            keyboard = []
            for channel in channels:
                channel_id = channel['id']
                channel_title = channel['snippet']['title']
                keyboard.append([
                    InlineKeyboardButton(
                        f"📺 {channel_title}",
                        callback_data=f'channel_{channel_id}_{channel_title}'
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                "📺 اختر القناة المراد الرفع إليها:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في جلب القنوات: {e}")
            await update.callback_query.edit_message_text(
                "❌ حدث خطأ في جلب القنوات. تأكد من صحة المصادقة."
            )

    async def handle_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_data: str):
        """معالجة اختيار القناة"""
        user_id = update.effective_user.id
        
        try:
            # استخراج معرف القناة واسمها
            parts = channel_data.split('_', 2)
            channel_id = parts[1]
            channel_name = parts[2]
            
            # حفظ القناة المختارة
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET selected_channel_id = ?, selected_channel_name = ?
                WHERE user_id = ?
            ''', (channel_id, channel_name, user_id))
            conn.commit()
            conn.close()
            
            await update.callback_query.edit_message_text(
                f"✅ تم اختيار القناة: {channel_name}\n\n"
                "يمكنك الآن إرسال الفيديوهات للرفع إلى YouTube!"
            )
            
        except Exception as e:
            logger.error(f"خطأ في اختيار القناة: {e}")
            await update.callback_query.answer("❌ حدث خطأ في اختيار القناة")

    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الفيديوهات المرسلة"""
        user_id = update.effective_user.id
        
        # التحقق من ربط الحساب
        credentials = self.get_user_credentials(user_id)
        if not credentials:
            await update.message.reply_text(
                "❌ يجب ربط حساب YouTube أولاً!\nاستخدم /start للبدء."
            )
            return
        
        # التحقق من اختيار القناة
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT selected_channel_id, selected_channel_name 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            keyboard = [[InlineKeyboardButton("📺 اختيار القناة", callback_data='select_channel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ يجب اختيار قناة YouTube أولاً!",
                reply_markup=reply_markup
            )
            return
        
        try:
            # إرسال رسالة تحضير
            status_message = await update.message.reply_text("📤 جاري تحضير الفيديو للرفع...")
            
            # تحميل الفيديو
            video_file = await update.message.video.get_file()
            file_path = f"downloads/{user_id}_{video_file.file_id}.mp4"
            
            # إنشاء مجلد التحميل إذا لم يكن موجوداً
            os.makedirs("downloads", exist_ok=True)
            
            # تحميل الفيديو
            await video_file.download_to_drive(file_path)
            
            # حفظ معلومات الفيديو
            video_info = {
                'file_path': file_path,
                'file_size': update.message.video.file_size,
                'duration': update.message.video.duration,
                'user_id': user_id,
                'step': 'waiting_title'
            }
            
            self.pending_uploads[user_id] = video_info
            self.user_states[user_id] = 'uploading_video'
            
            await status_message.edit_text(
                "📝 تم تحميل الفيديو بنجاح!\n\n"
                "الآن أرسل عنوان الفيديو:"
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الفيديو: {e}")
            await update.message.reply_text(
                "❌ حدث خطأ في معالجة الفيديو. حاول مرة أخرى."
            )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة النصوص المرسلة"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # تجاهل الأوامر
        if text.startswith('/'):
            return
        
        # معالجة رمز المصادقة
        if user_id in self.user_states and self.user_states[user_id] == 'waiting_auth_code':
            await self.handle_auth_code(update, context)
            return
        
        # معالجة تفاصيل الفيديو
        if user_id in self.pending_uploads and user_id in self.user_states:
            video_info = self.pending_uploads[user_id]
            
            if video_info['step'] == 'waiting_title':
                video_info['title'] = text
                video_info['step'] = 'waiting_description'
                await update.message.reply_text(
                    "📄 أرسل وصف الفيديو (أو اكتب 'تخطي' للتخطي):"
                )
                
            elif video_info['step'] == 'waiting_description':
                video_info['description'] = '' if text == 'تخطي' else text
                video_info['step'] = 'waiting_privacy'
                
                keyboard = [
                    [InlineKeyboardButton("🌍 عام", callback_data=f'privacy_public_{user_id}')],
                    [InlineKeyboardButton("🔒 غير مدرج", callback_data=f'privacy_unlisted_{user_id}')],
                    [InlineKeyboardButton("🔐 خاص", callback_data=f'privacy_private_{user_id}')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🎬 اختر مستوى الخصوصية:",
                    reply_markup=reply_markup
                )

    async def upload_to_youtube(self, update: Update, context: ContextTypes.DEFAULT_TYPE, privacy: str):
        """رفع الفيديو إلى YouTube"""
        user_id = update.effective_user.id
        
        if user_id not in self.pending_uploads:
            await update.callback_query.answer("❌ لم يتم العثور على فيديو للرفع")
            return
        
        video_info = self.pending_uploads[user_id]
        
        try:
            # إرسال رسالة بدء الرفع
            await update.callback_query.edit_message_text("📤 جاري رفع الفيديو إلى YouTube...")
            
            # جلب بيانات المصادقة
            credentials = self.get_user_credentials(user_id)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # جلب معرف القناة
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT selected_channel_id, selected_channel_name 
                FROM users WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            channel_id, channel_name = result
            
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'channelId': channel_id,
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': privacy
                }
            }
            
            # رفع الفيديو
            media = MediaFileUpload(
                video_info['file_path'],
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = insert_request.execute()
            video_id = response['id']
            
            # حفظ سجل الرفع
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO upload_logs 
                (user_id, video_title, video_id, upload_status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, video_info['title'], video_id, 'success'))
            conn.commit()
            conn.close()
            
            # رسالة النجاح
            success_message = f"""
✅ تم رفع الفيديو بنجاح!

📹 العنوان: {video_info['title']}
🔗 رابط الفيديو: https://youtube.com/watch?v={video_id}
🔒 الخصوصية: {privacy}
📺 القناة: {channel_name}
            """
            
            await update.callback_query.edit_message_text(success_message)
            
            # تنظيف الملفات
            if os.path.exists(video_info['file_path']):
                os.remove(video_info['file_path'])
            
            # إزالة البيانات المؤقتة
            del self.pending_uploads[user_id]
            if user_id in self.user_states:
                del self.user_states[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في رفع الفيديو: {e}")
            
            # حفظ سجل الخطأ
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO upload_logs 
                (user_id, video_title, video_id, upload_status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, video_info.get('title', 'Unknown'), None, f'error: {str(e)}'))
            conn.commit()
            conn.close()
            
            await update.callback_query.edit_message_text(
                "❌ حدث خطأ في رفع الفيديو إلى YouTube. حاول مرة أخرى."
            )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'connect_youtube':
            await self.connect_youtube(update, context)
        elif data == 'show_status':
            await self.show_status(update, context)
        elif data == 'select_channel':
            await self.select_channel(update, context)
        elif data.startswith('channel_'):
            await self.handle_channel_selection(update, context, data)
        elif data.startswith('privacy_'):
            privacy = data.split('_')[1]
            await self.upload_to_youtube(update, context, privacy)

    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(self.telegram_token).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
        
        # بدء التشغيل
        print("🤖 بدء تشغيل بوت رفع الفيديوهات إلى YouTube...")
        application.run_polling()


if __name__ == "__main__":
    # إنشاء وتشغيل البوت
    bot = YouTubeTelegramBot()
    bot.run()
