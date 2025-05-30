#!/bin/bash

# سكريبت إعداد ملف البيئة

echo "🔧 إعداد ملف البيئة للبوت..."

# التحقق من وجود ملف .env
if [ -f ".env" ]; then
    echo "⚠️ ملف .env موجود بالفعل"
    read -p "هل تريد استبداله؟ (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ تم إلغاء العملية"
        exit 1
    fi
fi

# نسخ ملف المثال
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ تم إنشاء ملف .env من .env.example"
else
    echo "❌ ملف .env.example غير موجود"
    exit 1
fi

echo ""
echo "📝 الآن تحتاج إلى تعديل ملف .env وإضافة البيانات التالية:"
echo ""
echo "1️⃣ TELEGRAM_BOT_TOKEN:"
echo "   - اذهب إلى @BotFather في تلقرام"
echo "   - أرسل /newbot واتبع التعليمات"
echo "   - انسخ التوكن وضعه في .env"
echo ""
echo "2️⃣ YOUTUBE_CLIENT_ID و YOUTUBE_CLIENT_SECRET:"
echo "   - اذهب إلى https://console.cloud.google.com"
echo "   - أنشئ مشروع جديد"
echo "   - فعّل YouTube Data API v3"
echo "   - أنشئ OAuth 2.0 credentials"
echo "   - انسخ Client ID و Client Secret"
echo ""
echo "3️⃣ REDIRECT_URI:"
echo "   - للتطوير المحلي: http://localhost:8080/callback"
echo "   - للإنتاج: https://your-domain.com/auth/callback"
echo ""
echo "🔒 تذكر: لا تشارك ملف .env مع أحد!"
echo "📁 ملف .env محمي بواسطة .gitignore"
