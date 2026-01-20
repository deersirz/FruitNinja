"""
界面布局模块
管理游戏界面的布局和UI元素
"""

import pygame
from game.config import GameConfig
from ui.fonts import FontManager


class UILayout:
    """
    界面布局管理器类
    管理游戏中所有UI元素的位置和绘制
    """
    def __init__(self, width, height):
        """
        初始化界面布局管理器
        
        Args:
            width (int): 屏幕宽度
            height (int): 屏幕高度
        """
        self.width = width
        self.height = height
        self.font_manager = FontManager()
        
        # UI元素位置映射
        self.ui_positions = {
            'score': (20, 20),
            'combo': (self.width // 2, 50),
            'missed': (self.width - 150, 20),
            'time': (self.width // 2, self.height - 40),
            'game_over_title': (self.width // 2, self.height // 3),
            'game_over_score': (self.width // 2, self.height // 2),
            'game_over_combo': (self.width // 2, self.height // 2 + 40),
            'game_over_restart': (self.width // 2, self.height // 2 + 120),
            'ready_title': (self.width // 2, self.height // 3),
            'ready_start': (self.width // 2, self.height // 2 + 40),
            'pause_title': (self.width // 2, self.height // 3),
            'pause_resume': (self.width // 2, self.height // 2 + 40)
        }
    
    def draw_ui(self, surface, score, combo, missed, game_time):
        """
        绘制游戏UI元素
        
        Args:
            surface (pygame.Surface): 绘制表面
            score (int): 当前分数
            combo (int): 当前连击数
            missed (int): 错过的水果数
            game_time (float): 游戏时间
        """
        # 绘制分数
        score_text = f"Score: {score}"
        score_surface = self.font_manager.render_text_normal(score_text, (255, 255, 255))
        score_rect = score_surface.get_rect(topleft=self.ui_positions['score'])
        surface.blit(score_surface, score_rect)
        
        # 绘制连击数
        if combo > 1:
            combo_text = f"Combo: {combo}x"
            combo_surface = self.font_manager.render_text(combo * 2, combo_text, (255, 215, 0))
            combo_rect = combo_surface.get_rect(center=self.ui_positions['combo'])
            surface.blit(combo_surface, combo_rect)
        
        # 绘制错过的水果数
        missed_text = f"Missed: {missed}/{GameConfig.MAX_MISSED_FRUITS}"
        missed_surface = self.font_manager.render_text_normal(missed_text, (255, 0, 0))
        missed_rect = missed_surface.get_rect(topleft=self.ui_positions['missed'])
        surface.blit(missed_surface, missed_rect)
        
        # 绘制游戏时间
        time_left = max(0, GameConfig.GAME_DURATION - game_time)
        time_text = f"Time: {int(time_left)}s"
        time_surface = self.font_manager.render_text_normal(time_text, (255, 255, 255))
        time_rect = time_surface.get_rect(center=self.ui_positions['time'])
        surface.blit(time_surface, time_rect)
    
    def draw_game_over_screen(self, surface, score, max_combo):
        """
        绘制游戏结束界面
        
        Args:
            surface (pygame.Surface): 绘制表面
            score (int): 最终分数
            max_combo (int): 最大连击数
        """
        # 绘制游戏结束标题
        title_text = "Game Over"
        title_surface = self.font_manager.render_title(title_text, (255, 0, 0))
        title_rect = title_surface.get_rect(center=self.ui_positions['game_over_title'])
        surface.blit(title_surface, title_rect)
        
        # 绘制最终分数
        score_text = f"Final Score: {score}"
        score_surface = self.font_manager.render_subtitle(score_text, (255, 255, 255))
        score_rect = score_surface.get_rect(center=self.ui_positions['game_over_score'])
        surface.blit(score_surface, score_rect)
        
        # 绘制最大连击数
        combo_text = f"Max Combo: {max_combo}x"
        combo_surface = self.font_manager.render_text_normal(combo_text, (255, 215, 0))
        combo_rect = combo_surface.get_rect(center=self.ui_positions['game_over_combo'])
        surface.blit(combo_surface, combo_rect)
        
        # 绘制重新开始提示
        restart_text = "Click to Restart"
        restart_surface = self.font_manager.render_text_normal(restart_text, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=self.ui_positions['game_over_restart'])
        surface.blit(restart_surface, restart_rect)
    
    def draw_ready_screen(self, surface):
        """
        绘制游戏准备界面
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制游戏标题
        title_text = "Fruit Ninja"
        title_surface = self.font_manager.render_title(title_text, (255, 255, 255))
        title_rect = title_surface.get_rect(center=self.ui_positions['ready_title'])
        surface.blit(title_surface, title_rect)
        
        # 绘制开始提示
        start_text = "Click to Start"
        start_surface = self.font_manager.render_subtitle(start_text, (255, 255, 255))
        start_rect = start_surface.get_rect(center=self.ui_positions['ready_start'])
        surface.blit(start_surface, start_rect)
    
    def draw_pause_screen(self, surface):
        """
        绘制游戏暂停界面
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制暂停标题
        title_text = "Paused"
        title_surface = self.font_manager.render_title(title_text, (255, 255, 255))
        title_rect = title_surface.get_rect(center=self.ui_positions['pause_title'])
        surface.blit(title_surface, title_rect)
        
        # 绘制继续提示
        resume_text = "Press Space to Resume"
        resume_surface = self.font_manager.render_subtitle(resume_text, (255, 255, 255))
        resume_rect = resume_surface.get_rect(center=self.ui_positions['pause_resume'])
        surface.blit(resume_surface, resume_rect)
    
    def get_ui_position(self, ui_element):
        """
        获取UI元素位置
        
        Args:
            ui_element (str): UI元素名称
            
        Returns:
            tuple: UI元素位置坐标
        """
        return self.ui_positions.get(ui_element, (0, 0))
