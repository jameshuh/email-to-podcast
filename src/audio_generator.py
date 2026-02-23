#!/usr/bin/env python3
"""
音频生成模块
使用 ElevenLabs TTS 将文本转为音频
"""

import os
import requests
import time
from pathlib import Path

class AudioGenerator:
    def __init__(self, api_key_path, voice_id=None):
        """
        初始化音频生成器
        
        Args:
            api_key_path: ElevenLabs API Key 文件路径
            voice_id: 声音 ID（可选，默认使用 Roger）
        """
        with open(os.path.expanduser(api_key_path)) as f:
            self.api_key = f.read().strip()
        
        # 默认使用 Roger 声音（成熟、自信）
        self.voice_id = voice_id or "CwhRBWXzdaRdYWBFblAy"  # Roger
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def text_to_speech(self, text, output_path=None):
        """
        将文本转为语音
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径（可选）
        
        Returns:
            bytes: 音频数据（如果 output_path 为 None）
            str: 保存的文件路径（如果 output_path 不为 None）
        """
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.6,  # 稳定性（0-1）
                "similarity_boost": 0.8  # 相似度增强（0-1）
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"TTS 失败: {response.status_code} - {response.text}")
        
        audio_data = response.content
        
        if output_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return output_path
        else:
            return audio_data
    
    def text_to_speech_batch(self, texts, output_dir, prefix='audio'):
        """
        批量将文本转为语音
        
        Args:
            texts: 文本列表
            output_dir: 输出目录
            prefix: 文件名前缀
        
        Returns:
            list: 生成的音频文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        
        for i, text in enumerate(texts, 1):
            print(f"  🎙️ 生成第 {i}/{len(texts)} 段音频...")
            
            output_path = os.path.join(output_dir, f"{prefix}_{i:03d}.mp3")
            
            try:
                self.text_to_speech(text, output_path)
                audio_files.append(output_path)
                
                # 避免 API 限流
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ⚠️ 第 {i} 段生成失败: {e}")
                continue
        
        return audio_files
    
    def get_available_voices(self):
        """
        获取可用的声音列表
        
        Returns:
            list: 声音信息列表
        """
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"获取声音列表失败: {response.status_code}")
        
        voices = response.json()["voices"]
        
        return [
            {
                "id": v["voice_id"],
                "name": v["name"],
                "labels": v.get("labels", {})
            }
            for v in voices
        ]


if __name__ == '__main__':
    # 测试代码
    api_key_path = "~/.config/elevenlabs/api_key.txt"
    
    generator = AudioGenerator(api_key_path)
    
    print("📊 获取可用声音...")
    voices = generator.get_available_voices()
    print(f"找到 {len(voices)} 个声音:")
    for v in voices[:5]:
        print(f"  - {v['name']} ({v['id'][:8]}...)")
    
    print("\n🎙️ 测试文本转语音...")
    test_text = "这是一段测试音频，用于验证 ElevenLabs TTS 服务。"
    output_path = "/tmp/test_tts.mp3"
    
    result = generator.text_to_speech(test_text, output_path)
    print(f"✅ 音频已保存到: {result}")
    print(f"   文件大小: {os.path.getsize(result) / 1024:.1f} KB")
