"""
إعداد وضع webhook للبوت على Render
"""
import os
import logging
import asyncio
from telegram import Bot
from telegram.ext import Application
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def setup_webhook():
    """إعداد webhook للبوت"""
    load_dotenv()
    
    # الحصول على متغيرات البيئة
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود")
        return False
    
    if not render_url:
        logger.error("❌ RENDER_EXTERNAL_URL غير موجود")
        logger.info("💡 يتم تعيين RENDER_EXTERNAL_URL تلقائيًا بواسطة Render")
        return False
    
    try:
        # إنشاء البوت
        bot = Bot(token=token)
        
        # الحصول على معلومات البوت
        bot_info = await bot.get_me()
        logger.info(f"✅ تم الاتصال بالبوت: @{bot_info.username}")
        
        # تعيين webhook
        webhook_url = f"{render_url}/webhook"
        await bot.set_webhook(url=webhook_url)
        
        # التحقق من إعداد webhook
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url == webhook_url:
            logger.info(f"✅ تم إعداد webhook بنجاح: {webhook_url}")
            return True
        else:
            logger.error(f"❌ فشل إعداد webhook. الرابط الحالي: {webhook_info.url}")
            return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد webhook: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_webhook())
