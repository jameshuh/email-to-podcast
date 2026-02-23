#!/usr/bin/env python3
"""
生成 Gmail OAuth 授权 URL
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# 配置
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_PATH = 'config/gmail_credentials.json'

def main():
    print("🔐 生成 Gmail OAuth 授权链接...\n")
    
    try:
        # 创建 OAuth 流程
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES,
            redirect_uri='http://localhost:8080/')
        
        # 生成授权 URL
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline'
        )
        
        print("📋 请点击以下链接进行授权：\n")
        print(auth_url)
        print("\n")
        print("授权后，将浏览器地址栏的完整 URL 复制给我")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
