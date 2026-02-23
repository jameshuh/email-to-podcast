"""
RSS Feed 生成器
生成符合 Podcast 标准的 RSS feed，支持在 Apple Podcasts、Spotify、小宇宙等平台订阅
"""

from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os


class RSSGenerator:
    """播客 RSS Feed 生成器"""
    
    def __init__(self, title, description, author, email, base_url):
        """
        初始化 RSS 生成器
        
        参数:
        - title: 播客标题
        - description: 播客描述
        - author: 作者名称
        - email: 联系邮箱
        - base_url: 播客文件的基础 URL（如 https://example.com/podcasts/）
        """
        self.title = title
        self.description = description
        self.author = author
        self.email = email
        self.base_url = base_url.rstrip('/')
        self.episodes = []
        
    def add_episode(self, audio_file, title, description, pub_date=None, duration=None):
        """
        添加一集播客
        
        参数:
        - audio_file: 音频文件路径
        - title: 本集标题
        - description: 本集描述
        - pub_date: 发布日期（默认为当前时间）
        - duration: 时长（秒）
        """
        if pub_date is None:
            pub_date = datetime.now()
            
        if duration is None:
            # 尝试从文件获取时长
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(audio_file)
                duration = len(audio) / 1000  # 转换为秒
            except:
                duration = 0
        
        # 获取文件大小
        file_size = os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
        
        episode = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'audio_file': os.path.basename(audio_file),
            'duration': duration,
            'file_size': file_size,
            'url': f"{self.base_url}/{os.path.basename(audio_file)}"
        }
        
        self.episodes.append(episode)
        return episode
    
    def generate_rss(self, output_file='podcast.xml'):
        """
        生成 RSS feed XML 文件
        
        返回:
        - RSS XML 内容
        """
        # 创建 RSS 根元素
        rss = ET.Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        
        # 创建 channel
        channel = ET.SubElement(rss, 'channel')
        
        # 添加 channel 基本信息
        ET.SubElement(channel, 'title').text = self.title
        ET.SubElement(channel, 'description').text = self.description
        ET.SubElement(channel, 'link').text = self.base_url
        ET.SubElement(channel, 'language').text = 'zh-CN'
        ET.SubElement(channel, 'copyright').text = f'© {datetime.now().year} {self.author}'
        
        # iTunes 特定标签
        ET.SubElement(channel, 'itunes:author').text = self.author
        ET.SubElement(channel, 'itunes:summary').text = self.description
        ET.SubElement(channel, 'itunes:owner')
        
        owner = channel.find('itunes:owner')
        ET.SubElement(owner, 'itunes:name').text = self.author
        ET.SubElement(owner, 'itunes:email').text = self.email
        
        # iTunes 分类（新闻）
        category = ET.SubElement(channel, 'itunes:category')
        category.set('text', 'News')
        
        # 显式内容标记
        ET.SubElement(channel, 'itunes:explicit').text = 'false'
        
        # 添加每一集
        for episode in sorted(self.episodes, key=lambda x: x['pub_date'], reverse=True):
            item = ET.SubElement(channel, 'item')
            
            ET.SubElement(item, 'title').text = episode['title']
            ET.SubElement(item, 'description').text = episode['description']
            ET.SubElement(item, 'pubDate').text = episode['pub_date'].strftime(
                '%a, %d %b %Y %H:%M:%S +0800'
            )
            ET.SubElement(item, 'link').text = episode['url']
            
            # iTunes 特定标签
            ET.SubElement(item, 'itunes:title').text = episode['title']
            ET.SubElement(item, 'itunes:summary').text = episode['description']
            ET.SubElement(item, 'itunes:duration').text = str(int(episode['duration']))
            ET.SubElement(item, 'itunes:explicit').text = 'false'
            
            # 音频 enclosure
            enclosure = ET.SubElement(item, 'enclosure')
            enclosure.set('url', episode['url'])
            enclosure.set('length', str(episode['file_size']))
            enclosure.set('type', 'audio/mpeg')
        
        # 格式化 XML
        rough_string = ET.tostring(rss, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent='  ')
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return pretty_xml
    
    def get_feed_url(self):
        """获取 RSS feed URL"""
        return f"{self.base_url}/podcast.xml"


# 使用示例
if __name__ == '__main__':
    # 创建 RSS 生成器
    rss = RSSGenerator(
        title="每日邮件摘要播客",
        description="将您的邮件自动转换为播客，随时随地收听重要信息",
        author="AI 助手",
        email="3305363@qq.com",
        base_url="https://example.com/podcasts"  # 替换为您的实际 URL
    )
    
    # 添加示例集数
    rss.add_episode(
        audio_file='./podcasts/podcast_20260224.mp3',
        title="2026年2月24日邮件摘要",
        description="今日5封重要邮件的音频摘要，包括...",
        pub_date=datetime.now(),
        duration=180  # 3分钟
    )
    
    # 生成 RSS feed
    rss_content = rss.generate_rss('podcast.xml')
    print("✅ RSS feed 生成完成！")
    print(f"📍 Feed URL: {rss.get_feed_url()}")
    print("\n💡 使用方法：")
    print("1. 将 podcast.xml 和音频文件上传到您的服务器")
    print("2. 在播客播放器中添加 feed URL 即可订阅")
    print("3. 支持：Apple Podcasts、Spotify、小宇宙、Google Podcasts 等")
