"""
渲染器模块
负责游戏的渲染逻辑
"""

import pygame
from game.config import GameConfig
from ui.effects import EffectsManager
from ui.layout import UILayout


class Renderer:
    """
    渲染器类
    """
    def __init__(self, width=GameConfig.WINDOW_WIDTH, height=GameConfig.WINDOW_HEIGHT):
        """
        初始化渲染器
        
        Args:
            width (int): 屏幕宽度
            height (int): 屏幕高度
        """
        # 初始化PyGame显示
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(GameConfig.WINDOW_TITLE)
        
        # 初始化特效管理器
        self.effects_manager = EffectsManager()
        
        # 初始化布局管理器
        self.layout = UILayout(width, height)
        
        # 背景色
        self.background_color = GameConfig.BACKGROUND_COLOR
    
    def clear(self):
        """
        清除屏幕
        """
        self.screen.fill(self.background_color)
    
    def render_fruits(self, fruits):
        """
        渲染水果
        
        Args:
            fruits (list): 水果列表
        """
        for fruit in fruits:
            if not fruit.sliced:
                # 绘制水果
                pygame.draw.circle(self.screen, fruit.color, 
                                 (int(fruit.x), int(fruit.y)), fruit.radius)
                
                # 绘制水果轮廓
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (int(fruit.x), int(fruit.y)), fruit.radius, 2)
            else:
                # 绘制切割后的水果（简化版）
                # 这里可以实现更复杂的切割效果
                pass
    
    def render_gesture_trajectory(self, trajectory):
        """
        渲染手势轨迹
        
        Args:
            trajectory (list): 手势轨迹点列表
        """
        if len(trajectory) >= 2:
            # 绘制轨迹线
            points = [(p['x'], p['y']) for p in trajectory]
            pygame.draw.lines(self.screen, (255, 255, 255), False, points, 3)
            
            # 绘制轨迹点
            for point in trajectory:
                pygame.draw.circle(self.screen, (255, 0, 0), 
                                 (int(point['x']), int(point['y'])), 3)
    
    def render_bg(self):
        """
        xuan ran bei jing
        """
        self.layout.draw_bg(self.screen)
        pass

    def render_ui(self, score, combo, missed, game_time):
        """
        渲染UI元素
        
        Args:
            score (int): 当前分数
            combo (int): 当前连击数
            missed (int): 错过的水果数
            game_time (float): 游戏时间
        """
        self.layout.draw_ui(self.screen, score, combo, missed, game_time)
    
    def render_ready_screen(self):
        """
        渲染准备界面
        """
        self.layout.draw_ready_screen(self.screen)
    
    def render_pause_screen(self):
        """
        渲染暂停界面
        """
        self.layout.draw_pause_screen(self.screen)
    
    def render_game_over_screen(self, score, max_combo):
        """
        渲染游戏结束界面
        
        Args:
            score (int): 最终分数
            max_combo (int): 最大连击数
        """
        self.layout.draw_game_over_screen(self.screen, score, max_combo)
    
    def render_effects(self):
        """
        渲染特效
        """
        self.effects_manager.draw(self.screen)
    
    def update_display(self):
        """
        更新显示
        """
        pygame.display.flip()
    
    def update_effects(self, dt):
        """
        更新特效
        
        Args:
            dt (float): 时间步长（秒）
        """
        self.effects_manager.update(dt)
    
    def create_slice_effect(self, x, y, color):
        """
        创建切割特效
        
        Args:
            x (float): 切割位置x坐标
            y (float): 切割位置y坐标
            color (tuple): 切割效果颜色
        """
        self.effects_manager.create_slice_effect(x, y, color)
    
    def create_explosion_effect(self, x, y, color):
        """
        创建爆炸特效
        
        Args:
            x (float): 爆炸位置x坐标
            y (float): 爆炸位置y坐标
            color (tuple): 爆炸颜色
        """
        self.effects_manager.create_explosion(x, y, color)
    
    def clear_effects(self):
        """
        清空特效
        """
        self.effects_manager.clear()
