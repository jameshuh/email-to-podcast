#!/usr/bin/env python3
"""
Gmail 邮件读取模块（改进版）
自动启动本地服务器接收 OAuth 回调
"""

import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Gmail API 权限范围
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailReader:
    def __init__(self, credentials_path, token_path='token.pickle'):
        """
        初始化 Gmail 阅读器
        
        Args:
            credentials_path: OAuth 凭据文件路径
            token_path: Token 缓存文件路径
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
    def authenticate(self):
        """认证并获取 Gmail API 服务"""
        creds = None
        
        # 尝试从缓存加载 token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果没有有效凭据，进行 OAuth 流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # 使用本地服务器自动接收回调
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(
                    port=8080,
                    open_browser=False,
                    authorization_prompt_message='\n🔐 请访问以下链接授权：\n\n{url}\n\n⏳ 等待授权中...\n'
                )
            
            # 保存 token 供下次使用
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def get_unread_emails(self, max_results=10, label_ids=None):
        """
        获取未读邮件列表
        
        Args:
            max_results: 最大返回数量
            label_ids: 标签过滤（如 ['INBOX', 'UNREAD']）
        
        Returns:
            邮件 ID 列表
        """
        if not self.service:
            self.authenticate()
        
        if label_ids is None:
            label_ids = ['INBOX', 'UNREAD']
        
        results = self.service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    
    def get_email_content(self, msg_id):
        """
        获取单封邮件的详细内容
        
        Args:
            msg_id: 邮件 ID
        
        Returns:
            dict: {
                'id': 邮件ID,
                'subject': 主题,
                'from': 发件人,
                'date': 日期,
                'body': 正文内容
            }
        """
        if not self.service:
            self.authenticate()
        
        message = self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        # 提取头部信息
        headers = message['payload'].get('headers', [])
        email_data = {
            'id': msg_id,
            'subject': '',
            'from': '',
            'date': '',
            'body': ''
        }
        
        for header in headers:
            if header['name'] == 'Subject':
                email_data['subject'] = header['value']
            elif header['name'] == 'From':
                email_data['from'] = header['value']
            elif header['name'] == 'Date':
                email_data['date'] = header['value']
        
        # 提取正文
        email_data['body'] = self._extract_body(message['payload'])
        
        return email_data
    
    def _extract_body(self, payload):
        """
        从邮件 payload 提取正文内容
        
        Args:
            payload: Gmail API 返回的 payload
        
        Returns:
            str: 纯文本正文
        """
        body = ''
        
        if 'parts' in payload:
            # 多部分邮件，查找 text/plain
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    # 如果没有纯文本，从 HTML 提取
                    data = part['body'].get('data', '')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html, 'html.parser')
                        body = soup.get_text(separator=' ', strip=True)
        else:
            # 单部分邮件
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # 清理文本
        body = ' '.join(body.split())  # 移除多余空白
        return body
    
    def mark_as_read(self, msg_id):
        """标记邮件为已读"""
        if not self.service:
            self.authenticate()
        
        self.service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()


if __name__ == '__main__':
    # 测试代码
    import sys
    
    credentials_path = '../config/gmail_credentials.json'
    
    reader = GmailReader(credentials_path)
    
    print("🔐 正在认证 Gmail API...")
    print("\n⚠️ 请按照以下步骤操作：")
    print("1. 程序会显示一个授权链接")
    print("2. 点击链接并授权")
    print("3. 授权后浏览器会自动跳转到 localhost:8080")
    print("4. 程序会自动接收授权码并完成认证\n")
    
    reader.authenticate()
    print("✅ 认证成功！")
    
    print("\n📧 获取未读邮件...")
    emails = reader.get_unread_emails(max_results=5)
    
    if not emails:
        print("没有未读邮件")
    else:
        print(f"找到 {len(emails)} 封未读邮件：")
        for i, email in enumerate(emails[:3], 1):
            content = reader.get_email_content(email['id'])
            print(f"\n{i}. {content['subject']}")
            print(f"   发件人: {content['from']}")
            print(f"   日期: {content['date']}")
            print(f"   正文预览: {content['body'][:100]}...")
