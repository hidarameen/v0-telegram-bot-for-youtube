"""
تعليمات إعداد بوت رفع الفيديوهات إلى YouTube
"""

def print_setup_instructions():
    instructions = """
🚀 تعليمات إعداد بوت رفع الفيديوهات إلى YouTube

📋 المتطلبات:
1. Python 3.8 أو أحدث
2. حساب Telegram
3. حساب Google/YouTube
4. مشروع في Google Cloud Console

🔧 خطوات الإعداد:

1️⃣ إنشاء بوت تلقرام:
   - اذهب إلى @BotFather في تلقرام
   - أرسل /newbot
   - اتبع التعليمات واحصل على التوكن

2️⃣ إعداد Google Cloud Console:
   - اذهب إلى https://console.cloud.google.com
   - أنشئ مشروع جديد أو اختر مشروع موجود
   - فعّل YouTube Data API v3
   - أنشئ OAuth 2.0 credentials
   - أضف redirect URI: http://localhost:8080/callback

3️⃣ تثبيت المكتبات:
   pip install -r requirements.txt

4️⃣ إنشاء ملف .env:
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   YOUTUBE_CLIENT_ID=your_google_client_id
   YOUTUBE_CLIENT_SECRET=your_google_client_secret
   REDIRECT_URI=http://localhost:8080/callback

5️⃣ تشغيل البوت:
   python telegram_youtube_bot.py

📱 استخدام البوت:
1. ابدأ محادثة مع البوت
2. اضغط /start
3. اربط حساب YouTube
4. اختر القناة
5. أرسل فيديو للرفع

⚠️ ملاحظات مهمة:
- تأكد من أن حساب YouTube لديه قناة
- الفيديوهات الكبيرة قد تستغرق وقتاً أطول
- احتفظ بنسخة احتياطية من قاعدة البيانات
- لا تشارك بيانات المصادقة مع أحد

🔒 الأمان:
- احفظ ملف .env في مكان آمن
- لا ترفع ملف .env إلى GitHub
- استخدم HTTPS في الإنتاج
- راجع صلاحيات البوت بانتظام

📞 الدعم:
إذا واجهت مشاكل، تحقق من:
- صحة التوكنات
- اتصال الإنترنت
- صلاحيات YouTube API
- مساحة التخزين المتاحة
    """
    
    print(instructions)

if __name__ == "__main__":
    print_setup_instructions()
