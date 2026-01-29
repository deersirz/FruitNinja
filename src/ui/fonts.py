"""
字体管理模块
管理游戏中使用的字体
"""

import pygame
import os

art_font = 'Artier'
sans_font = 'NotoSansSC'  # 等线字体


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
            'title': 80,
            'subtitle': 50,
            'text': 30,
            'small': 20
        }
        
        # 中文字体备选列表
        self.chinese_fonts = [
            sans_font,  # 首选等线字体
            'simsun',   # 宋体
            'simhei',   # 黑体
            'microsoftyahei'  # 微软雅黑
        ]
    
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
        font_key = f"{font_name}_{size}" if font_name else f"{art_font}_{size}"
        
        # 如果字体已缓存，直接返回
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        # 加载字体
        try:
            if font_name:
                # 尝试加载指定字体
                font = self._load_specific_font(font_name, size)
            else:
                # 默认使用Artier字体
                font = self._load_specific_font(art_font, size)
            
            # 缓存字体
            self.fonts[font_key] = font
            
            return font
        except Exception as e:
            # 如果加载失败，使用Artier字体作为备选
            print(f"Failed to load font: {e}")
            font = self._load_specific_font(art_font, size)
            self.fonts[font_key] = font
            return font
    
    def _load_specific_font(self, font_name, size):
        """
        加载指定字体，实现字体回退机制
        
        Args:
            font_name (str): 字体名称
            size (int): 字体大小
            
        Returns:
            pygame.font.Font: 字体对象
        """
        # 尝试从多个位置加载字体文件
        font_paths = [
            os.path.join('assets', 'fonts', f'{font_name}.ttf'),
            os.path.join('src', 'ui', 'resource', 'font', f'{font_name}.ttf')
        ]
        
        # 尝试加载指定字体
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return pygame.font.Font(font_path, size)
                except Exception:
                    pass
        
        # 如果是中文字体，尝试备选字体
        if font_name == sans_font:
            for alt_font in self.chinese_fonts[1:]:
                try:
                    # 尝试系统字体
                    font = pygame.font.SysFont(alt_font, size)
                    if font is not None:
                        return font
                except Exception:
                    pass
        
        # 尝试系统默认字体
        try:
            font = pygame.font.SysFont(None, size)
            if font is not None:
                return font
        except Exception:
            pass
        
        # 最后使用pygame默认字体
        return pygame.font.Font(None, size)
    
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
        # 统一使用Artier字体，无论是否包含中文字符
        font = self.get_font(size, font_name or art_font)
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
        return self.render_text(text, self.default_sizes['title'], color, art_font)
    
    def render_subtitle(self, text, color=(255, 255, 255)):
        """
        渲染副标题文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['subtitle'], color, art_font)
    
    def render_text_normal(self, text, color=(255, 255, 255)):
        """
        渲染普通文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['text'], color, art_font)
    
    def render_small_text(self, text, color=(255, 255, 255)):
        """
        渲染小文本
        
        Args:
            text (str): 文本内容
            color (tuple): 文本颜色
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        return self.render_text(text, self.default_sizes['small'], color, art_font)
    
    def render_score_life_text(self, text, color=(255, 255, 255)):
        '''
        专门渲染分数和生命
        by Chaistr
        '''
        return self.render_text(str(text), self.default_sizes['text'], color, art_font)

    def clear_cache(self):
        """
        清空字体缓存
        """
        self.fonts.clear()
