#!/usr/bin/env python3
"""测试 Gmail API 读取邮件"""

import pickle
import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import httplib2
import google_auth_httplib2

# 代理配置
PROXY = 'http://127.0.0.1:7897'

def test_gmail_api():
    """测试 Gmail API 读取邮件"""
    # 加载 token
    token_path = 'token.pickle'
    if not os.path.exists(token_path):
        print('❌ Token文件不存在')
        return False

    with open(token_path, 'rb') as token:
        creds = pickle.load(token)

    # 检查 token 是否过期
    if creds.expired:
        print('⚠️  Token已过期,尝试刷新...')
        # 使用代理刷新 token
        http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
            httplib2.socks.PROXY_TYPE_HTTP,
            '127.0.0.1',
            7897
        ))
        creds.refresh(Request(http=http))
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print('✅ Token刷新成功')

    # 创建带代理的 HTTP 对象
    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
        httplib2.socks.PROXY_TYPE_HTTP,
        '127.0.0.1',
        7897
    ))
    
    # 使用 google_auth_httplib2 授权
    authed_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)

    # 创建 Gmail API 服务
    service = build('gmail', 'v1', http=authed_http)

    # 获取最近的邮件
    print('📬 正在获取最近的邮件...')
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print('📭 没有找到邮件')
        return False

    print(f'✅ 找到 {len(messages)} 封最近邮件:\n')
    for i, msg in enumerate(messages, 1):
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '无主题')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '未知发件人')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '未知日期')
        
        print(f'{i}. {subject[:60]}')
        print(f'   来自: {from_addr[:50]}')
        print(f'   日期: {date}')
        print()

    return True

if __name__ == '__main__':
    try:
        test_gmail_api()
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()
