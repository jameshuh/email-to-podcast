#!/usr/bin/env python3
"""
使用 requests 库通过代理测试 Gmail API
"""

import pickle
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_PATH = 'token.pickle'
PROXY = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

def main():
    print("📧 测试 Gmail API（通过 requests + 代理）...\n")
    
    try:
        # 加载 token
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        
        print("✅ Token 加载成功")
        
        # 创建带代理的 session
        session = requests.Session()
        session.proxies = PROXY
        
        # 创建授权的 session
        authed_session = Request(session)
        
        # 如果 token 过期，刷新
        if creds.expired and creds.refresh_token:
            print("🔄 刷新 token...")
            creds.refresh(authed_session)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Token 已刷新")
        
        # 使用 requests 构建服务
        from googleapiclient.http import build_http
        import google.auth.transport.requests
        
        # 创建自定义 HTTP 对象
        class AuthorizedHttp:
            def __init__(self, creds, session):
                self.creds = creds
                self.session = session
            
            def request(self, uri, method='GET', body=None, headers=None, **kwargs):
                # 添加授权头
                auth_headers = dict(headers) if headers else {}
                self.creds.apply(auth_headers)
                
                # 发送请求
                response = self.session.request(
                    method=method,
                    url=uri,
                    data=body,
                    headers=auth_headers,
                    timeout=30
                )
                
                return response, response.content
        
        authed_http = AuthorizedHttp(creds, session)
        
        # 构建服务
        service = build('gmail', 'v1', http=authed_http)
        
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
        
        print("\n🎉 Gmail API 集成成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
