#!/usr/bin/env python3
"""
全自动播客生成脚本
每天自动执行：读取邮件 → 生成播客 → 更新 RSS feed
适合用 cron 或 launchd 定时执行
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import EmailToPodcast, load_config
from rss_generator import RSSGenerator


class AutoPodcast:
    """全自动播客生成器"""
    
    def __init__(self, config, rss_config):
        """
        初始化
        
        参数:
        - config: 邮件和百度 API 配置
        - rss_config: RSS feed 配置
        """
        self.config = config
        self.rss_config = rss_config
        self.output_dir = Path(config.get('output_dir', './podcasts'))
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_daily_podcast(self, email_limit=5, intro=None, outro=None):
        """
        生成每日播客
        
        参数:
        - email_limit: 读取邮件数量
        - intro: 片头文本
        - outro: 片尾文本
        
        返回:
        - 生成的播客文件路径，失败返回 None
        """
        print(f"\n{'='*60}")
        print(f"🎧 开始生成每日播客 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 1. 生成播客
        converter = EmailToPodcast(self.config['email'], self.config['baidu'])
        
        podcast_file = converter.generate_podcast(
            output_dir=str(self.output_dir),
            email_limit=email_limit,
            intro_text=intro or self.config.get('intro_text'),
            outro_text=outro or self.config.get('outro_text')
        )
        
        if not podcast_file:
            print("❌ 播客生成失败")
            return None
        
        print(f"✅ 播客生成成功: {podcast_file}")
        
        # 2. 更新 RSS feed
        self._update_rss(podcast_file)
        
        return podcast_file
    
    def _update_rss(self, podcast_file):
        """更新 RSS feed"""
        print("\n📡 更新 RSS feed...")
        
        # 创建 RSS 生成器
        rss = RSSGenerator(
            title=self.rss_config['title'],
            description=self.rss_config['description'],
            author=self.rss_config['author'],
            email=self.rss_config['email'],
            base_url=self.rss_config['base_url']
        )
        
        # 添加历史播客（扫描输出目录）
        podcast_files = sorted(self.output_dir.glob('podcast_*.mp3'), reverse=True)
        
        for i, pf in enumerate(podcast_files[:30]):  # 最多保留30集
            # 从文件名提取日期
            filename = pf.stem  # podcast_20260224_030456
            parts = filename.split('_')
            if len(parts) >= 3:
                date_str = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:8]}"
                time_str = f"{parts[2][:2]}:{parts[2][2:4]}" if len(parts) > 2 else "00:00"
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
                time_str = datetime.now().strftime('%H:%M')
            
            # 获取文件修改时间作为发布日期
            pub_date = datetime.fromtimestamp(pf.stat().st_mtime)
            
            rss.add_episode(
                audio_file=str(pf),
                title=f"{date_str} 邮件摘要",
                description=f"{date_str} {time_str} 生成的邮件摘要播客",
                pub_date=pub_date
            )
        
        # 生成 RSS 文件
        rss_file = self.output_dir / 'podcast.xml'
        rss.generate_rss(str(rss_file))
        
        print(f"✅ RSS feed 更新完成: {rss_file}")
        print(f"📍 Feed URL: {self.rss_config['base_url']}/podcast.xml")
    
    def test_connection(self):
        """测试连接（不生成播客，只测试配置是否正确）"""
        print("\n🔍 测试配置...")
        
        # 测试邮箱连接
        try:
            from service import EmailReader
            reader = EmailReader(
                self.config['email']['address'],
                self.config['email']['password'],
                self.config['email'].get('imap_server', 'imap.qq.com')
            )
            reader.connect()
            print("✅ 邮箱连接成功")
            reader.disconnect()
        except Exception as e:
            print(f"❌ 邮箱连接失败: {e}")
            return False
        
        # 测试百度 API
        try:
            from service import BaiduTTS
            tts = BaiduTTS(
                self.config['baidu']['api_key'],
                self.config['baidu']['secret_key']
            )
            tts.get_access_token()
            print("✅ 百度 API 连接成功")
        except Exception as e:
            print(f"❌ 百度 API 连接失败: {e}")
            return False
        
        print("\n🎉 所有配置正确！可以开始生成播客。")
        return True


def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # RSS 配置（请根据实际情况修改）
    rss_config = {
        'title': '每日邮件摘要播客',
        'description': '将您的邮件自动转换为播客，随时随地收听重要信息',
        'author': 'AI 助手',
        'email': config['email']['address'],
        'base_url': os.getenv('RSS_BASE_URL', 'https://your-domain.com/podcasts')
    }
    
    # 创建自动播客生成器
    auto = AutoPodcast(config, rss_config)
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        auto.test_connection()
        return
    
    # 生成播客
    podcast = auto.generate_daily_podcast(
        email_limit=5,
        intro="欢迎收听今日邮件摘要播客，由 AI 助手为您播报。",
        outro="以上就是今日邮件摘要，感谢收听。明天见！"
    )
    
    if podcast:
        print(f"\n🎉 每日播客生成完成！")
        print(f"📁 文件: {podcast}")
        print(f"📡 RSS: {rss_config['base_url']}/podcast.xml")
    else:
        print(f"\n❌ 生成失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
