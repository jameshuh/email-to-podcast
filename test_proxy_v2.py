#!/usr/bin/env python3
"""
通过代理测试 Gmail API - 正确配置方式
"""

import pickle
import httplib2
from googleapiclient.discovery import build
from google.auth.transport.httplib2 import Request

TOKEN_PATH = 'token.pickle'

def main():
    print("📧 测试 Gmail API（通过代理）...\n")
    
    try:
        # 加载 token
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        
        print("✅ Token 加载成功")
        
        # 配置带代理的 http
        proxy_http = httplib2.Http(
            proxy_info=httplib2.ProxyInfo(
                httplib2.socks.PROXY_TYPE_HTTP,
                '127.0.0.1',
                7897
            ),
            timeout=30
        )
        
        # 刷新 token（如果需要）
        if creds.expired and creds.refresh_token:
            print("🔄 刷新 token...")
            creds.refresh(Request(proxy_http))
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Token 已刷新")
        
        # 创建认证后的 http 对象
        authed_http = creds.authorize(httplib2.Http(
            proxy_info=httplib2.ProxyInfo(
                httplib2.socks.PROXY_TYPE_HTTP,
                '127.0.0.1',
                7897
            ),
            timeout=30
        ))
        
        # 创建 Gmail 服务（不传 credentials，只用 http）
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
        
        print("\n🎉 Gmail API 集成完全成功！")
        print("✅ 可以读取邮件了")
        print("✅ Email-to-Podcast 项目 Phase 1 技术验证完成！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
