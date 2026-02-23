#!/usr/bin/env python3
"""
文本处理模块
提取邮件关键信息，生成播客脚本
"""

import re
from datetime import datetime

class TextProcessor:
    def __init__(self, max_length=500):
        """
        初始化文本处理器
        
        Args:
            max_length: 每封邮件的最大处理长度（字符）
        """
        self.max_length = max_length
    
    def process_email(self, email_data):
        """
        处理单封邮件，生成播客片段
        
        Args:
            email_data: GmailReader 返回的邮件数据
        
        Returns:
            str: 播客片段脚本
        """
        subject = email_data.get('subject', '无主题')
        from_addr = email_data.get('from', '未知发件人')
        body = email_data.get('body', '')
        
        # 清理发件人地址（提取名字）
        from_name = self._extract_sender_name(from_addr)
        
        # 清理和压缩正文
        body_clean = self._clean_text(body)
        
        # 截断到最大长度
        if len(body_clean) > self.max_length:
            body_clean = body_clean[:self.max_length] + '...（内容已截断）'
        
        # 生成播客脚本
        script = f"""
接下来是一封来自 {from_name} 的邮件，主题是：{subject}。

邮件内容如下：
{body_clean}

邮件读毕。
"""
        return script.strip()
    
    def create_podcast_intro(self, total_emails):
        """
        创建播客开场白
        
        Args:
            total_emails: 邮件总数
        
        Returns:
            str: 开场白脚本
        """
        today = datetime.now().strftime('%Y年%m月%d日')
        
        intro = f"""
欢迎收听您的邮件播客。今天是 {today}。

本期播客将为您朗读 {total_emails} 封未读邮件。

让我们开始吧。
"""
        return intro.strip()
    
    def create_podcast_outro(self):
        """
        创建播客结束语
        
        Returns:
            str: 结束语脚本
        """
        outro = """
以上就是本期邮件播客的全部内容。

感谢您的收听，祝您有愉快的一天！
"""
        return outro.strip()
    
    def _extract_sender_name(self, from_addr):
        """
        从邮件地址提取发件人名字
        
        Args:
            from_addr: 完整的发件人地址
        
        Returns:
            str: 发件人名字
        """
        # 尝试提取 "Name <email@example.com>" 格式中的名字
        match = re.match(r'^(.+?)\s*<.+?>$', from_addr)
        if match:
            name = match.group(1).strip()
            # 移除引号
            name = name.strip('"\'')
            return name
        
        # 如果没有名字，返回邮箱地址
        return from_addr
    
    def _clean_text(self, text):
        """
        清理文本，移除无用字符
        
        Args:
            text: 原始文本
        
        Returns:
            str: 清理后的文本
        """
        # 移除 HTML 实体
        text = re.sub(r'&[a-z]+;', ' ', text)
        
        # 移除多余空白
        text = ' '.join(text.split())
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：""''（）\-\.\,\!\?]', '', text)
        
        return text.strip()
    
    def create_full_script(self, emails):
        """
        创建完整的播客脚本
        
        Args:
            emails: 邮件列表
        
        Returns:
            str: 完整脚本
        """
        script_parts = []
        
        # 开场白
        script_parts.append(self.create_podcast_intro(len(emails)))
        
        # 每封邮件
        for i, email in enumerate(emails, 1):
            script_parts.append(f"\n--- 第 {i} 封邮件 ---")
            script_parts.append(self.process_email(email))
        
        # 结束语
        script_parts.append(self.create_podcast_outro())
        
        return '\n\n'.join(script_parts)


if __name__ == '__main__':
    # 测试代码
    processor = TextProcessor(max_length=200)
    
    test_email = {
        'subject': '项目进度更新',
        'from': '张三 <zhangsan@example.com>',
        'date': '2026-02-18',
        'body': '你好，项目进展顺利，预计下周完成第一版开发。请查看附件中的详细报告。'
    }
    
    script = processor.process_email(test_email)
    print("📝 生成的播客片段：")
    print(script)
    
    print("\n" + "="*50)
    
    full_script = processor.create_full_script([test_email, test_email])
    print("\n📝 完整播客脚本：")
    print(full_script)
