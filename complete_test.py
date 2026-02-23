#!/usr/bin/env python3
"""
立即使用新授权码换取 token 并测试
"""

import sys
import pickle
import socks
import socket
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 配置
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_PATH = 'config/gmail_credentials.json'
TOKEN_PATH = 'token.pickle'

# 用户提供的 URL
AUTH_URL = "http://localhost:8080/?state=R5J8Ikmm6RRyaYznpvTigfAwtzQFkC&code=4/0AfrIepCG9tTIcfg_fUZj7V5Bar1yu8eaOzFUYTGK2RNoSTJw1WsYtk5z8vGuew7s_DxyhA&scope=https://www.googleapis.com/auth/gmail.readonly"

def main():
    print("🔐 正在完成 Gmail OAuth 认证...\n")
    
    try:
        # 设置全局代理
        socks.set_default_proxy(socks.HTTP, '127.0.0.1', 7897)
        socket.socket = socks.socksocket
        
        # 从 URL 中提取授权码
        parsed = urlparse(AUTH_URL)
        params = parse_qs(parsed.query)
        
        auth_code = params.get('code', [None])[0]
        if not auth_code:
            raise ValueError("URL 中没有找到授权码")
        
        print(f"✅ 授权码: {auth_code[:30]}...")
        
        # 创建 OAuth 流程
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES,
            redirect_uri='http://localhost:8080/')
        
        # 使用授权码获取 token
        print("🔄 正在换取 access token...")
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # 保存 token
        print("💾 保存 token...")
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"\n✅ 认证成功！Token 已保存\n")
        
        # 立即测试 Gmail API
        print("📧 测试 Gmail API 连接...")
        service = build('gmail', 'v1', credentials=creds)
        
        # 测试：获取标签
        print("\n🔍 测试 1: 获取标签列表...")
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print(f"✅ 成功！找到 {len(labels)} 个标签")
        
        # 测试：获取最近邮件
        print("\n🔍 测试 2: 获取最近邮件...")
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=5
        ).execute()
        messages = results.get('messages', [])
        print(f"✅ 成功！找到 {len(messages)} 封邮件")
        
        if messages:
            print("\n📋 最近邮件：")
            for i, msg_info in enumerate(messages[:3], 1):
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_info['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From']
                ).execute()
                
                subject = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject'), '无主题')
                from_addr = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'From'), '未知')
                
                print(f"\n{i}. {subject[:60]}")
                print(f"   发件人: {from_addr[:50]}")
        
        print("\n🎉 Gmail API 集成完全成功！")
        print("✅ Email-to-Podcast 项目 Phase 1 完成！")
        print("✅ 下一步：注册 ElevenLabs 获取 TTS API Key")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
