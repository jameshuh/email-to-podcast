#!/usr/bin/env python3
"""
Email-to-Podcast MVP 技术原型
Phase 1: 基础功能测试

目标：验证技术可行性（Gmail API + ElevenLabs TTS + ffmpeg）
"""

import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置文件路径
CONFIG_DIR = Path.home() / ".config" / "email-to-podcast"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 临时测试文件
TEST_DIR = Path("/tmp/email-to-podcast-test")
TEST_DIR.mkdir(parents=True, exist_ok=True)

# 依赖检查
print("=" * 50)
print("Email-to-Podcast MVP - Phase 1 依赖检查")
print("=" * 50)

# 1. Python 依赖
print("\n1. Python 依赖检查:")
dependencies = {
    "requests": "HTTP 客户端（用于调用 API）",
    "googleapiclient": "Gmail API 客户端",
    "google_auth_httplib2": "Google 认证",
    "google_auth_oauthlib": "Google OAuth"
}

missing_deps = []
for dep, desc in dependencies.items():
    try:
        __import__(dep.replace("-", "_"))
        print(f"  ✅ {dep}: {desc}")
    except ImportError:
        print(f"  ❌ {dep}: {desc} (缺失)")
        missing_deps.append(dep)

if missing_deps:
    print(f"\n  需要安装: pip install {' '.join(missing_deps)}")

# 2. 系统依赖
print("\n2. 系统依赖检查:")
import subprocess

# ffmpeg
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    print(f"  ✅ ffmpeg: 音频处理工具")
except FileNotFoundError:
    print(f"  ❌ ffmpeg: 音频处理工具 (缺失)")
    print(f"     安装: brew install ffmpeg")

# 3. API Keys
print("\n3. API Keys 检查:")

# ElevenLabs API Key
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
if elevenlabs_key:
    print(f"  ✅ ElevenLabs API Key: 已设置")
else:
    print(f"  ❌ ElevenLabs API Key: 未设置")
    print(f"     获取: https://elevenlabs.io")
    print(f"     设置: export ELEVENLABS_API_KEY='your_key'")

# Gmail OAuth Credentials
gmail_creds = CONFIG_DIR / "credentials.json"
if gmail_creds.exists():
    print(f"  ✅ Gmail OAuth Credentials: {gmail_creds}")
else:
    print(f"  ❌ Gmail OAuth Credentials: 未找到")
    print(f"     获取: https://console.cloud.google.com")
    print(f"     保存: {gmail_creds}")

# 4. 测试文件准备
print("\n4. 测试文件准备:")

# 创建测试文本
test_text = """
Hello, this is a test email newsletter.

In this episode, we'll discuss the latest developments in AI technology.
Artificial Intelligence is transforming healthcare, finance, and many other industries.

Key highlights:
1. New AI models can diagnose diseases with 95% accuracy
2. Autonomous vehicles are becoming mainstream
3. AI assistants are getting smarter every day

That's all for today. Thank you for listening!
"""

test_file = TEST_DIR / "test_newsletter.txt"
with open(test_file, 'w') as f:
    f.write(test_text)

print(f"  ✅ 测试文本: {test_file}")
print(f"  ✅ 字符数: {len(test_text)}")

# 5. 下一步
print("\n" + "=" * 50)
print("下一步操作:")
print("=" * 50)
print("1. 安装缺失的依赖:")
if missing_deps:
    print(f"   pip install {' '.join(missing_deps)}")

print("\n2. 安装 ffmpeg:")
print("   brew install ffmpeg")

print("\n3. 获取 ElevenLabs API Key:")
print("   访问 https://elevenlabs.io 注册账号")
print("   export ELEVENLABS_API_KEY='your_key'")

print("\n4. 配置 Gmail OAuth:")
print("   访问 https://console.cloud.google.com")
print("   创建项目 → 启用 Gmail API → 获取 OAuth 凭据")
print(f"   保存到: {gmail_creds}")

print("\n5. 运行测试脚本:")
print("   python3 scripts/test_tts.py  # 测试 TTS API")
print("   python3 scripts/test_gmail.py  # 测试 Gmail API")

print("\n" + "=" * 50)
