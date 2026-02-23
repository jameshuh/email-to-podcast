"""
Email-to-Podcast 服务 - 国内版
完全基于国内服务，无需翻墙
"""

import imaplib
import email
from email.header import decode_header
import requests
import os
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment


class EmailReader:
    """邮件读取器（支持QQ邮箱、网易邮箱等）"""
    
    def __init__(self, email_address, email_password, imap_server='imap.qq.com'):
        self.email_address = email_address
        self.email_password = email_password  # QQ邮箱使用授权码
        self.imap_server = imap_server
        self.mail = None
        
    def connect(self):
        """连接到邮箱服务器"""
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(self.email_address, self.email_password)
        self.mail.select('inbox')
        
    def fetch_unread(self, limit=10):
        """获取未读邮件"""
        _, message_ids = self.mail.search(None, 'UNSEEN')
        email_ids = message_ids[0].split()
        
        emails = []
        for email_id in email_ids[:limit]:
            _, msg_data = self.mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # 解析邮件
            subject = self._decode_header(email_message['Subject'])
            sender = email_message['From']
            body = self._get_body(email_message)
            
            emails.append({
                'id': email_id.decode(),
                'subject': subject,
                'sender': sender,
                'body': body
            })
            
        return emails
    
    def fetch_from_sender(self, sender_filter, limit=10):
        """获取特定发件人的邮件"""
        _, message_ids = self.mail.search(None, f'FROM "{sender_filter}" UNSEEN')
        email_ids = message_ids[0].split()
        
        emails = []
        for email_id in email_ids[:limit]:
            _, msg_data = self.mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            subject = self._decode_header(email_message['Subject'])
            sender = email_message['From']
            body = self._get_body(email_message)
            
            emails.append({
                'id': email_id.decode(),
                'subject': subject,
                'sender': sender,
                'body': body
            })
            
        return emails
    
    def _decode_header(self, header):
        """解码邮件标题"""
        if header is None:
            return ''
        decoded = decode_header(header)
        return ''.join([
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded
        ])
    
    def _get_body(self, email_message):
        """提取邮件正文"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return ''
    
    def disconnect(self):
        """断开连接"""
        if self.mail:
            self.mail.close()
            self.mail.logout()


class BaiduTTS:
    """百度语音合成"""
    
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        
    def get_access_token(self):
        """获取百度 AI 的 access token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        response = requests.post(url, params=params)
        self.access_token = response.json()["access_token"]
        return self.access_token
    
    def synthesize(self, text, output_file, voice=0, speed=5, pitch=5, volume=5):
        """
        将文本转换为语音
        
        参数:
        - text: 要转换的文本
        - output_file: 输出文件路径
        - voice: 发音人选择（0:女声, 1:男声, 3:情感合成-度逍遥, 4:情感合成-度丫丫）
        - speed: 语速（0-15，默认5）
        - pitch: 音调（0-15，默认5）
        - volume: 音量（0-15，默认5）
        """
        if not self.access_token:
            self.get_access_token()
            
        url = f"https://tsn.baidu.com/text2audio?tok={self.access_token}"
        
        data = {
            "tex": text,
            "tok": self.access_token,
            "cuid": "email-to-podcast",
            "ctp": 1,
            "lan": "zh",
            "spd": speed,
            "pit": pitch,
            "vol": volume,
            "per": voice,
            "aue": 3  # MP3格式
        }
        
        response = requests.post(url, data=data)
        
        if response.headers.get('Content-Type') == 'audio/mp3':
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"转换失败: {response.text}")
            return False


class AudioProcessor:
    """音频处理器"""
    
    @staticmethod
    def merge_audio_files(file_list, output_file):
        """合并多个音频文件"""
        combined = AudioSegment.empty()
        
        for file in file_list:
            audio = AudioSegment.from_mp3(file)
            combined += audio
            # 添加1秒静音作为间隔
            combined += AudioSegment.silent(duration=1000)
        
        combined.export(output_file, format='mp3')
        return output_file
    
    @staticmethod
    def add_intro_outro(main_audio, intro_file, outro_file, output_file):
        """添加片头片尾"""
        intro = AudioSegment.from_mp3(intro_file)
        main = AudioSegment.from_mp3(main_audio)
        outro = AudioSegment.from_mp3(outro_file)
        
        combined = intro + main + outro
        combined.export(output_file, format='mp3')
        return output_file


class EmailToPodcast:
    """邮件转播客服务"""
    
    def __init__(self, email_config, baidu_config):
        self.email_reader = EmailReader(
            email_config['address'],
            email_config['password'],
            email_config.get('imap_server', 'imap.qq.com')
        )
        
        self.tts = BaiduTTS(
            baidu_config['api_key'],
            baidu_config['secret_key']
        )
        
    def generate_podcast(self, output_dir='./podcasts', email_limit=5, 
                        intro_text=None, outro_text=None):
        """生成播客"""
        # 创建输出目录
        Path(output_dir).mkdir(exist_ok=True)
        
        # 1. 读取邮件
        print("📧 正在读取邮件...")
        self.email_reader.connect()
        emails = self.email_reader.fetch_unread(limit=email_limit)
        self.email_reader.disconnect()
        
        if not emails:
            print("❌ 没有未读邮件")
            return None
        
        print(f"✅ 找到 {len(emails)} 封未读邮件")
        
        # 2. 转换每封邮件为音频
        audio_files = []
        for i, email_data in enumerate(emails):
            print(f"🎵 处理邮件 {i+1}/{len(emails)}: {email_data['subject'][:30]}...")
            
            # 准备文本内容
            text = f"""
            来自 {email_data['sender']} 的邮件。
            标题：{email_data['subject']}
            正文内容：
            {email_data['body'][:2000]}
            """
            
            # 转换为音频
            audio_file = f"{output_dir}/email_{i+1}.mp3"
            if self.tts.synthesize(text, audio_file):
                audio_files.append(audio_file)
        
        # 3. 合并所有音频
        if audio_files:
            print("🎧 正在合并音频...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_podcast = f"{output_dir}/podcast_{timestamp}.mp3"
            AudioProcessor.merge_audio_files(audio_files, final_podcast)
            
            # 4. 添加片头片尾（如果提供）
            if intro_text and outro_text:
                intro_file = f"{output_dir}/intro.mp3"
                outro_file = f"{output_dir}/outro.mp3"
                
                self.tts.synthesize(intro_text, intro_file)
                self.tts.synthesize(outro_text, outro_file)
                
                final_with_branding = f"{output_dir}/podcast_{timestamp}_final.mp3"
                AudioProcessor.add_intro_outro(final_podcast, intro_file, outro_file, final_with_branding)
                
                # 删除临时文件
                os.remove(intro_file)
                os.remove(outro_file)
                os.remove(final_podcast)
                os.rename(final_with_branding, final_podcast)
            
            # 5. 清理临时文件
            for file in audio_files:
                os.remove(file)
            
            print(f"✅ 播客生成完成: {final_podcast}")
            print(f"📊 时长: {len(AudioSegment.from_mp3(final_podcast)) / 1000:.1f} 秒")
            return final_podcast
        
        return None


# 配置示例（从环境变量或配置文件读取）
def load_config():
    """加载配置"""
    return {
        'email': {
            'address': os.getenv('EMAIL_ADDRESS', '3305363@qq.com'),
            'password': os.getenv('EMAIL_PASSWORD', 'wowffdbhmmrzbjfb'),  # QQ邮箱授权码
            'imap_server': 'imap.qq.com'
        },
        'baidu': {
            'api_key': os.getenv('BAIDU_API_KEY', 'dECKo31rLB1AWOKzMI8bpiSi'),
            'secret_key': os.getenv('BAIDU_SECRET_KEY', 'cIW7sFvwSFPKAKdjKvn7ZjcjpV2rYuW1')
        }
    }


if __name__ == '__main__':
    # 加载配置
    config = load_config()
    
    # 生成播客
    converter = EmailToPodcast(config['email'], config['baidu'])
    
    # 可选：添加自定义片头片尾
    intro = "欢迎收听今日邮件摘要播客，由AI助手为您播报。"
    outro = "以上就是今日邮件摘要，感谢收听。"
    
    podcast = converter.generate_podcast(
        email_limit=5,
        intro_text=intro,
        outro_text=outro
    )
    
    if podcast:
        print(f"\n🎉 成功！播客已保存到: {podcast}")
    else:
        print("\n❌ 生成失败")
