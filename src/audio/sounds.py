"""
音效管理模块
管理游戏中的音效
"""

import pygame
import os
from game.config import GameConfig


class SoundManager:
    """
    音效管理器类
    管理游戏中所有音效的加载和播放
    """
    def __init__(self):
        """
        初始化音效管理器
        """
        self.sounds = {}
        self.volume = GameConfig.SOUND_VOLUME
        
        # 预定义音效映射
        self.sound_files = {
            'slice': 'slice.wav',
            'start': 'start.wav',
            'pause': 'pause.wav',
            'resume': 'resume.wav',
            'game_over': 'game_over.wav',
            'combo': 'combo.wav'
        }
        
        self._load_sounds()
    
    def _load_sounds(self):
        """
        加载预定义音效文件
        """
        for sound_name, sound_file in self.sound_files.items():
            try:
                sound_path = os.path.join('assets', 'sounds', 'effects', sound_file)
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                else:
                    print(f"Sound file not found: {sound_path}")
                    self.sounds[sound_name] = None
            except Exception as e:
                print(f"Failed to load sound {sound_name}: {e}")
                self.sounds[sound_name] = None
    
    def play_sound(self, sound_name):
        """
        播放指定音效
        
        Args:
            sound_name (str): 音效名称
        """
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Failed to play sound {sound_name}: {e}")
    
    def set_volume(self, volume):
        """
        设置音效音量
        
        Args:
            volume (float): 音量大小（0.0-1.0）
        """
        self.volume = max(0.0, min(1.0, volume))
        for sound_name, sound in self.sounds.items():
            if sound:
                sound.set_volume(self.volume)
    
    def get_volume(self):
        """
        获取当前音量
        
        Returns:
            float: 当前音量
        """
        return self.volume
    
    def stop_all_sounds(self):
        """
        停止所有正在播放的音效
        """
        pygame.mixer.stop()
    
    def add_sound(self, sound_name, sound_path):
        """
        添加自定义音效
        
        Args:
            sound_name (str): 音效名称
            sound_path (str): 音效文件路径
        """
        try:
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(self.volume)
                self.sounds[sound_name] = sound
            else:
                print(f"Sound file not found: {sound_path}")
        except Exception as e:
            print(f"Failed to add sound {sound_name}: {e}")
    
    def remove_sound(self, sound_name):
        """
        移除指定音效
        
        Args:
            sound_name (str): 音效名称
        """
        if sound_name in self.sounds:
            del self.sounds[sound_name]
