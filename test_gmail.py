#!/usr/bin/env python3
"""
测试 Gmail API 并获取未读邮件
"""

import pickle
import os
from googleapiclient.discovery import build

# 加载 token
TOKEN_PATH = 'token.pickle'

print("🔐 加载 Gmail API 凭据...")
with open(TOKEN_PATH, 'rb') as token:
    creds = pickle.load(token)

print(f"✅ Token 加载成功")
print(f"   过期时间: {creds.expiry}")
print(f"   有效: {creds.valid}")

# 创建 Gmail API 服务
print("\n📧 连接 Gmail API...")
service = build('gmail', 'v1', credentials=creds)

# 获取标签列表
print("\n📊 获取标签列表...")
results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])
print(f"✅ 找到 {len(labels)} 个标签")

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
    # 读取前3封邮件
    print("\n📧 邮件详情：")
    for i, msg_meta in enumerate(messages[:3], 1):
        msg = service.users().messages().get(
            userId='me',
            id=msg_meta['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '无主题')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '未知')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '未知')
        
        print(f"\n{i}. {subject}")
        print(f"   发件人: {from_addr}")
        print(f"   日期: {date}")

print("\n✅ Gmail API 测试成功！")
