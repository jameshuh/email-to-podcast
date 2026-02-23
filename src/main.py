#!/usr/bin/env python3
"""
Email-to-Podcast 主程序
将 Gmail 未读邮件转换为播客音频
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gmail_reader import GmailReader
from src.text_processor import TextProcessor
from src.audio_generator import AudioGenerator
from src.podcast_creator import PodcastCreator

class EmailToPodcast:
    def __init__(self, config_dir='config', output_dir='output'):
        """
        初始化 Email-to-Podcast 服务
        
        Args:
            config_dir: 配置文件目录
            output_dir: 输出文件目录
        """
        self.config_dir = config_dir
        self.output_dir = output_dir
        
        # 初始化各模块
        credentials_path = os.path.join(config_dir, 'gmail_credentials.json')
        self.gmail_reader = GmailReader(credentials_path)
        
        self.text_processor = TextProcessor(max_length=500)
        
        api_key_path = "~/.config/elevenlabs/api_key.txt"
        self.audio_generator = AudioGenerator(api_key_path)
        
        self.podcast_creator = PodcastCreator()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self, max_emails=5, mark_read=False):
        """
        执行完整的 Email-to-Podcast 流程
        
        Args:
            max_emails: 最大处理邮件数
            mark_read: 是否标记为已读
        
        Returns:
            str: 生成的播客文件路径
        """
        print("🚀 Email-to-Podcast 服务启动")
        print("="*60)
        
        # 步骤1：获取未读邮件
        print("\n📧 步骤1：获取未读邮件...")
        try:
            email_list = self.gmail_reader.get_unread_emails(max_results=max_emails)
            
            if not email_list:
                print("✅ 没有未读邮件，无需生成播客")
                return None
            
            print(f"✅ 找到 {len(email_list)} 封未读邮件")
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {e}")
            raise
        
        # 步骤2：读取邮件内容
        print("\n📝 步骤2：读取邮件内容...")
        emails = []
        for i, email_meta in enumerate(email_list, 1):
            print(f"  📖 读取第 {i}/{len(email_list)} 封邮件...")
            email_data = self.gmail_reader.get_email_content(email_meta['id'])
            emails.append(email_data)
        
        print(f"✅ 成功读取 {len(emails)} 封邮件")
        
        # 步骤3：生成播客脚本
        print("\n🎙️ 步骤3：生成播客脚本...")
        script = self.text_processor.create_full_script(emails)
        
        # 保存脚本（可选）
        script_path = os.path.join(self.output_dir, 'script.txt')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"✅ 脚本已保存: {script_path}")
        print(f"   脚本长度: {len(script)} 字符")
        
        # 步骤4：将脚本分段转为音频
        print("\n🎵 步骤4：生成音频...")
        
        # 将脚本按段落分割（每段独立生成音频，便于错误处理）
        script_parts = script.split('\n\n--- 第')
        script_parts = [script_parts[0]] + ['--- 第' + part for part in script_parts[1:]]
        
        temp_audio_dir = os.path.join(self.output_dir, 'temp_audio')
        audio_files = self.audio_generator.text_to_speech_batch(
            script_parts,
            temp_audio_dir,
            prefix='part'
        )
        
        print(f"✅ 生成了 {len(audio_files)} 个音频片段")
        
        # 步骤5：合并音频为播客
        print("\n🎧 步骤5：创建播客...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        podcast_filename = f"podcast_{timestamp}.mp3"
        podcast_path = os.path.join(self.output_dir, podcast_filename)
        
        self.podcast_creator.merge_audio_files(audio_files, podcast_path)
        
        print(f"✅ 播客已生成: {podcast_path}")
        
        # 步骤6：标记邮件为已读（可选）
        if mark_read:
            print("\n✉️ 步骤6：标记邮件为已读...")
            for email_meta in email_list:
                self.gmail_reader.mark_as_read(email_meta['id'])
            print(f"✅ 已标记 {len(email_list)} 封邮件为已读")
        
        # 清理临时文件
        print("\n🧹 清理临时文件...")
        for audio_file in audio_files:
            os.remove(audio_file)
        os.rmdir(temp_audio_dir)
        
        print("\n" + "="*60)
        print("✨ Email-to-Podcast 完成！")
        print(f"🎧 播客文件: {podcast_path}")
        
        # 显示播客信息
        duration = self.podcast_creator.get_audio_duration(podcast_path)
        file_size = os.path.getsize(podcast_path) / 1024 / 1024
        print(f"⏱️  时长: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
        print(f"📦 大小: {file_size:.2f} MB")
        
        return podcast_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email-to-Podcast: 将邮件转为播客')
    parser.add_argument('--max-emails', type=int, default=5, help='最大处理邮件数（默认5）')
    parser.add_argument('--mark-read', action='store_true', help='处理后标记邮件为已读')
    parser.add_argument('--output-dir', default='output', help='输出目录（默认output）')
    
    args = parser.parse_args()
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # 创建服务实例
    service = EmailToPodcast(output_dir=args.output_dir)
    
    # 运行
    try:
        podcast_path = service.run(
            max_emails=args.max_emails,
            mark_read=args.mark_read
        )
        
        if podcast_path:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
