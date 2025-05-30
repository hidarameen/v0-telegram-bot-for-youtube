"""
اختبار الاتصال بقاعدة البيانات PostgreSQL
"""
import os
from dotenv import load_dotenv
from database import create_database_manager
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    print("🔍 اختبار الاتصال بقاعدة البيانات PostgreSQL...")
    print("=" * 60)
    
    # التحقق من وجود رابط قاعدة البيانات
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL غير موجود في ملف .env")
        print("📝 أضف DATABASE_URL إلى ملف .env")
        return False
    
    # إخفاء كلمة المرور في الرابط للعرض
    safe_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split(':')
            if len(user_pass) >= 2:
                safe_url = f"{user_pass[0]}:***@{parts[1]}"
    
    print(f"🔗 رابط قاعدة البيانات: {safe_url}")
    
    try:
        # إنشاء مدير قاعدة البيانات
        db_manager = create_database_manager()
        
        if not db_manager:
            print("❌ فشل في إنشاء مدير قاعدة البيانات")
            return False
        
        print("✅ تم إنشاء مدير قاعدة البيانات")
        
        # اختبار الاتصال
        if db_manager.test_connection():
            print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        else:
            print("❌ فشل في اختبار الاتصال")
            return False
        
        # اختبار العمليات الأساسية
        print("\n🧪 اختبار العمليات الأساسية...")
        
        # اختبار إنشاء مستخدم تجريبي
        test_user_data = {
            'user_id': 999999999,
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        if db_manager.create_or_update_user(test_user_data):
            print("✅ تم إنشاء مستخدم تجريبي")
        else:
            print("❌ فشل في إنشاء مستخدم تجريبي")
            return False
        
        # اختبار جلب المستخدم
        user = db_manager.get_user(999999999)
        if user:
            print(f"✅ تم جلب المستخدم: {user.username}")
        else:
            print("❌ فشل في جلب المستخدم")
            return False
        
        # اختبار الإحصائيات
        stats = db_manager.get_upload_stats(999999999)
        print(f"✅ الإحصائيات: {stats}")
        
        # اختبار عد المستخدمين
        users_count = db_manager.get_all_users_count()
        print(f"✅ عدد المستخدمين: {users_count}")
        
        # حذف المستخدم التجريبي
        with db_manager.get_session() as session:
            session.query(db_manager.User).filter(
                db_manager.User.user_id == 999999999
            ).delete()
            session.commit()
        print("✅ تم حذف المستخدم التجريبي")
        
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ قاعدة البيانات جاهزة للاستخدام")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def show_database_info():
    """عرض معلومات قاعدة البيانات"""
    
    load_dotenv()
    
    print("\n📊 معلومات قاعدة البيانات:")
    print("=" * 40)
    
    try:
        db_manager = create_database_manager()
        if not db_manager:
            print("❌ لا يمكن الاتصال بقاعدة البيانات")
            return
        
        # عدد المستخدمين
        total_users = db_manager.get_all_users_count()
        active_users = db_manager.get_active_users_count()
        
        print(f"👥 إجمالي المستخدمين: {total_users}")
        print(f"🟢 المستخدمين النشطين: {active_users}")
        
        # معلومات الجداول
        with db_manager.get_session() as session:
            # عدد سجلات الرفع
            upload_logs_count = session.query(db_manager.UploadLog).count()
            print(f"📤 سجلات الرفع: {upload_logs_count}")
            
            # آخر عمليات الرفع
            recent_uploads = session.query(db_manager.UploadLog)\
                .order_by(db_manager.UploadLog.upload_time.desc())\
                .limit(5).all()
            
            if recent_uploads:
                print(f"\n📋 آخر {len(recent_uploads)} عمليات رفع:")
                for upload in recent_uploads:
                    status_icon = "✅" if upload.upload_status == "success" else "❌"
                    print(f"  {status_icon} {upload.video_title[:30]}... - {upload.upload_time.strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        print(f"❌ خطأ في جلب المعلومات: {e}")

if __name__ == "__main__":
    print("🗄️ أداة اختبار قاعدة البيانات PostgreSQL")
    print("=" * 60)
    
    # اختبار الاتصال
    if test_database_connection():
        # عرض معلومات قاعدة البيانات
        show_database_info()
    else:
        print("\n❌ فشل في اختبار قاعدة البيانات")
        print("\n🔧 تحقق من:")
        print("1. صحة رابط DATABASE_URL في ملف .env")
        print("2. أن قاعدة البيانات متاحة ويمكن الوصول إليها")
        print("3. صحة بيانات المصادقة (اسم المستخدم وكلمة المرور)")
        print("4. أن المنفذ صحيح ومفتوح")
