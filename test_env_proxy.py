#!/usr/bin/env python3
"""
通过环境变量设置代理测试 Gmail API
"""

import os
import pickle

# 在导入 Google 库之前设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
os.environ['http_proxy'] = 'http://127.0.0.1:7897'
os.environ['https_proxy'] = 'http://127.0.0.1:7897'

from googleapiclient.discovery import build

TOKEN_PATH = 'token.pickle'

def main():
    print("📧 测试 Gmail API（环境变量代理）...\n")
    
    try:
        # 加载 token
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        
        print("✅ Token 加载成功")
        print(f"   代理: {os.environ.get('HTTPS_PROXY')}")
        
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
        
        print("\n🎉 Gmail API 集成成功！")
        print("✅ Email-to-Podcast Phase 1 完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
