"""
التحقق من صحة متغيرات البيئة
"""
import os
from dotenv import load_dotenv

def validate_env():
    """التحقق من وجود جميع متغيرات البيئة المطلوبة"""
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # المتغيرات المطلوبة
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'توكن بوت التلقرام',
        'YOUTUBE_CLIENT_ID': 'معرف عميل Google',
        'YOUTUBE_CLIENT_SECRET': 'سر عميل Google',
        'DATABASE_URL': 'رابط قاعدة بيانات PostgreSQL'
    }
    
    # المتغيرات الاختيارية
    optional_vars = {
        'REDIRECT_URI': 'عنوان إعادة التوجيه',
        'NORTHFLANK_API_TOKEN': 'توكن Northflank API',
        'YOUTUBE_REFRESH_TOKEN': 'توكن تحديث OAuth ليوتيوب (للتخطي بدون رابط المصادقة)',
        'YOUTUBE_CHANNEL_ID': 'معرف القناة الافتراضية للرفع',
        'YOUTUBE_CHANNEL_NAME': 'اسم القناة الافتراضية (اختياري)'
    }
    
    print("🔍 فحص متغيرات البيئة...")
    print("=" * 50)
    
    missing_vars = []
    
    # فحص المتغيرات المطلوبة
    print("📋 المتغيرات المطلوبة:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # إخفاء جزء من القيمة للأمان
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: غير موجود - {description}")
            missing_vars.append(var)
    
    print("\n📋 المتغيرات الاختيارية:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ⚠️ {var}: غير موجود - {description}")
    
    print("=" * 50)
    
    if missing_vars:
        print(f"❌ متغيرات مفقودة: {', '.join(missing_vars)}")
        print("\n📝 لإصلاح المشكلة:")
        print("1. انسخ ملف .env.example إلى .env")
        print("2. عدّل ملف .env وأضف القيم المطلوبة")
        print("3. شغّل هذا السكريبت مرة أخرى للتحقق")
        return False
    else:
        print("✅ جميع المتغيرات المطلوبة موجودة!")
        return True

def create_env_template():
    """إنشاء ملف .env من القالب"""
    if os.path.exists('.env'):
        print("⚠️ ملف .env موجود بالفعل")
        return False
    
    if not os.path.exists('.env.example'):
        print("❌ ملف .env.example غير موجود")
        return False
    
    # نسخ القالب
    with open('.env.example', 'r', encoding='utf-8') as source:
        content = source.read()
    
    with open('.env', 'w', encoding='utf-8') as target:
        target.write(content)
    
    print("✅ تم إنشاء ملف .env من القالب")
    print("📝 الآن عدّل ملف .env وأضف بياناتك الحقيقية")
    return True

if __name__ == "__main__":
    print("🔧 أداة التحقق من متغيرات البيئة")
    print("=" * 50)
    
    # التحقق من وجود ملف .env
    if not os.path.exists('.env'):
        print("❌ ملف .env غير موجود")
        print("📝 سيتم إنشاؤه من القالب...")
        if create_env_template():
            print("\n🔍 فحص الملف الجديد...")
        else:
            exit(1)
    
    # التحقق من المتغيرات
    if validate_env():
        print("\n🎉 البوت جاهز للتشغيل!")
    else:
        print("\n❌ يرجى إصلاح المتغيرات المفقودة أولاً")
        exit(1)
