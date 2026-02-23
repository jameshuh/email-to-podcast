#!/usr/bin/env python3
"""
播客创建模块
使用 ffmpeg 合并多个音频文件为一个播客
"""

import os
import subprocess
from pathlib import Path

class PodcastCreator:
    def __init__(self):
        """初始化播客创建器"""
        pass
    
    def merge_audio_files(self, audio_files, output_path, silence_duration=1):
        """
        合并多个音频文件为一个播客
        
        Args:
            audio_files: 音频文件路径列表
            output_path: 输出文件路径
            silence_duration: 每段之间的静音时长（秒）
        
        Returns:
            str: 生成的播客文件路径
        """
        if not audio_files:
            raise ValueError("音频文件列表不能为空")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 创建文件列表（用于 ffmpeg concat）
        list_file = "/tmp/audio_list.txt"
        
        with open(list_file, 'w') as f:
            for audio_file in audio_files:
                # ffmpeg 需要转义路径中的特殊字符
                escaped_path = audio_file.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        # 使用 ffmpeg 合并音频
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y',  # 覆盖已存在的文件
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ 播客已生成: {output_path}")
            print(f"   文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
            
            # 清理临时文件
            os.remove(list_file)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ffmpeg 错误: {e.stderr}")
            raise
    
    def add_intro_outro(self, podcast_path, intro_path=None, outro_path=None, output_path=None):
        """
        添加片头和片尾音乐（可选功能）
        
        Args:
            podcast_path: 播客文件路径
            intro_path: 片头音乐路径（可选）
            outro_path: 片尾音乐路径（可选）
            output_path: 输出文件路径（可选，默认覆盖原文件）
        
        Returns:
            str: 最终播客文件路径
        """
        if output_path is None:
            output_path = podcast_path
        
        files_to_merge = []
        
        if intro_path and os.path.exists(intro_path):
            files_to_merge.append(intro_path)
        
        files_to_merge.append(podcast_path)
        
        if outro_path and os.path.exists(outro_path):
            files_to_merge.append(outro_path)
        
        if len(files_to_merge) == 1:
            # 没有片头片尾，直接返回原文件
            return podcast_path
        
        # 合并
        return self.merge_audio_files(files_to_merge, output_path)
    
    def get_audio_duration(self, audio_path):
        """
        获取音频时长
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            float: 时长（秒）
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"⚠️ 无法获取音频时长: {e}")
            return 0


if __name__ == '__main__':
    # 测试代码
    creator = PodcastCreator()
    
    # 创建测试音频文件（使用之前生成的测试文件）
    test_files = [
        "/tmp/test_tts.mp3",
        "/tmp/test_audio.mp3"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    if existing_files:
        print(f"📊 找到 {len(existing_files)} 个测试音频文件")
        
        print("\n🎙️ 合并音频文件...")
        output_path = "/tmp/test_podcast.mp3"
        
        try:
            result = creator.merge_audio_files(existing_files, output_path)
            print(f"✅ 测试播客已生成: {result}")
            
            duration = creator.get_audio_duration(result)
            print(f"   时长: {duration:.1f} 秒")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("⚠️ 没有找到测试音频文件，请先运行 audio_generator.py 生成测试文件")
