"""
فحص صحة البوت
"""
import os
import sys
import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def health_check():
    """فحص صحة البوت"""
    try:
        # التحقق من وجود التوكن
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN غير موجود")
            return False
        
        # إنشاء البوت
        bot = Bot(token=token)
        
        # فحص الاتصال
        me = await bot.get_me()
        print(f"✅ البوت متصل: @{me.username}")
        
        # فحص قاعدة البيانات
        import sqlite3
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if len(tables) >= 2:
            print("✅ قاعدة البيانات جاهزة")
        else:
            print("⚠️ قاعدة البيانات تحتاج إعداد")
        
        return True
        
    except TelegramError as e:
        print(f"❌ خطأ في Telegram: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
