#!/bin/bash

# سكريبت نشر البوت على Northflank

echo "🚀 بدء نشر بوت YouTube Telegram على Northflank..."

# التحقق من وجود المتطلبات
if [ ! -f ".env" ]; then
    echo "❌ ملف .env غير موجود"
    echo "📝 أنشئ ملف .env وأضف المتغيرات المطلوبة"
    exit 1
fi

# تحميل متغيرات البيئة
source .env

# التحقق من المتغيرات المطلوبة
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN غير موجود في .env"
    exit 1
fi

if [ -z "$YOUTUBE_CLIENT_ID" ]; then
    echo "❌ YOUTUBE_CLIENT_ID غير موجود في .env"
    exit 1
fi

if [ -z "$YOUTUBE_CLIENT_SECRET" ]; then
    echo "❌ YOUTUBE_CLIENT_SECRET غير موجود في .env"
    exit 1
fi

echo "✅ جميع المتغيرات موجودة"

# بناء الصورة محلياً للاختبار
echo "🔨 بناء صورة Docker..."
docker build -t youtube-telegram-bot .

if [ $? -eq 0 ]; then
    echo "✅ تم بناء الصورة بنجاح"
else
    echo "❌ فشل في بناء الصورة"
    exit 1
fi

# اختبار الصورة
echo "🧪 اختبار الصورة..."
docker run --rm --env-file .env youtube-telegram-bot python healthcheck.py

if [ $? -eq 0 ]; then
    echo "✅ الصورة تعمل بشكل صحيح"
else
    echo "❌ الصورة لا تعمل بشكل صحيح"
    exit 1
fi

echo "🎉 البوت جاهز للنشر على Northflank!"
echo ""
echo "📋 الخطوات التالية:"
echo "1. ادفع الكود إلى GitHub"
echo "2. اربط المستودع مع Northflank"
echo "3. أضف متغيرات البيئة في Northflank"
echo "4. انشر الخدمة"
