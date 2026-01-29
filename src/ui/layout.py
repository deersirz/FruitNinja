"""
界面布局模块
管理游戏界面的布局和UI元素
"""

import pygame
from game.config import GameConfig
from ui.fonts import FontManager
from utils.resource import resource_manager


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
            'score': (30, 30),
            'combo': (self.width // 2, 50),
            'missed': (self.width - 200, 30),
            'time': (self.width // 2, self.height - 40),
            'game_over_title': (self.width // 2, self.height // 3),
            'game_over_score': (self.width // 2, self.height // 2),
            'game_over_combo': (self.width // 2, self.height // 2 + 40),
            'game_over_restart': (self.width // 2, self.height // 2 + 120),
            'game_over_quit': (self.width // 2, self.height // 2 + 180),
            'ready_title': (self.width // 2, self.height // 3),
            'ready_start': (self.width // 2, self.height // 3 + 100),
            'pause_title': (self.width // 2, self.height // 3),
            'pause_resume': (self.width // 2, self.height // 2 + 40),
            'title_screen_title': (self.width // 2, self.height // 3),
            'title_screen_start': (self.width // 2, self.height // 3 + 100),
            'title_screen_duration': (50, 30),
            'title_screen_rules': (self.width - 180, self.height - 60),
            'title_screen_quit': (self.width - 180, self.height - 120),
            'camera_preview': (10, self.height - 150)  # 左下角摄像头预览窗口位置，避免与血量显示冲突
        }

        # 加载资源
        self.load_resources()
        
        # 游戏时长选择
        self.selected_duration = GameConfig.DEFAULT_GAME_DURATION
        self.show_rules = False
    
    def load_resources(self):
        """
        加载UI相关资源
        """
        # 加载图片资源
        self.title_image = resource_manager.load_image('title.png')
        self.logo_image = resource_manager.load_image('logo.png')
        # 使用title.png作为背景图片
        self.background_image = resource_manager.load_image('title.png')
        
        # 加载按钮图片
        self.start_button_image = resource_manager.load_image('new-game.png')
        self.start_button_hover = resource_manager.load_image('new-game-hover.png')
        self.start_button_click = resource_manager.load_image('new-game-click.png')
        
        # 加载心形图片
        self.heart_image = resource_manager.load_image('heart.png')
        
        # 缩放图片
        if self.start_button_image:
            self.start_button_image = pygame.transform.scale(self.start_button_image, (200, 200))
        if self.start_button_hover:
            self.start_button_hover = pygame.transform.scale(self.start_button_hover, (200, 200))
        if self.start_button_click:
            self.start_button_click = pygame.transform.scale(self.start_button_click, (200, 200))
        if self.heart_image:
            self.heart_image = pygame.transform.scale(self.heart_image, (40, 40))
        if self.background_image:
            # 将背景图片缩放到与窗口大小一致
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        if self.title_image:
            # 计算标题图片的最佳缩放比例，保持宽高比
            img_width, img_height = self.title_image.get_size()
            max_title_height = self.height // 2  # 限制标题图片高度为窗口高度的一半
            scale = min(self.width * 0.8 / img_width, max_title_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            self.title_image = pygame.transform.scale(self.title_image, (new_width, new_height))
    
    def draw_bg(self, surface):
        """
        绘制背景图
        """
        if self.background_image:
            # 背景图片已缩放到窗口大小，直接从(0, 0)位置绘制
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(GameConfig.BACKGROUND_COLOR)
    
    def draw_ui(self, surface, score, combo, missed, game_time, game_duration):
        """
        绘制游戏UI元素
        
        Args:
            surface (pygame.Surface): 绘制表面
            score (int): 当前分数
            combo (int): 当前连击数
            missed (int): 错过的水果数
            game_time (float): 游戏时间
            game_duration (int): 游戏时长
        """
        # 绘制分数
        score_text = f"Score: {score}"
        score_surface = self.font_manager.render_score_life_text(score_text, GameConfig.WHITE)
        score_rect = score_surface.get_rect(topleft=self.ui_positions['score'])
        surface.blit(score_surface, score_rect)
        
        # 绘制连击数
        if combo > 1:
            combo_text = f"Combo: {combo}x"
            combo_surface = self.font_manager.render_text(combo_text, combo * 2, GameConfig.GOLD)
            combo_rect = combo_surface.get_rect(center=self.ui_positions['combo'])
            surface.blit(combo_surface, combo_rect)
        
        # 绘制生命，使用心形图标
        lives = int(GameConfig.INITIAL_LIVES) - int(missed)
        heart_icon = resource_manager.load_image('heart.png')
        
        if heart_icon:
            # 调整心形图标大小
            heart_width, heart_height = heart_icon.get_size()
            scaled_heart = pygame.transform.scale(heart_icon, (30, 30))
            
            # 绘制多个心形图标表示生命值
            for i in range(lives):
                heart_x = self.ui_positions['missed'][0] + i * 40
                heart_y = self.ui_positions['missed'][1]
                surface.blit(scaled_heart, (heart_x, heart_y))
        else:
            # 降级方案：用艺术X表示
            missed_text = f"X " * lives
            missed_surface = self.font_manager.render_score_life_text(missed_text, GameConfig.RED)
            missed_rect = missed_surface.get_rect(topleft=self.ui_positions['missed'])
            surface.blit(missed_surface, missed_rect)
        
        # 绘制游戏时间
        time_left = max(0, game_duration - game_time)
        time_text = f"Time: {int(time_left)}s"
        time_surface = self.font_manager.render_text_normal(time_text, GameConfig.WHITE)
        time_rect = time_surface.get_rect(center=self.ui_positions['time'])
        surface.blit(time_surface, time_rect)
        
        # 绘制Logo
        if self.logo_image:
            logo_x = self.width // 2 - self.logo_image.get_width() // 2
            surface.blit(self.logo_image, (logo_x, 10))
    
    def draw_title_screen(self, surface):
        """
        绘制开始页面
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制开始按钮
        self.draw_start_button(surface)
        
        # 绘制退出按钮
        self.draw_quit_button(surface, 'title_screen_quit')
        
        # 绘制时间选择器
        self.draw_duration_selector(surface)
        
        # 绘制规则按钮
        self.draw_rules_button(surface)
    
    def draw_duration_selector(self, surface):
        """
        绘制游戏时长选择器
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制标签
        duration_label = self.font_manager.render_text_normal('Game Duration:', GameConfig.WHITE)
        surface.blit(duration_label, self.ui_positions['title_screen_duration'])
        
        # 时长选项
        duration_options = [30, 60, 90]
        duration_button_y = 110
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for i, duration in enumerate(duration_options):
            button_x = 50 + i * 90
            button_rect = pygame.Rect(button_x, duration_button_y, 80, 40)
            
            # 检查鼠标位置
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # 交互逻辑 - 无透明边框，仅使用颜色变化显示状态
            if duration == self.selected_duration:
                # 选中状态使用黄色
                text_color = GameConfig.GOLD
            elif is_hovered:
                # 鼠标悬停状态使用浅蓝色
                text_color = GameConfig.BLUE
                if mouse_pressed[0]:
                    self.selected_duration = duration
            else:
                # 正常状态使用白色
                text_color = GameConfig.WHITE
            
            # 绘制文本
            text = self.font_manager.render_text_normal(f'{duration}s', text_color)
            text_rect = text.get_rect(center=button_rect.center)
            surface.blit(text, text_rect)
    
    def draw_start_button(self, surface):
        """
        绘制开始按钮
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        button_x = self.width // 2 - 100
        button_y = self.height // 3 + 50
        rect = pygame.Rect(button_x, button_y, 200, 200)
        mouse_pos = pygame.mouse.get_pos()
        
        # 绘制按钮
        if rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                if self.start_button_click:
                    surface.blit(self.start_button_click, (button_x, button_y))
            else:
                if self.start_button_hover:
                    surface.blit(self.start_button_hover, (button_x, button_y))
        else:
            if self.start_button_image:
                surface.blit(self.start_button_image, (button_x, button_y))
    
    def draw_rules_button(self, surface):
        """
        绘制规则按钮
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        rect = pygame.Rect(self.ui_positions['title_screen_rules'][0], 
                         self.ui_positions['title_screen_rules'][1], 
                         160, 45)
        
        # 检查鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        
        # 无透明边框，仅使用颜色变化显示状态
        if is_hovered:
            # 鼠标悬停时使用黄色
            text_color = GameConfig.GOLD
        else:
            # 正常状态使用白色
            text_color = GameConfig.WHITE
        
        # 绘制文本
        text = self.font_manager.render_text_normal('Rules', text_color)
        surface.blit(text, (rect.x + 20, rect.y + 10))
        
        # 检查点击
        if is_hovered and pygame.mouse.get_pressed()[0]:
            self.show_rules = True
    
    def draw_quit_button(self, surface, position_key):
        """
        绘制退出按钮
        
        Args:
            surface (pygame.Surface): 绘制表面
            position_key (str): 位置键名
        """
        # 对于开始界面，将退出按钮放置于开始游戏按钮的正下方，确保沿同一垂直中轴对称
        if position_key == 'title_screen_quit':
            button_x = self.width // 2 - 45
            button_y = self.height // 3 + 280  
            rect = pygame.Rect(button_x, button_y, 160, 45)
        else:
            # 对于其他界面，使用原来的位置
            pos = self.ui_positions[position_key]
            rect = pygame.Rect(pos[0] - 80, pos[1] - 20, 160, 45)
        
        # 检查鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        
        # 无透明边框，仅使用颜色变化显示状态
        if is_hovered:
            # 鼠标悬停时使用红色
            text_color = GameConfig.RED
        else:
            # 正常状态使用白色
            text_color = GameConfig.WHITE
        
        # 绘制文本
        text = self.font_manager.render_text_normal('Quit', text_color)
        surface.blit(text, (rect.x + 20, rect.y + 10))
        
        # 检查点击
        if is_hovered and pygame.mouse.get_pressed()[0]:
            pygame.quit()
            exit()
    
    def draw_text_button(self, surface, text, x, y, width, height, hover_color=GameConfig.GOLD, normal_color=GameConfig.WHITE):
        """
        绘制文本按钮
        
        Args:
            surface (pygame.Surface): 绘制表面
            text (str): 按钮文本
            x (int): 按钮X坐标
            y (int): 按钮Y坐标
            width (int): 按钮宽度
            height (int): 按钮高度
            hover_color (tuple): 悬停时的颜色
            normal_color (tuple): 正常状态的颜色
            
        Returns:
            bool: 按钮是否被点击
        """
        rect = pygame.Rect(x, y, width, height)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        
        # 无透明边框，仅使用颜色变化显示状态
        if is_hovered:
            text_color = hover_color
        else:
            text_color = normal_color
        
        # 绘制文本
        button_text = self.font_manager.render_text_normal(text, text_color)
        surface.blit(button_text, (rect.x + 20, rect.y + 10))
        
        # 检查点击
        is_clicked = is_hovered and pygame.mouse.get_pressed()[0]
        return is_clicked
    
    def draw_rules_overlay(self, surface):
        """
        绘制规则覆盖层
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制半透明背景
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(GameConfig.BLACK)
        surface.blit(overlay, (0, 0))
        
        # 绘制规则文本
        rules = [
            "=== Game Rules ===",
            "[Cutting Method]",  # 移除主标题后的空行
            "Swipe your hand across the screen to cut fruits",
            "Watermelon: Requires a two-finger swipe",
            "Other fruits: Normal single-finger swipe works",
            "[Scoring]",
            "Watermelon: 20 points",
            "All other fruits: 10 points",      
            "[Combo System]",
            "Each consecutive fruit sliced increases combo",
            "Combo bonus: +5 points per combo",
            "Reset combo when fruit falls off screen",
            "[Bombs]",
            "Don't slice bombs (-1 life)",
            "[Lives]",
            "Initial lives: 3",
            "Lose 1 life when slicing bombs",
            "",
            "Click anywhere to close"
        ]
        
        y = 60
        for line in rules:
            color = GameConfig.GOLD if "===" in line else GameConfig.BLUE if "[" in line else GameConfig.WHITE
            
            # 根据文本类型使用不同的字体大小
            if "===" in line:
                text = self.font_manager.render_text(line, 40, color)  # 减小主标题字体大小
            elif "[" in line:
                text = self.font_manager.render_text_normal(line, color)
            else:
                text = self.font_manager.render_small_text(line, color)
            
            rect = text.get_rect(center=(self.width // 2, y))
            surface.blit(text, rect)
            y += 35  # 调整行间距，适应较小的字体
    
    def draw_game_over_screen(self, surface, score, max_combo, lives, end_reason):
        """
        绘制游戏结束界面
        
        Args:
            surface (pygame.Surface): 绘制表面
            score (int): 最终分数
            max_combo (int): 最大连击数
            lives (int): 剩余生命数
            end_reason (str): 结束原因
        """
        # 绘制最终分数
        score_text = f"Final Score: {score}"
        score_surface = self.font_manager.render_text_normal(score_text, GameConfig.WHITE)
        score_rect = score_surface.get_rect(center=(self.width // 2, self.height // 2 - 60))
        surface.blit(score_surface, score_rect)
        
        # 绘制结束原因
        reason_text = "TIME OVER" if end_reason == "time_over" else "DEAD"
        color = GameConfig.GOLD if end_reason == "time_over" else GameConfig.RED
        text = self.font_manager.render_title(reason_text, color)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, rect)
        
        # 绘制时长选择
        self.draw_duration_selector(surface)
        
        # 绘制new game按钮和quit按钮，在同一水平线上分居于两端
        button_y = self.height // 2 + 120
        
        # 绘制new game按钮（左侧）
        new_game_clicked = self.draw_text_button(surface, "New Game", 50, button_y, 160, 45)
        
        # 绘制quit按钮（右侧）
        quit_clicked = self.draw_text_button(surface, "Quit", self.width - 210, button_y, 160, 45, GameConfig.RED, GameConfig.WHITE)
        
        # 处理quit按钮点击
        if quit_clicked:
            import pygame
            pygame.quit()
            exit()
        
        return new_game_clicked
    
    def draw_ready_screen(self, surface):
        """
        绘制游戏准备界面
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制游戏标题
        title_text = "Fruit Ninja"
        title_surface = self.font_manager.render_title(title_text, GameConfig.WHITE)
        title_rect = title_surface.get_rect(center=self.ui_positions['ready_title'])
        surface.blit(title_surface, title_rect)
        
        # 绘制开始提示
        start_text = "Click to Start"
        start_surface = self.font_manager.render_subtitle(start_text, GameConfig.WHITE)
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
        title_surface = self.font_manager.render_title(title_text, GameConfig.WHITE)
        title_rect = title_surface.get_rect(center=self.ui_positions['pause_title'])
        surface.blit(title_surface, title_rect)
        
        # 绘制继续提示
        resume_text = "Press Space to Resume"
        resume_surface = self.font_manager.render_subtitle(resume_text, GameConfig.WHITE)
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
    
    def get_selected_duration(self):
        """
        获取选择的游戏时长
        
        Returns:
            int: 游戏时长（秒）
        """
        return self.selected_duration
    
    def set_show_rules(self, show):
        """
        设置是否显示规则
        
        Args:
            show (bool): 是否显示规则
        """
        self.show_rules = show
    
    def get_show_rules(self):
        """
        获取是否显示规则
        
        Returns:
            bool: 是否显示规则
        """
        return self.show_rules
