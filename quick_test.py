#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build

# 加载 token
with open('token.pickle', 'rb') as f:
    creds = pickle.load(f)

# 创建 Gmail API 服务
service = build('gmail', 'v1', credentials=creds)

# 获取未读邮件（只获取1封）
results = service.users().messages().list(
    userId='me',
    labelIds=['INBOX', 'UNREAD'],
    maxResults=1
).execute()

messages = results.get('messages', [])

if messages:
    # 读取邮件
    msg = service.users().messages().get(
        userId='me',
        id=messages[0]['id'],
        format='metadata',
        metadataHeaders=['Subject', 'From']
    ).execute()
    
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '无主题')
    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '未知')
    
    print(f'✅ Gmail API 可用！')
    print(f'找到未读邮件：{subject}')
    print(f'发件人：{from_addr}')
else:
    print('✅ Gmail API 可用！')
    print('没有未读邮件')
