# Gmail API 启用指南

## 问题诊断
✅ OAuth 认证成功
✅ Token 有效
✅ 代理配置成功
❌ Gmail API 未启用

错误信息: "Mail service not enabled"

## 解决步骤

### 1. 访问 Google Cloud Console
https://console.cloud.google.com/

### 2. 选择项目
选择你创建 OAuth client 的项目 (calm-magpie-487800-i2)

### 3. 启用 Gmail API
1. 左侧菜单 → "API 和服务" → "库"
2. 搜索 "Gmail API"
3. 点击 "Gmail API"
4. 点击 "启用" 按钮

### 4. 等待生效
- 通常立即生效
- 如果仍然失败,等待 1-2 分钟后重试

## 验证
启用后,运行测试脚本验证:
```bash
cd /Users/hwf/.openclaw/workspace-work/email-to-podcast
python3 test_gmail_api.py
```

预期结果:
```
✅ 找到 5 封最近邮件
```

## 当前进度
- ✅ Phase 1 技术研究 (100%)
- ✅ OAuth 认证 (100%)
- ✅ 代理配置 (100%)
- ⏳ Gmail API 启用 (需要用户操作)
- ⏳ ElevenLabs API Key (需要用户注册)

## 下一步
启用 Gmail API 后:
1. 测试读取邮件
2. 集成 ElevenLabs TTS
3. 音频合并测试
4. MVP 完整流程
