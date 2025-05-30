"""
إدارة قاعدة بيانات PostgreSQL
"""
import os
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# إنشاء قاعدة النماذج
Base = declarative_base()

class User(Base):
    """نموذج المستخدمين"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime)
    selected_channel_id = Column(String(255))
    selected_channel_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UploadLog(Base):
    """نموذج سجل الرفع"""
    __tablename__ = 'upload_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    video_title = Column(String(500))
    video_description = Column(Text)
    video_id = Column(String(255))
    video_url = Column(String(500))
    file_size = Column(Integer)
    duration = Column(Integer)
    privacy_status = Column(String(50))
    upload_status = Column(String(100))
    error_message = Column(Text)
    channel_id = Column(String(255))
    channel_name = Column(String(255))
    upload_time = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        
    def connect(self):
        """الاتصال بقاعدة البيانات"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # تغيير إلى True لرؤية استعلامات SQL
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # إنشاء الجداول
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("✅ تم الاتصال بقاعدة البيانات PostgreSQL بنجاح")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return False
    
    def get_session(self) -> Session:
        """الحصول على جلسة قاعدة البيانات"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بقاعدة البيانات"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"❌ فشل اختبار الاتصال: {e}")
            return False
    
    # ===== عمليات المستخدمين =====
    
    def get_user(self, user_id: int) -> Optional[User]:
        """جلب بيانات المستخدم"""
        try:
            with self.get_session() as session:
                return session.query(User).filter(User.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"خطأ في جلب المستخدم {user_id}: {e}")
            return None
    
    def create_or_update_user(self, user_data: Dict) -> bool:
        """إنشاء أو تحديث المستخدم"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.user_id == user_data['user_id']).first()
                
                if user:
                    # تحديث المستخدم الموجود
                    for key, value in user_data.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    user.updated_at = datetime.utcnow()
                else:
                    # إنشاء مستخدم جديد
                    user = User(**user_data)
                    session.add(user)
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في حفظ المستخدم: {e}")
            return False
    
    def save_user_credentials(self, user_id: int, access_token: str, 
                            refresh_token: str, token_expiry: datetime) -> bool:
        """حفظ بيانات المصادقة"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.user_id == user_id).first()
                
                if user:
                    user.access_token = access_token
                    user.refresh_token = refresh_token
                    user.token_expiry = token_expiry
                    user.updated_at = datetime.utcnow()
                else:
                    user = User(
                        user_id=user_id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        token_expiry=token_expiry
                    )
                    session.add(user)
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في حفظ بيانات المصادقة: {e}")
            return False
    
    def update_user_channel(self, user_id: int, channel_id: str, channel_name: str) -> bool:
        """تحديث قناة المستخدم المختارة"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.user_id == user_id).first()
                
                if user:
                    user.selected_channel_id = channel_id
                    user.selected_channel_name = channel_name
                    user.updated_at = datetime.utcnow()
                    session.commit()
                    return True
                
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في تحديث القناة: {e}")
            return False
    
    # ===== عمليات سجل الرفع =====
    
    def log_upload(self, upload_data: Dict) -> bool:
        """تسجيل عملية رفع"""
        try:
            with self.get_session() as session:
                upload_log = UploadLog(**upload_data)
                session.add(upload_log)
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في تسجيل الرفع: {e}")
            return False
    
    def get_user_uploads(self, user_id: int, limit: int = 10) -> List[UploadLog]:
        """جلب سجل رفع المستخدم"""
        try:
            with self.get_session() as session:
                return session.query(UploadLog)\
                    .filter(UploadLog.user_id == user_id)\
                    .order_by(UploadLog.upload_time.desc())\
                    .limit(limit)\
                    .all()
        except SQLAlchemyError as e:
            logger.error(f"خطأ في جلب سجل الرفع: {e}")
            return []
    
    def get_upload_stats(self, user_id: int) -> Dict:
        """إحصائيات الرفع للمستخدم"""
        try:
            with self.get_session() as session:
                total_uploads = session.query(UploadLog)\
                    .filter(UploadLog.user_id == user_id).count()
                
                successful_uploads = session.query(UploadLog)\
                    .filter(UploadLog.user_id == user_id, 
                           UploadLog.upload_status == 'success').count()
                
                failed_uploads = session.query(UploadLog)\
                    .filter(UploadLog.user_id == user_id, 
                           UploadLog.upload_status.like('error%')).count()
                
                return {
                    'total': total_uploads,
                    'successful': successful_uploads,
                    'failed': failed_uploads,
                    'success_rate': (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0
                }
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في جلب الإحصائيات: {e}")
            return {'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0}
    
    # ===== عمليات الإدارة =====
    
    def get_all_users_count(self) -> int:
        """عدد جميع المستخدمين"""
        try:
            with self.get_session() as session:
                return session.query(User).count()
        except SQLAlchemyError as e:
            logger.error(f"خطأ في عد المستخدمين: {e}")
            return 0
    
    def get_active_users_count(self) -> int:
        """عدد المستخدمين النشطين"""
        try:
            with self.get_session() as session:
                return session.query(User).filter(User.is_active == True).count()
        except SQLAlchemyError as e:
            logger.error(f"خطأ في عد المستخدمين النشطين: {e}")
            return 0
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """تنظيف السجلات القديمة"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                deleted_count = session.query(UploadLog)\
                    .filter(UploadLog.upload_time < cutoff_date)\
                    .delete()
                session.commit()
                
                logger.info(f"تم حذف {deleted_count} سجل قديم")
                return deleted_count
                
        except SQLAlchemyError as e:
            logger.error(f"خطأ في تنظيف السجلات: {e}")
            return 0

# إنشاء مثيل مدير قاعدة البيانات
def create_database_manager() -> Optional[DatabaseManager]:
    """إنشاء مدير قاعدة البيانات"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ DATABASE_URL غير موجود في متغيرات البيئة")
        return None
    
    db_manager = DatabaseManager(database_url)
    
    if db_manager.connect():
        return db_manager
    else:
        return None
