"""
资源管理模块
负责游戏资源的加载和管理
"""

import pygame
import os
import sys
import threading
import concurrent.futures
import time


class ResourceManager:
    """
    资源管理器类
    管理游戏中的所有资源加载
    """
    def __init__(self):
        """
        初始化资源管理器
        """
        # 资源目录路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        self.images_dir = os.path.join(self.assets_dir, 'images')
        self.sounds_dir = os.path.join(self.assets_dir, 'sounds')
        self.fonts_dir = os.path.join(self.assets_dir, 'fonts')
        
        # 资源缓存
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        
        # 初始化pygame mixer
        pygame.mixer.init()
        
        # 线程池用于并行加载资源
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # 加载超时设置
        self.load_timeout = 2.0  # 资源加载超时时间（秒）
    
    def load_image(self, filename):
        """
        加载图片资源
        
        Args:
            filename: 图片文件名
            
        Returns:
            pygame.Surface: 加载的图片表面
        """
        if filename in self.images:
            return self.images[filename]
        
        def _load_image_task():
            try:
                # 尝试从当前项目的images目录加载
                image_path = os.path.join(self.images_dir, filename)
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path).convert_alpha()
                    self.images[filename] = image
                    return image
                
                # 尝试从上级目录的image目录加载（兼容旧项目结构）
                alt_image_path = os.path.join(os.path.dirname(self.base_dir), 'image', filename)
                if os.path.exists(alt_image_path):
                    image = pygame.image.load(alt_image_path).convert_alpha()
                    self.images[filename] = image
                    return image
                
                # 尝试从FruitNinja-main目录的image目录加载
                alt_image_path2 = os.path.join(os.path.dirname(self.base_dir), 'FruitNinja-main', 'image', filename)
                if os.path.exists(alt_image_path2):
                    image = pygame.image.load(alt_image_path2).convert_alpha()
                    self.images[filename] = image
                    return image
                
                print(f"Error loading image {filename}: File not found")
                return None
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                return None
        
        # 使用线程池执行加载任务，并设置超时
        future = self.executor.submit(_load_image_task)
        try:
            return future.result(timeout=self.load_timeout)
        except concurrent.futures.TimeoutError:
            print(f"Warning: Image loading timeout for {filename}")
            return None
    
    def load_sound(self, filename):
        """
        加载音效资源
        
        Args:
            filename: 音效文件名
            
        Returns:
            pygame.mixer.Sound: 加载的音效对象
        """
        if filename in self.sounds:
            return self.sounds[filename]
        
        def _load_sound_task():
            try:
                # 尝试从当前项目的sounds目录加载
                sound_path = os.path.join(self.sounds_dir, filename)
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[filename] = sound
                    return sound
                
                # 尝试从上级目录的sound目录加载（兼容旧项目结构）
                alt_sound_path = os.path.join(os.path.dirname(self.base_dir), 'sound', filename)
                if os.path.exists(alt_sound_path):
                    sound = pygame.mixer.Sound(alt_sound_path)
                    self.sounds[filename] = sound
                    return sound
                
                # 尝试从FruitNinja-main目录的sound目录加载
                alt_sound_path2 = os.path.join(os.path.dirname(self.base_dir), 'FruitNinja-main', 'sound', filename)
                if os.path.exists(alt_sound_path2):
                    sound = pygame.mixer.Sound(alt_sound_path2)
                    self.sounds[filename] = sound
                    return sound
                
                print(f"Error loading sound {filename}: File not found")
                return None
            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
                return None
        
        # 使用线程池执行加载任务，并设置超时
        future = self.executor.submit(_load_sound_task)
        try:
            return future.result(timeout=self.load_timeout)
        except concurrent.futures.TimeoutError:
            print(f"Warning: Sound loading timeout for {filename}")
            return None
    
    def load_font(self, filename, size):
        """
        加载字体资源
        
        Args:
            filename: 字体文件名
            size: 字体大小
            
        Returns:
            pygame.font.Font: 加载的字体对象
        """
        font_key = f"{filename}_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        def _load_font_task():
            try:
                font_path = os.path.join(self.fonts_dir, filename)
                font = pygame.font.Font(font_path, size)
                self.fonts[font_key] = font
                return font
            except Exception as e:
                print(f"Error loading font {filename}: {e}")
                # 回退到系统默认字体
                font = pygame.font.SysFont(None, size)
                self.fonts[font_key] = font
                return font
        
        # 使用线程池执行加载任务，并设置超时
        future = self.executor.submit(_load_font_task)
        try:
            return future.result(timeout=self.load_timeout)
        except concurrent.futures.TimeoutError:
            print(f"Warning: Font loading timeout for {filename}")
            # 超时后回退到系统默认字体
            font = pygame.font.SysFont(None, size)
            self.fonts[font_key] = font
            return font
    
    def load_music(self, filename):
        """
        加载背景音乐
        
        Args:
            filename: 音乐文件名
            
        Returns:
            bool: 是否加载成功
        """
        def _load_music_task():
            try:
                # 尝试从当前项目的sounds目录加载
                music_path = os.path.join(self.sounds_dir, filename)
                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    return True
                
                # 尝试从上级目录的sound目录加载（兼容旧项目结构）
                alt_music_path = os.path.join(os.path.dirname(self.base_dir), 'sound', filename)
                if os.path.exists(alt_music_path):
                    pygame.mixer.music.load(alt_music_path)
                    return True
                
                # 尝试从FruitNinja-main目录的sound目录加载
                alt_music_path2 = os.path.join(os.path.dirname(self.base_dir), 'FruitNinja-main', 'sound', filename)
                if os.path.exists(alt_music_path2):
                    pygame.mixer.music.load(alt_music_path2)
                    return True
                
                print(f"Error loading music {filename}: File not found")
                return False
            except Exception as e:
                print(f"Error loading music {filename}: {e}")
                return False
        
        # 使用线程池执行加载任务，并设置超时
        future = self.executor.submit(_load_music_task)
        try:
            return future.result(timeout=self.load_timeout)
        except concurrent.futures.TimeoutError:
            print(f"Warning: Music loading timeout for {filename}")
            return False
    
    def play_music(self, loops=-1):
        """
        播放背景音乐
        
        Args:
            loops: 播放次数，-1表示循环播放
        """
        try:
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self):
        """
        停止背景音乐
        """
        pygame.mixer.music.stop()
    
    def get_image(self, filename):
        """
        获取已加载的图片
        
        Args:
            filename: 图片文件名
            
        Returns:
            pygame.Surface: 图片表面
        """
        return self.images.get(filename)
    
    def get_sound(self, filename):
        """
        获取已加载的音效
        
        Args:
            filename: 音效文件名
            
        Returns:
            pygame.mixer.Sound: 音效对象
        """
        return self.sounds.get(filename)
    
    def get_font(self, filename, size):
        """
        获取已加载的字体
        
        Args:
            filename: 字体文件名
            size: 字体大小
            
        Returns:
            pygame.font.Font: 字体对象
        """
        font_key = f"{filename}_{size}"
        return self.fonts.get(font_key)
    
    def clear_cache(self):
        """
        清空资源缓存
        """
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
    
    def shutdown(self):
        """
        关闭资源管理器，释放线程池
        """
        self.executor.shutdown(wait=False)
        self.clear_cache()


# 创建全局资源管理器实例
resource_manager = ResourceManager()
