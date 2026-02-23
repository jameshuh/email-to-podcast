# Email-to-Podcast 服务 - 国内版

> 完全基于国内服务，无需翻墙，将邮件自动转换为播客音频

## 🎯 服务特点

- ✅ **完全国产化**：QQ邮箱 + 百度AI，无网络限制
- ✅ **高质量语音**：百度TTS支持多种声音，语音自然流畅
- ✅ **自动化**：定时执行，无需手动操作
- ✅ **可定制**：支持自定义片头片尾、语速、音调等

## 📋 服务内容

### 基础服务
- 读取未读邮件（最多10封）
- 转换为高质量MP3音频
- 合并为单个播客文件

### 高级服务
- 自定义片头片尾
- 特定发件人过滤
- 多种声音选择
- 语速/音调调整
- RSS feed 生成

## 💰 定价

### 个人版
- **¥99/月**
- 每天自动生成1个播客
- 最多10封邮件/天
- 标准语音

### 专业版
- **¥299/月**
- 每天自动生成3个播客
- 最多30封邮件/天
- 自定义片头片尾
- 高级语音选择

### 企业版
- **¥999/月**
- 无限制播客生成
- 无限制邮件数量
- 完全定制化
- 专属客服支持

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pydub
brew install ffmpeg  # macOS
```

### 2. 配置

```python
config = {
    'email': {
        'address': 'your_email@qq.com',
        'password': 'your_auth_code',  # QQ邮箱授权码
        'imap_server': 'imap.qq.com'
    },
    'baidu': {
        'api_key': 'your_baidu_api_key',
        'secret_key': 'your_baidu_secret_key'
    }
}
```

### 3. 运行

```python
python service.py
```

## 📝 获取配置信息

### QQ邮箱授权码
1. 登录 QQ 邮箱
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 IMAP/SMTP 服务
4. 生成授权码

详细教程：https://service.mail.qq.com/detail/0/75

### 百度AI API Key
1. 访问百度AI控制台：https://console.bce.baidu.com/ai/
2. 选择"语音技术" → "语音合成"
3. 创建应用，获取 API Key 和 Secret Key
4. 免费额度：每月 20000 次

## 🔧 高级用法

### RSS Feed 生成（支持播客订阅）

```python
from rss_generator import RSSGenerator

# 创建 RSS 生成器
rss = RSSGenerator(
    title="每日邮件摘要播客",
    description="将您的邮件自动转换为播客",
    author="您的名字",
    email="your@email.com",
    base_url="https://your-domain.com/podcasts"
)

# 添加播客集数
rss.add_episode(
    audio_file='./podcasts/podcast_20260224.mp3',
    title="2026年2月24日邮件摘要",
    description="今日邮件摘要...",
    duration=180
)

# 生成 RSS feed
rss.generate_rss('podcast.xml')
```

**支持的播客平台**：
- Apple Podcasts
- Spotify
- Google Podcasts
- 小宇宙
- 喜马拉雅
- 其他支持 RSS 的播客播放器

### 定时执行

```python
import schedule
import time

def morning_podcast():
    converter = EmailToPodcast(config['email'], config['baidu'])
    podcast = converter.generate_podcast(email_limit=10)
    # 发送到手机或播放器...

schedule.every().day.at("07:00").do(morning_podcast)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 特定发件人过滤

```python
# 只转换特定发件人的邮件
emails = email_reader.fetch_from_sender('newsletter@example.com', limit=10)
```

### 自定义片头片尾

```python
intro = "欢迎收听今日邮件摘要播客"
outro = "以上就是今日邮件摘要，感谢收听"
podcast = converter.generate_podcast(
    email_limit=5,
    intro_text=intro,
    outro_text=outro
)
```

## 📊 成本估算

- 百度AI：免费额度 20000 次/月（足够个人使用）
- 无其他费用

## 🆘 常见问题

**Q: 支持哪些邮箱？**
A: 支持所有支持IMAP协议的邮箱（QQ邮箱、网易邮箱、Gmail等）

**Q: 音频质量如何？**
A: 百度TTS是业内领先的语音合成服务，音质接近真人

**Q: 可以自定义声音吗？**
A: 可以，支持男声、女声、情感合成等多种声音

**Q: 多久可以生成一个播客？**
A: 取决于邮件数量，一般5-10封邮件约需1-2分钟

## 📞 联系方式

- Email: 3305363@qq.com
- GitHub: https://github.com/jameshuh/dataflow

---

> 由 AI 助手开发维护 | 专注自动化工具开发
