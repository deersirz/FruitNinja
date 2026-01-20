"""
字体管理模块
管理游戏中使用的字体
"""

import pygame
import os


class FontManager:
    """
    字体管理器类
    """
    def __init__(self):
        """
        初始化字体管理器
        """
        # 初始化PyGame字体
        pygame.font.init()
        
        # 字体缓存
        self.fonts = {}
        
        # 默认字体大小
        self.default_sizes = {
            'title': 48,
            'subtitle': 36,
            'text': 24,
            'small': 18
        }
    
    def get_font(self, size, font_name=None):
        """
        获取字体
        
        Args:
            size (int): 字体大小
            font_name (str): 字体名称
            
        Returns:
            pygame.font.Font: 字体对象
        """
        # 生成字体键
        font_key = f"{font_name}_{size}" if font_name else f"default_{size}"
        
        # 如果字体已缓存，直接返回
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        # 加载字体
        try:
            if font_name:
                # 尝试加载指定字体
                font_path = os.path.join('assets', 'fonts', f'{font_name}.ttf')
                if os.path.exists(font_path):
                    font = pygame.font.Font(font_path, size)
                else:
                    # 如果指定字体不存在，使用默认字体
                    font = pygame.font.Font(None, size)
            else:
                # 使用默认字体
                font = pygame.font.Font(None, size)
            
            # 缓存字体
            self.fonts[font_key] = font
            
            return font
        except Exception as e:
            # 如果加载失败，使用默认字体
            print(f"Failed to load font: {e}")
            font = pygame.font.Font(None, size)
            self.fonts[font_key] = font
            return font
    
    def get_title_font(self):
        """
        获取标题字体
        
        Returns:
            pygame.font.Font: 标题字体
        """
        return self.get_font(self.default_sizes['title'])
    
    def get_subtitle_font(self):
        """
        获取副标题字体
        
        Returns:
            pygame.font.Font: 副标题字体
        """
        return self.get_font(self.default_sizes['subtitle'])
    
    def get_text_font(self):
        """
        获取文本字体
        
        Returns:
            pygame.font.Font: 文本字体
        """
        return self.get_font(self.default_sizes['text'])
    
    def get_small_font(self):
        """
        获取小字体
        
        Returns:
            pygame.font.Font: 小字体
        """
        return self.get_font(self.default_sizes['small'])
    
    def render_text(self, text, size, color=(255, 255, 255), font_name=None):
        """
        渲染文本
        
        Args:
            text (str): 文本内容
            size (int): 字体大小
            color (tuple): 文本颜色
            font_name (str): 字体名称
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        font = self.get_font(size, font_name)
        return font.render(text, True, color)
    
    def render_title(self, text, color=(255, 255, 255)):
        """
        渲染标题文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['title'], color)
    
    def render_subtitle(self, text, color=(255, 255, 255)):
        """
        渲染副标题文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['subtitle'], color)
    
    def render_text_normal(self, text, color=(255, 255, 255)):
        """
        渲染普通文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['text'], color)
    
    def render_small_text(self, text, color=(255, 255, 255)):
        """
        渲染小文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['small'], color)
    
    def clear_cache(self):
        """
        清空字体缓存
        """
        self.fonts.clear()
