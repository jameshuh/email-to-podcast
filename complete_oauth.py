#!/usr/bin/env python3
"""
完成 Gmail OAuth 认证流程
使用授权码获取 access token
"""

import sys
import os
import pickle
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 配置
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_PATH = 'config/gmail_credentials.json'
TOKEN_PATH = 'token.pickle'

# 用户提供的完整 URL
REDIRECT_URL = "http://localhost:8080/?state=oFwi6gDu6dtjP3WIXfw7uPXpFSWR0f&code=4/0AfrIepCTDIOaSwtJjeR_IGAxPe8qtQri8sM6yWBKl-RF6SIttLJnVKgpfrh_4xNhmoznuA&scope=https://www.googleapis.com/auth/gmail.readonly"

def main():
    print("🔐 正在完成 Gmail OAuth 认证...")
    
    try:
        # 从 URL 中提取授权码
        print("   从 URL 提取授权码...")
        parsed = urlparse(REDIRECT_URL)
        params = parse_qs(parsed.query)
        
        auth_code = params.get('code', [None])[0]
        if not auth_code:
            raise ValueError("URL 中没有找到授权码")
        
        print(f"   授权码: {auth_code[:20]}...")
        
        # 创建 OAuth 流程
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES,
            redirect_uri='http://localhost:8080/')
        
        # 使用授权码获取 token
        print("   使用授权码换取 access token...")
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # 保存 token
        print("   保存 token 到文件...")
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"\n✅ 认证成功！Token 已保存到 {TOKEN_PATH}")
        
        # 测试 Gmail API
        print("\n📧 测试 Gmail API...")
        from googleapiclient.discovery import build
        
        service = build('gmail', 'v1', credentials=creds)
        
        # 获取用户标签列表（简单测试）
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        print(f"✅ Gmail API 可用！找到 {len(labels)} 个标签")
        
        # 获取未读邮件
        print("\n📬 获取未读邮件...")
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=5
        ).execute()
        
        messages = results.get('messages', [])
        print(f"✅ 找到 {len(messages)} 封未读邮件")
        
        if messages:
            # 读取第一封邮件
            msg = service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()
            
            subject = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject'), '无主题')
            from_addr = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'From'), '未知')
            
            print(f"\n📧 第一封未读邮件：")
            print(f"   主题: {subject}")
            print(f"   发件人: {from_addr}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 认证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
