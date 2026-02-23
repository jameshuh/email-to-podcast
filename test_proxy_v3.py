#!/usr/bin/env python3
"""
通过代理测试 Gmail API - 使用 requests
"""

import pickle
import httplib2
from googleapiclient.discovery import build
import socks
import socket

TOKEN_PATH = 'token.pickle'

def main():
    print("📧 测试 Gmail API（通过代理）...\n")
    
    try:
        # 设置全局代理
        socks.set_default_proxy(socks.HTTP, '127.0.0.1', 7897)
        socket.socket = socks.socksocket
        
        # 加载 token
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        
        print("✅ Token 加载成功")
        
        # 创建 Gmail 服务
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
