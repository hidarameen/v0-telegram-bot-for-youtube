"""
ملف تشغيل البوت
"""
from telegram_youtube_bot import YouTubeTelegramBot
from config import Config
import os
from dotenv import load_dotenv

def main():
    # تحميل متغيرات البيئة
    load_dotenv()
    
    try:
        # التحقق من صحة الإعدادات
        Config.validate()
        
        # إنشاء وتشغيل البوت
        print("🚀 بدء تشغيل بوت رفع الفيديوهات إلى YouTube...")
        bot = YouTubeTelegramBot()
        bot.run()
        
    except ValueError as e:
        print(f"❌ خطأ في الإعدادات: {e}")
        print("📝 تأكد من إنشاء ملف .env وتعبئة البيانات المطلوبة")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
