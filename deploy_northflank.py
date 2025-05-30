"""
سكريبت نشر البوت على Northflank
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class NorthflankDeployer:
    def __init__(self):
        self.api_token = os.getenv('NORTHFLANK_API_TOKEN')
        self.project_id = os.getenv('NORTHFLANK_PROJECT_ID', 'youtube-telegram-bot')
        self.base_url = 'https://api.northflank.com/v1'
        
        if not self.api_token:
            raise ValueError("NORTHFLANK_API_TOKEN مطلوب")
    
    def create_project(self):
        """إنشاء مشروع جديد"""
        url = f"{self.base_url}/projects"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "name": "YouTube Telegram Bot",
            "description": "بوت تلقرام لرفع الفيديوهات إلى YouTube",
            "color": "#FF6B6B"
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            project = response.json()
            print(f"✅ تم إنشاء المشروع: {project['data']['id']}")
            return project['data']['id']
        else:
            print(f"❌ فشل إنشاء المشروع: {response.text}")
            return None
    
    def create_service(self, project_id):
        """إنشاء خدمة البوت"""
        url = f"{self.base_url}/projects/{project_id}/services"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "name": "telegram-bot",
            "description": "خدمة بوت التلقرام",
            "billing": {
                "deploymentPlan": "nf-compute-10"
            },
            "deployment": {
                "instances": 1,
                "docker": {
                    "configType": "dockerfile"
                },
                "internal": {
                    "id": "telegram-bot",
                    "branch": "main",
                    "projectRoot": "/"
                }
            },
            "runtimeEnvironment": {
                "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
                "YOUTUBE_CLIENT_ID": "${YOUTUBE_CLIENT_ID}",
                "YOUTUBE_CLIENT_SECRET": "${YOUTUBE_CLIENT_SECRET}",
                "REDIRECT_URI": "${REDIRECT_URI}"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            service = response.json()
            print(f"✅ تم إنشاء الخدمة: {service['data']['id']}")
            return service['data']['id']
        else:
            print(f"❌ فشل إنشاء الخدمة: {response.text}")
            return None
    
    def deploy(self):
        """نشر البوت"""
        print("🚀 بدء نشر البوت على Northflank...")
        
        # إنشاء المشروع
        project_id = self.create_project()
        if not project_id:
            return False
        
        # إنشاء الخدمة
        service_id = self.create_service(project_id)
        if not service_id:
            return False
        
        print("✅ تم نشر البوت بنجاح!")
        print(f"📊 معرف المشروع: {project_id}")
        print(f"🔧 معرف الخدمة: {service_id}")
        
        return True

def main():
    try:
        deployer = NorthflankDeployer()
        deployer.deploy()
    except Exception as e:
        print(f"❌ خطأ في النشر: {e}")

if __name__ == "__main__":
    main()
