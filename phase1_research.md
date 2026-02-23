# Email-to-Podcast 技术原型 - Phase 1 研究

## 项目概述

**目标**: 构建一个将 email newsletter 转换为 podcast 的自动化服务

**技术栈**:
- Gmail API（读取邮件）
- ElevenLabs TTS API（文本转语音）
- ffmpeg（音频处理）

**预期效果**: 医疗 newsletter → 自动转换为音频 → 医生通勤收听

---

## Phase 1: 技术研究

### 1. Gmail API 研究笔记

**官方文档**: https://developers.google.com/gmail/api

**认证方式**: OAuth 2.0
- 需要创建 Google Cloud 项目
- 需要启用 Gmail API
- 需要获取 credentials（client_id, client_secret）

**Python 库**: `google-api-python-client`

**核心功能**:
```python
# 伪代码示例
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 认证
creds = Credentials.from_authorized_user_file('credentials.json')
service = build('gmail', 'v1', credentials=creds)

# 读取邮件
results = service.users().messages().list(userId='me', maxResults=10).execute()
messages = results.get('messages', [])

# 获取邮件内容
for msg in messages:
    message = service.users().messages().get(userId='me', id=msg['id']).execute()
    # 提取正文（需要解析 MIME 格式）
```

**挑战**:
1. **OAuth 认证**: 需要用户授权（无法完全自动化）
   - 解决方案: 让用户完成 OAuth 授权，保存 token
   
2. **邮件解析**: Gmail 返回 MIME 格式，需要解析 HTML/纯文本
   - 解决方案: 使用 `email` 库解析 MIME

3. **速率限制**: Gmail API 有速率限制
   - 解决方案: 批量读取，缓存结果

**成本**: 免费（每天 1,000,000 次 quota）

---

### 2. ElevenLabs TTS 研究笔记

**官方网站**: https://elevenlabs.io

**API 文档**: https://api.elevenlabs.io/docs

**定价**:
- Free: 10,000 characters/month
- Starter: $5/month (30,000 characters)
- Creator: $22/month (100,000 characters)
- Independent Publisher: $99/month (500,000 characters)

**Python 库**: 官方无库，使用 `requests` 调用 API

**核心功能**:
```python
import requests

API_KEY = 'your_api_key'
VOICE_ID = 'your_voice_id'  # 可选择不同声音

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "text": "Hello, this is a test.",
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}

response = requests.post(url, json=data, headers=headers)

# 保存音频
with open('output.mp3', 'wb') as f:
    f.write(response.content)
```

**声音选择**:
- 提供 10+ 预设声音
- 可克隆自定义声音（需要付费）
- 支持多语言（包括中文）

**挑战**:
1. **成本**: 需要付费订阅
   - 解决方案: 定价覆盖成本（$0.01-0.02/分钟）

2. **字符限制**: 免费层有限制
   - 解决方案: 使用付费订阅，按实际使用计费

3. **延迟**: 生成音频需要时间
   - 解决方案: 异步处理，后台生成

**成本计算**:
- 每封 newsletter 平均 5,000 字符
- Starter 计划（$5/month）可处理 6 封/月
- Creator 计划（$22/month）可处理 20 封/月
- Independent Publisher（$99/month）可处理 100 封/月

**定价策略**:
- Basic（$9.9/month）: 10 封 newsletter → 成本 ~$10 → 亏损
- Pro（$29.9/month）: 无限 newsletter → 成本 ~$50 → 盈利（如用户<50封）

**优化方案**:
1. 使用更便宜的 TTS（如 Google TTS, Amazon Polly）
2. 限制 Pro 用户的邮件数量
3. 提供基础版（使用免费 TTS，质量较低）

---

### 3. ffmpeg 研究笔记

**官方文档**: https://ffmpeg.org/documentation.html

**安装**: 
```bash
# macOS
brew install ffmpeg

# 验证
ffmpeg -version
```

**核心功能**:
```bash
# 合并多个音频文件
ffmpeg -i "concat:part1.mp3|part2.mp3|part3.mp3" -acodec copy output.mp3

# 转换格式
ffmpeg -i input.wav -acodec mp3 -ab 128k output.mp3

# 调整音量
ffmpeg -i input.mp3 -af "volume=1.5" output.mp3

# 添加背景音乐
ffmpeg -i voice.mp3 -i music.mp3 -filter_complex amix=inputs=2:duration=longest output.mp3
```

**Python 调用**:
```python
import subprocess

def concat_audio(files, output):
    """
    合并多个音频文件
    files: ['part1.mp3', 'part2.mp3', ...]
    output: 'output.mp3'
    """
    # 创建文件列表
    list_file = 'file_list.txt'
    with open(list_file, 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")
    
    # 调用 ffmpeg
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', list_file, '-c', 'copy', output
    ]
    subprocess.run(cmd, check=True)

def convert_to_mp3(input_file, output_file):
    """转换为 MP3 格式"""
    cmd = ['ffmpeg', '-i', input_file, '-acodec', 'mp3', '-ab', '128k', output_file]
    subprocess.run(cmd, check=True)
```

**挑战**:
1. **安装**: 需要在服务器上安装 ffmpeg
   - 解决方案: Docker 容器预装 ffmpeg

2. **大文件**: 处理大音频文件需要时间
   - 解决方案: 分段处理，流式输出

**成本**: 免费（开源工具）

---

## 技术架构设计

### 流程图

```
[Newsletter Email] 
    ↓
[Gmail API: 读取邮件]
    ↓
[文本提取: 解析 MIME]
    ↓
[文本处理: 清理/分段]
    ↓
[ElevenLabs TTS: 文本转语音]
    ↓
[ffmpeg: 合并音频]
    ↓
[Podcast MP3 输出]
```

### 数据流

1. **输入**: Gmail 账号 + newsletter 发件人列表
2. **处理**: 
   - 扫描新邮件（定时任务）
   - 提取纯文本内容
   - 调用 TTS API 转换
   - 合并音频文件
3. **输出**: MP3 文件 + RSS feed（用于 podcast 订阅）

### 技术栈

```yaml
后端:
  - Python 3.10+
  - FastAPI（API 服务）
  - Celery（后台任务）
  - Redis（队列管理）

外部服务:
  - Gmail API（读取邮件）
  - ElevenLabs API（TTS）
  
工具:
  - ffmpeg（音频处理）
  - ffmpeg-python（Python 绑定）

存储:
  - PostgreSQL（用户数据）
  - S3/MinIO（音频文件存储）
```

---

## MVP 实现计划

### Phase 1: 基础功能（本周）

**目标**: 手动处理一封 newsletter

**步骤**:
1. [ ] 手动获取 Gmail OAuth token（一次性）
2. [ ] 读取一封测试邮件
3. [ ] 提取纯文本内容
4. [ ] 调用 ElevenLabs TTS API
5. [ ] 使用 ffmpeg 生成最终音频
6. [ ] 验证输出质量

**交付物**: 一个可运行的 Python 脚本

### Phase 2: 自动化（下周）

**目标**: 自动处理新邮件

**步骤**:
1. [ ] 定时任务（扫描新邮件）
2. [ ] 用户管理（Gmail 授权）
3. [ ] 订阅系统（Stripe 集成）
4. [ ] 简单 Web UI

**交付物**: 可用的 Web 服务

### Phase 3: 市场验证（下月）

**目标**: 获得前 5 个付费用户

**步骤**:
1. [ ] Landing Page
2. [ ] 寻找测试用户（医疗专业人士）
3. [ ] 收集反馈
4. [ ] 优化产品

**交付物**: 5 个付费用户 + 产品反馈

---

## 成本分析

### 开发成本
- Gmail API: 免费
- ElevenLabs TTS: $22/month（Creator 计划）
- ffmpeg: 免费
- 服务器: $5-20/month（DigitalOcean）

**总计**: $27-42/month

### 运营成本（规模化）
- 每封 newsletter: $0.10-0.20（TTS 成本）
- 100 个用户（每人 30 封/月）: $300-600/month
- 服务器 + 存储: $50/month

**总计**: $350-650/month

### 收益预测
- 100 个 Basic 用户（$9.9/month）: $990/month
- 20 个 Pro 用户（$29.9/month）: $598/month

**总收益**: $1,588/month
**净利润**: $938-1,238/month

**ROI**: 144-265%

---

## 风险与应对

### 1. OAuth 认证复杂
- **风险**: 用户不愿意授权 Gmail 访问
- **应对**: 
  - 提供详细的隐私政策
  - 支持其他邮件服务（Outlook, Yahoo）
  - 提供"转发邮件"替代方案

### 2. TTS 成本过高
- **风险**: ElevenLabs 成本无法覆盖
- **应对**:
  - 使用更便宜的 TTS（Google TTS, Amazon Polly）
  - 限制邮件长度
  - 提供分层定价

### 3. 音频质量不佳
- **风险**: AI 语音不自然
- **应对**:
  - 选择高质量声音（ElevenLabs 最接近真人）
  - 提供"预览"功能
  - 支持自定义声音（付费）

### 4. 版权问题
- **风险**: newsletter 内容有版权
- **应对**:
  - 用户授权条款
  - 只处理用户订阅的内容
  - 与 newsletter 作者合作

---

## 下一步行动

**立即执行（今天）**:
1. [ ] 注册 ElevenLabs 账号（获取 API key）
2. [ ] 测试 ElevenLabs TTS API（调用示例）
3. [ ] 验证 ffmpeg 安装
4. [ ] 设计 MVP 脚本架构

**本周执行**:
1. [ ] 完成 Gmail API 集成（手动 OAuth）
2. [ ] 完成 TTS API 集成
3. [ ] 完成 ffmpeg 音频合并
4. [ ] 测试端到端流程

**下周执行**:
1. [ ] 搭建 FastAPI 后端
2. [ ] 设计数据库模型
3. [ ] 实现用户认证
4. [ ] 部署到测试环境

---

**创建时间**: 2026-02-18 08:10 AM
**下次更新**: Phase 1 技术原型完成后
**负责人**: CH
