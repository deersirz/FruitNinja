"""
游戏引擎模块
管理游戏主循环和协调各模块工作
"""

import pygame
import time
from game.factory import GameFactory
from game.config import GameConfig


class GameEngine:
    """
    游戏引擎类
    """
    def __init__(self, hand_detector, renderer, logger):
    #def __init__(self, hand_detector, renderer, audio_manager, logger):
        """
        初始化游戏引擎
        
        Args:
            hand_detector (HandDetector): 手部检测器
            renderer (Renderer): 渲染器
            audio_manager (AudioManager): 音频管理器
            logger (Logger): 日志记录器
        """
        self.hand_detector = hand_detector
        self.renderer = renderer
        #self.audio_manager = audio_manager
        self.logger = logger
        
        # 使用游戏工厂创建所有模块
        self.factory = GameFactory()
        modules = self.factory.create_all_modules()
        
        # 初始化游戏模块
        self.fruit_manager = modules['fruit_manager']
        self.score_manager = modules['score_manager']
        self.collision_detector = modules['collision_detector']
        self.physics_engine = modules['physics_engine']
        
        # 初始化手势模块
        self.gesture_tracker = modules['gesture_tracker']
        self.gesture_mapper = modules['gesture_mapper']
        
        # 游戏状态
        self.running = False
        self.game_state = 'ready'  # ready, playing, paused, game_over
        
        # 时间管理
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        
    def run(self):
        """
        游戏主循环
        """
        self.running = True
        
        while self.running:
            # 计算时间步长
            current_time = time.time()
            dt = min(current_time - self.last_time, 0.1)  # 限制最大时间步长
            self.last_time = current_time
            
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            if self.game_state == 'playing':
                self.update(dt, current_time)
            
            # 渲染游戏画面
            self.render()
            
            # 控制帧率
            self.clock.tick(GameConfig.FPS)
        
    def handle_events(self):
        """
        处理游戏事件
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == 'ready':
                    self.start_game()
                elif self.game_state == 'game_over':
                    self.reset_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == 'playing':
                        self.pause_game()
                    elif self.game_state == 'paused':
                        self.resume_game()
    
    def update(self, dt, current_time):
        """
        更新游戏状态
        
        Args:
            dt (float): 时间步长（秒）
            current_time (float): 当前时间（秒）
        """
        # 获取摄像头帧
        frame = self.hand_detector.get_frame()
        if frame is not None:
            # 检测手部
            detection_result = self.hand_detector.detect_hands(frame)
            
            # 更新手势跟踪
            self.gesture_tracker.update_landmarks(detection_result['landmarks'])
            
            # 检测挥砍动作
            if self.gesture_mapper.is_swipe():
                # 获取手势轨迹
                trajectory = self.gesture_tracker.get_trajectory()
                
                # 检测碰撞
                collided_fruits = self.collision_detector.detect_multiple_collisions(
                    trajectory, self.fruit_manager.get_fruits()
                )
                
                # 处理碰撞
                for fruit in collided_fruits:
                    if not fruit.sliced:
                        fruit.slice(current_time)
                        self.score_manager.update_score(fruit)
                        #self.audio_manager.play_sound('slice')
                        
                        # 创建切割特效
                        self.renderer.create_slice_effect(fruit.x, fruit.y, fruit.color)
        
        # 更新水果管理器
        self.fruit_manager.update(dt, current_time, self.physics_engine)
        
        # 检查并处理超出屏幕的水果
        for fruit in self.fruit_manager.get_fruits()[:]:
            if fruit.is_off_screen() and not fruit.sliced:
                self.score_manager.increment_missed_fruits()
                self.fruit_manager.remove_fruit(fruit)
        
        # 更新分数管理器
        self.score_manager.update_game_time(dt)
        
        # 检查游戏是否结束
        if self.score_manager.is_game_over():
            self.end_game()
    
    def render(self):
        """
        渲染游戏画面
        """
        # 清除屏幕
        self.renderer.clear()
        
        # 根据游戏状态渲染
        if self.game_state == 'ready':
            self.renderer.render_ready_screen()
        elif self.game_state == 'playing':
            # 渲染水果
            fruits = self.fruit_manager.get_fruits()
            self.renderer.render_fruits(fruits)
            
            # 渲染手势轨迹
            trajectory = self.gesture_tracker.get_trajectory()
            self.renderer.render_gesture_trajectory(trajectory)
            
            # 渲染UI
            score = self.score_manager.get_score()
            combo = self.score_manager.get_combo()
            missed = self.score_manager.get_missed_fruits()
            game_time = self.score_manager.get_game_time()
            
            self.renderer.render_ui(score, combo, missed, game_time)
        elif self.game_state == 'paused':
            self.renderer.render_pause_screen()
        elif self.game_state == 'game_over':
            score = self.score_manager.get_score()
            max_combo = self.score_manager.get_max_combo()
            self.renderer.render_game_over_screen(score, max_combo)
            self.renderer.clear_effects()
        
        # 渲染特效
        self.renderer.render_effects()
        
        # 更新显示
        self.renderer.update_display()
    
    def start_game(self):
        """
        开始游戏
        """
        self.game_state = 'playing'
        self.score_manager.reset()
        self.fruit_manager.clear_fruits()
        #self.audio_manager.play_sound('start')
        self.logger.log("游戏开始")
    
    def pause_game(self):
        """
        暂停游戏
        """
        self.game_state = 'paused'
        #self.audio_manager.play_sound('pause')
        self.logger.log("游戏暂停")
    
    def resume_game(self):
        """
        恢复游戏
        """
        self.game_state = 'playing'
        # self.audio_manager.play_sound('resume')
        self.logger.log("游戏恢复")
    
    def end_game(self):
        """
        结束游戏
        """
        self.game_state = 'game_over'
        # self.audio_manager.play_sound('game_over')
        score = self.score_manager.get_score()
        self.logger.log(f"游戏结束，得分：{score}")
    
    def reset_game(self):
        """
        重置游戏
        """
        self.game_state = 'ready'
        self.score_manager.reset()
        self.fruit_manager.clear_fruits()
        self.logger.log("游戏重置")
    
    def quit(self):
        """
        退出游戏
        """
        self.running = False
        self.logger.log("游戏退出")
