"""
音频管理器模块
管理游戏的音频系统
"""

import pygame
from audio.sounds import SoundManager


class AudioManager:
    """
    音频管理器类
    管理游戏中所有音频的加载和播放
    """
    def __init__(self):
        """
        初始化音频管理器
        """
        # 初始化PyGame音频
        pygame.mixer.init()
        
        # 初始化音效管理器
        self.sound_manager = SoundManager()
        
        # 事件与音效的映射
        self.event_sound_map = {
            'fruit_sliced': 'slice',
            'game_start': 'start',
            'game_pause': 'pause',
            'game_resume': 'resume',
            'game_over': 'game_over',
            'combo': 'combo'
        }
        
        # 背景音乐
        self.background_music = None
        self.music_volume = 0.5
    
    def init(self):
        """
        初始化音频系统
        """
        # 重新初始化音频系统
        pygame.mixer.quit()
        pygame.mixer.init()
        
        # 重新加载音效
        self.sound_manager = SoundManager()
    
    def play_sound(self, sound_name):
        """
        播放音效
        
        Args:
            sound_name (str): 音效名称
        """
        self.sound_manager.play_sound(sound_name)
    
    def play_music(self, music_file, loop=True):
        """
        播放背景音乐
        
        Args:
            music_file (str): 音乐文件路径
            loop (bool): 是否循环播放
        """
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.background_music = music_file
        except Exception as e:
            print(f"Failed to play music: {e}")
    
    def stop_music(self):
        """
        停止背景音乐
        """
        pygame.mixer.music.stop()
        self.background_music = None
    
    def pause_music(self):
        """
        暂停背景音乐
        """
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """
        恢复播放背景音乐
        """
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """
        设置背景音乐音量
        
        Args:
            volume (float): 音量大小（0.0-1.0）
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """
        设置音效音量
        
        Args:
            volume (float): 音量大小（0.0-1.0）
        """
        self.sound_manager.set_volume(volume)
    
    def get_music_volume(self):
        """
        获取背景音乐音量
        
        Returns:
            float: 音量大小
        """
        return self.music_volume
    
    def get_sound_volume(self):
        """
        获取音效音量
        
        Returns:
            float: 音量大小
        """
        return self.sound_manager.get_volume()
    
    def process_event(self, event_type, **kwargs):
        """
        处理游戏事件，播放对应的音效
        
        Args:
            event_type (str): 事件类型
            **kwargs: 事件参数
        """
        # 播放对应的音效
        if event_type in self.event_sound_map:
            sound_name = self.event_sound_map[event_type]
            self.sound_manager.play_sound(sound_name)
        
        # 处理特殊事件
        if event_type == 'combo':
            # 处理连击事件
            combo = kwargs.get('combo', 0)
            if combo > 5:
                # 播放连击音效
                self.sound_manager.play_sound('combo')
    
    def register_event(self, event_type, sound_name):
        """
        注册新的事件与音效映射
        
        Args:
            event_type (str): 事件类型
            sound_name (str): 音效名称
        """
        self.event_sound_map[event_type] = sound_name
    
    def unregister_event(self, event_type):
        """
        注销事件与音效映射
        
        Args:
            event_type (str): 事件类型
        """
        if event_type in self.event_sound_map:
            del self.event_sound_map[event_type]
    
    def get_event_sound(self, event_type):
        """
        获取事件对应的音效
        
        Args:
            event_type (str): 事件类型
            
        Returns:
            str: 音效名称
        """
        return self.event_sound_map.get(event_type, None)
    
    def quit(self):
        """
        退出音频系统
        """
        # 停止所有音频
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        
        # 退出音频系统
        pygame.mixer.quit()
