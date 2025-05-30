"""
نسخة webhook من البوت للعمل على Render
"""
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
from telegram_youtube_bot import YouTubeTelegramBot

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(title="YouTube Telegram Bot Webhook")

# إنشاء البوت
bot_instance = YouTubeTelegramBot()
application = Application.builder().token(bot_instance.telegram_token).build()

# إضافة المعالجات
application.add_handler(CommandHandler("start", bot_instance.start_command))
application.add_handler(CallbackQueryHandler(bot_instance.button_handler))
application.add_handler(MessageHandler(filters.VIDEO, bot_instance.handle_video))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_text_input))

@app.post("/webhook")
async def webhook(request: Request):
    """معالج webhook لتلقي تحديثات التلقرام"""
    try:
        # قراءة البيانات من الطلب
        data = await request.json()
        
        # معالجة التحديث
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة التحديث: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    """صفحة الترحيب"""
    return {
        "status": "online",
        "bot": "YouTube Telegram Bot",
        "webhook_endpoint": "/webhook"
    }

@app.get("/health")
async def health():
    """فحص صحة البوت"""
    try:
        # التحقق من اتصال البوت
        me = await application.bot.get_me()
        
        # التحقق من اتصال قاعدة البيانات
        db_status = bot_instance.db.test_connection()
        
        return {
            "status": "healthy",
            "bot_username": f"@{me.username}",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"❌ خطأ في فحص الصحة: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    # الحصول على منفذ من متغيرات البيئة أو استخدام 8000 كقيمة افتراضية
    port = int(os.getenv("PORT", 8000))
    
    # تشغيل التطبيق
    uvicorn.run(app, host="0.0.0.0", port=port)
