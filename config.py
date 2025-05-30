import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات البوت"""
    
    # إعدادات تلقرام
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # إعدادات YouTube API
    YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/callback')
    
    # إعدادات قاعدة البيانات
    DATABASE_PATH = 'bot_database.db'
    
    # إعدادات التحميل
    DOWNLOAD_PATH = 'downloads'
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    
    # نطاقات YouTube
    YOUTUBE_SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
    
    @classmethod
    def validate(cls):
        """التحقق من صحة الإعدادات"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'YOUTUBE_CLIENT_ID',
            'YOUTUBE_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        
        return True
