#!/usr/bin/env python3
"""
国内版 Email-to-Podcast 服务
使用：IMAP 协议读取邮件 + 百度语音合成 API
完全基于国内服务，无需国外账号
"""

import imaplib
import email
from email.header import decode_header
import requests
import json
import hashlib
import time
import base64
from pathlib import Path

class ChinaEmailToPodcast:
    """国内版 Email-to-Podcast"""
    
    def __init__(self, email_address, email_password, baidu_api_key, baidu_secret_key):
        """
        初始化
        
        Args:
            email_address: 邮箱地址（QQ邮箱/网易邮箱）
            email_password: 邮箱授权码（非密码）
            baidu_api_key: 百度 AI API Key
            baidu_secret_key: 百度 AI Secret Key
        """
        self.email_address = email_address
        self.email_password = email_password
        self.baidu_api_key = baidu_api_key
        self.baidu_secret_key = baidu_secret_key
        self.baidu_access_token = None
        
        # IMAP 服务器配置（国内邮箱）
        self.imap_servers = {
            'qq.com': 'imap.qq.com',
            '163.com': 'imap.163.com',
            '126.com': 'imap.126.com',
            'yeah.net': 'imap.yeah.net',
        }
    
    def get_imap_server(self):
        """获取 IMAP 服务器地址"""
        domain = self.email_address.split('@')[1]
        return self.imap_servers.get(domain, 'imap.qq.com')
    
    def get_baidu_access_token(self):
        """获取百度 AI Access Token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.baidu_api_key,
            "client_secret": self.baidu_secret_key
        }
        
        response = requests.post(url, params=params)
        result = response.json()
        
        if 'access_token' in result:
            self.baidu_access_token = result['access_token']
            return self.baidu_access_token
        else:
            raise Exception(f"获取百度 Access Token 失败: {result}")
    
    def read_emails(self, folder='INBOX', limit=10):
        """
        读取邮件
        
        Args:
            folder: 邮箱文件夹（默认收件箱）
            limit: 读取数量限制
            
        Returns:
            list: 邮件列表 [{'subject': str, 'from': str, 'date': str, 'body': str}]
        """
        imap_server = self.get_imap_server()
        
        try:
            # 连接 IMAP 服务器
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email_address, self.email_password)
            mail.select(folder)
            
            # 搜索邮件
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            emails = []
            # 只读取最新的 N 封邮件
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 解码主题
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8')
                        
                        # 提取正文
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True).decode('utf-8')
                                    except:
                                        body = part.get_payload(decode=True).decode('gbk')
                                    break
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode('utf-8')
                            except:
                                body = msg.get_payload(decode=True).decode('gbk')
                        
                        emails.append({
                            'subject': subject,
                            'from': msg['From'],
                            'date': msg['Date'],
                            'body': body[:5000]  # 限制长度
                        })
            
            mail.close()
            mail.logout()
            
            return emails
            
        except Exception as e:
            raise Exception(f"读取邮件失败: {e}")
    
    def text_to_speech(self, text, output_file, voice=0, speed=5, pitch=5, volume=5):
        """
        文本转语音（百度 TTS）
        
        Args:
            text: 待转换文本
            output_file: 输出 MP3 文件路径
            voice: 发音人（0-度小美，1-度小宇，3-度逍遥，4-度丫丫）
            speed: 语速（0-9）
            pitch: 音调（0-9）
            volume: 音量（0-9）
            
        Returns:
            bool: 是否成功
        """
        if not self.baidu_access_token:
            self.get_baidu_access_token()
        
        url = "https://tsn.baidu.com/text2audio"
        
        params = {
            "tex": text,
            "tok": self.baidu_access_token,
            "cuid": "email-to-podcast",
            "ctp": 1,
            "lan": "zh",
            "spd": speed,
            "pit": pitch,
            "vol": volume,
            "per": voice,
        }
        
        response = requests.post(url, data=params)
        
        # 检查响应
        content_type = response.headers.get('Content-Type', '')
        if 'audio' in content_type:
            # 保存音频文件
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        else:
            # 错误响应
            error = response.json()
            raise Exception(f"百度 TTS 转换失败: {error}")
    
    def newsletter_to_podcast(self, emails, output_dir="podcasts"):
        """
        将邮件转换为 Podcast
        
        Args:
            emails: 邮件列表
            output_dir: 输出目录
            
        Returns:
            list: 生成的音频文件列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        
        for i, email_data in enumerate(emails):
            print(f"正在处理第 {i+1} 封邮件: {email_data['subject']}")
            
            # 准备文本（主题 + 正文）
            text = f"{email_data['subject']}。\n\n{email_data['body']}"
            
            # 生成音频文件
            audio_file = output_path / f"podcast_{i+1}_{int(time.time())}.mp3"
            
            try:
                self.text_to_speech(text, str(audio_file))
                audio_files.append(str(audio_file))
                print(f"✓ 已生成: {audio_file}")
            except Exception as e:
                print(f"✗ 转换失败: {e}")
        
        return audio_files


def main():
    """主函数"""
    print("🇨🇳 国内版 Email-to-Podcast 服务")
    print("=" * 60)
    
    # 配置信息（需要用户填写）
    config = {
        'email_address': 'YOUR_EMAIL@qq.com',  # 替换为你的邮箱
        'email_password': 'YOUR_EMAIL_PASSWORD',  # 替换为邮箱授权码
        'baidu_api_key': 'YOUR_BAIDU_API_KEY',  # 替换为百度 API Key
        'baidu_secret_key': 'YOUR_BAIDU_SECRET_KEY',  # 替换为百度 Secret Key
    }
    
    print("\n使用说明：")
    print("1. 获取 QQ邮箱授权码: https://service.mail.qq.com/detail/0/75")
    print("2. 获取百度 AI API Key: https://console.bce.baidu.com/ai/#/ai/speech/overview/index")
    print("3. 修改 config 字段后重新运行")
    
    # 如果配置未填写，返回
    if 'YOUR_' in config['email_address']:
        print("\n⚠️  请先配置邮箱和百度 API 信息")
        return
    
    try:
        # 初始化服务
        service = ChinaEmailToPodcast(
            email_address=config['email_address'],
            email_password=config['email_password'],
            baidu_api_key=config['baidu_api_key'],
            baidu_secret_key=config['baidu_secret_key']
        )
        
        # 读取最新 5 封邮件
        print("\n正在读取邮件...")
        emails = service.read_emails(limit=5)
        print(f"✓ 读取到 {len(emails)} 封邮件")
        
        # 转换为 Podcast
        print("\n正在转换为 Podcast...")
        audio_files = service.newsletter_to_podcast(emails)
        
        print("\n" + "=" * 60)
        print("✓ Podcast 生成完成！")
        print(f"共生成 {len(audio_files)} 个音频文件")
        for audio_file in audio_files:
            print(f"  - {audio_file}")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
