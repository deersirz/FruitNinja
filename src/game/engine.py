"""
游戏引擎模块
管理游戏主循环和协调各模块工作
"""

import pygame
import time
import threading
from game.factory import GameFactory
from game.config import GameConfig
from utils.resource import resource_manager
from utils.camera import Camera


class GameEngine:
    """
    游戏引擎类
    """
    def __init__(self, hand_detector, renderer, logger):
        """
        初始化游戏引擎
        
        Args:
            hand_detector (HandDetector): 手部检测器
            renderer (Renderer): 渲染器
            logger (Logger): 日志记录器
        """
        self.hand_detector = hand_detector
        self.renderer = renderer
        self.logger = logger
        
        # 初始化状态
        self.initializing = True
        self.init_complete = False
        self.init_progress = 0
        self.init_message = "Initializing game..."
        
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
        self.game_state = GameConfig.GAME_STATES['TITLE']  # TITLE, COUNTDOWN, PLAYING, GAME_OVER
        
        # 时间管理
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        
        # 游戏时长
        self.selected_duration = GameConfig.DEFAULT_GAME_DURATION
        
        # 倒计时
        self.countdown_start_time = 0
        
        # 初始化摄像头
        self.camera = None
        self.camera_preview_ready = False
        
        # 资源加载标志
        self.resources_loaded = False
        
        # 启动异步初始化线程
        self.init_thread = threading.Thread(target=self._async_init, daemon=True)
        self.init_thread.start()
    
    def _async_init(self):
        """
        异步初始化方法，在后台线程中执行耗时操作
        """
        # 添加初始化超时机制
        init_timeout = 10.0  # 初始化超时时间（秒）
        start_time = time.time()
        
        try:
            # 加载游戏资源
            self.init_message = "Loading game resources..."
            self.init_progress = 10
            self.load_resources()
            self.resources_loaded = True
            
            # 检查是否超时
            if time.time() - start_time > init_timeout:
                raise TimeoutError(f"Initialization timeout ({init_timeout} seconds)")
            
            # 初始化摄像头
            self.init_message = "Initializing camera..."
            self.init_progress = 30
            self.camera = Camera()
            
            # 检查是否超时
            if time.time() - start_time > init_timeout:
                raise TimeoutError(f"Initialization timeout ({init_timeout} seconds)")
            
            # 检查手部检测器状态
            self.init_message = "Initializing hand detector..."
            self.init_progress = 60
            self.check_hand_detector_status()
            
            # 检查是否超时
            if time.time() - start_time > init_timeout:
                raise TimeoutError(f"Initialization timeout ({init_timeout} seconds)")
            
            # 开始摄像头预热
            self.init_message = "Camera warming up..."
            self.init_progress = 80
            self.logger.log("Starting camera warmup...")
            self.start_camera_warmup()
            
            # 检查是否超时
            if time.time() - start_time > init_timeout:
                raise TimeoutError(f"初始化超时（{init_timeout}秒）")
            
            # 播放标题音乐
            self.play_music('happyfly.ogg')
            
            # 初始化完成
            self.init_message = "Initialization complete"
            self.init_progress = 100
            self.init_complete = True
            self.initializing = False
            self.logger.log("Game initialization complete, starting main loop...")
        except TimeoutError as e:
            self.logger.log(f"Initialization timeout: {e}", level="error")
            self.initializing = False
            self.init_complete = True
            self.init_message = "Initialization timeout, please check hardware connections"
            self.init_progress = 100
        except Exception as e:
            self.logger.log(f"Initialization error: {e}", level="error")
            self.initializing = False
            self.init_complete = True
            self.init_message = "Initialization error, please check logs"
            self.init_progress = 100
    
    def start_camera_warmup(self):
        """
        Start camera warmup process
        Actively capture frames to accelerate camera initialization and adjustment
        """
        self.logger.log("Camera warmup started...")
        
        # 减少预热帧数，加快初始化速度
        max_warmup_frames = 5
        warmup_timeout = 3.0  # 预热超时时间（秒）
        start_time = time.time()
        
        # 主动捕获几帧以加速摄像头预热
        for i in range(max_warmup_frames):
            # 检查是否超时
            if time.time() - start_time > warmup_timeout:
                self.logger.log(f"Camera warmup timeout ({warmup_timeout} seconds)", level="warning")
                break
            
            frame = self.camera.get_frame()
            if frame is not None:
                # 预热过程中不处理帧，仅让摄像头调整
                pass
            time.sleep(0.02)  # 减少延迟，加快初始化速度
        
        # 检查摄像头状态
        if self.camera.is_available():
            self.camera_preview_ready = True
            self.logger.log("Camera warmup completed, ready!")
        else:
            self.logger.log("Camera still unavailable after warmup, please check camera connection", level="warning")
    
    def render_camera_loading_status(self):
        """
        Render camera loading status
        """
        import pygame
        from game.config import GameConfig
        
        # 绘制加载状态背景
        overlay_surface = pygame.Surface((300, 100), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        
        # 计算位置（屏幕右下角）
        pos_x = self.renderer.width - 320
        pos_y = self.renderer.height - 120
        
        # 绘制背景
        self.renderer.screen.blit(overlay_surface, (pos_x, pos_y))
        
        # 绘制加载状态文本
        font = pygame.font.Font(None, 24)
        
        # 根据摄像头状态显示不同文本
        if not self.camera.is_opened:
            text = font.render("Initializing camera...", True, GameConfig.WHITE)
        elif self.camera.is_loading():
            progress = min(100, int((self.camera.warmup_frames / self.camera.max_warmup_frames) * 100))
            text = font.render(f"Camera warming up... {progress}%", True, GameConfig.WHITE)
        else:
            text = font.render("Camera ready", True, GameConfig.GREEN)
        
        # 绘制文本
        text_rect = text.get_rect(center=(pos_x + 150, pos_y + 50))
        self.renderer.screen.blit(text, text_rect)
    
    def load_resources(self):
        """
        加载游戏资源
        """
        # 加载音效
        self.cut_sound = resource_manager.load_sound('cut.mp3')
        
        # 加载水果图片
        self.fruit_images = {
            'apple': resource_manager.load_image('apple.png'),
            'banana': resource_manager.load_image('banana.png'),
            'peach': resource_manager.load_image('peach.png'),
            'watermelon': resource_manager.load_image('watermelon.png'),
            'strawberry': resource_manager.load_image('strawberry.png')
        }
        
        # 加载切割后的水果图片
        self.fruit_left_images = {
            'apple': resource_manager.load_image('apple-1.png'),
            'banana': resource_manager.load_image('banana-1.png'),
            'peach': resource_manager.load_image('peach-1.png'),
            'watermelon': resource_manager.load_image('watermelon-1.png'),
            'strawberry': resource_manager.load_image('strawberry-1.png')
        }
        
        self.fruit_right_images = {
            'apple': resource_manager.load_image('apple-2.png'),
            'banana': resource_manager.load_image('banana-2.png'),
            'peach': resource_manager.load_image('peach-2.png'),
            'watermelon': resource_manager.load_image('watermelon-2.png'),
            'strawberry': resource_manager.load_image('strawberry-2.png')
        }
        
        # 加载炸弹图片
        self.bomb_image = resource_manager.load_image('boom.png')
    
    def play_music(self, filename):
        """
        播放音乐
        
        Args:
            filename (str): 音乐文件名
        """
        if resource_manager.load_music(filename):
            resource_manager.play_music(-1)  # 循环播放
    
    def check_hand_detector_status(self):
        """
        检查手部检测器状态
        """
        if hasattr(self.hand_detector, 'is_initialized'):
            initialized = self.hand_detector.is_initialized()
            error_message = self.hand_detector.get_error_message() if hasattr(self.hand_detector, 'get_error_message') else ""
            status = self.hand_detector.get_status() if hasattr(self.hand_detector, 'get_status') else {}
            
            if initialized:
                version = status.get('version', 'unknown')
                self.logger.log(f"手部检测器初始化成功 (版本: {version})")
            else:
                self.logger.log(f"警告: 手部检测器未初始化: {error_message}", level="warning")
                print(f"手部识别加载失败: {error_message}")
                print("请检查以下内容:")
                print("1. MediaPipe 是否已安装: pip install mediapipe")
                print("2. 模型文件是否存在: src/gesture/hand_landmarker.task")
                print("3. 网络连接是否正常 (首次运行需要下载模型)")
        else:
            self.logger.log("警告: 手部检测器缺少状态检查方法", level="warning")
        
        # 保存手部检测器状态
        self.hand_detector_initialized = False
        if hasattr(self.hand_detector, 'is_initialized'):
            self.hand_detector_initialized = self.hand_detector.is_initialized()
        self.hand_detector_error = ""
        if hasattr(self.hand_detector, 'get_error_message'):
            self.hand_detector_error = self.hand_detector.get_error_message()
    
    def stop_music(self):
        """
        停止音乐
        """
        resource_manager.stop_music()
    
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
            if self.game_state == GameConfig.GAME_STATES['PLAYING']:
                self.update(dt, current_time)
            elif self.game_state == GameConfig.GAME_STATES['COUNTDOWN']:
                self.update_countdown(current_time)
            
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
                mouse_pos = pygame.mouse.get_pos()
                
                if self.game_state == GameConfig.GAME_STATES['TITLE']:
                    # 检查规则界面点击
                    if self.renderer.layout.get_show_rules():
                        self.renderer.layout.set_show_rules(False)
                    else:
                        # 检查开始按钮点击
                        start_button_rect = pygame.Rect(
                            GameConfig.WINDOW_WIDTH // 2 - 100,
                            GameConfig.WINDOW_HEIGHT // 2 + 100,
                            200,
                            200
                        )
                        if start_button_rect.collidepoint(mouse_pos):
                            self.start_countdown()
                elif self.game_state == GameConfig.GAME_STATES['GAME_OVER']:
                    # 检查开始按钮点击
                    start_button_rect = pygame.Rect(
                        GameConfig.WINDOW_WIDTH // 2 - 100,
                        GameConfig.WINDOW_HEIGHT // 2 + 100,
                        200,
                        200
                    )
                    if start_button_rect.collidepoint(mouse_pos):
                        self.reset_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == GameConfig.GAME_STATES['PLAYING']:
                        self.pause_game()
                    elif self.game_state == 'paused':
                        self.resume_game()
    
    def update_countdown(self, current_time):
        """
        更新倒计时
        
        Args:
            current_time (float): 当前时间
        """
        elapsed = current_time - self.countdown_start_time
        if elapsed >= 3:
            self.start_game()
    
    def update(self, dt, current_time):
        """
        更新游戏状态
        
        Args:
            dt (float): 时间步长（秒）
            current_time (float): 当前时间（秒）
        """
        # 检查摄像头是否初始化完成
        if self.camera is not None and self.camera.is_available():
            # 获取摄像头帧
            frame = self.camera.get_frame()
            if frame is not None:
                try:
                    # 检测手部
                    detection_result = self.hand_detector.detect_hands(frame)
                    
                    # 更新手势跟踪
                    self.gesture_tracker.update_landmarks(detection_result['landmarks'])
                    
                    # 保存当前帧和手部关键点，用于渲染摄像头预览
                    self.current_frame = frame
                    self.current_hand_landmarks = detection_result['landmarks']
                except Exception:
                    # 静默处理异常，避免影响游戏流畅度
                    pass
            else:
                # 摄像头不可用，清空帧和关键点
                self.current_frame = None
                self.current_hand_landmarks = []
        else:
            # 摄像头未初始化，清空帧和关键点
            self.current_frame = None
            self.current_hand_landmarks = []
        
        # 更新轨迹点的透明度，实现动态消散效果
        self.gesture_tracker.update_trajectory_alpha(dt)
        
        # 更新特效
        self.renderer.effects_manager.update(dt)
        
        # 检测挥砍动作
        if self.gesture_mapper.is_swipe():
            # 获取平滑后的手势轨迹
            trajectory = self.gesture_tracker.get_smooth_trajectory()
            
            # 获取中指轨迹
            middle_finger_trajectory = self.gesture_tracker.get_middle_finger_trajectory()
            
            # 检测碰撞
            collided_fruits = self.collision_detector.detect_multiple_collisions(
                trajectory, middle_finger_trajectory, self.fruit_manager.get_fruits()
            )
            
            # 处理碰撞
            for fruit in collided_fruits:
                if not fruit.sliced:
                    fruit.slice(current_time)
                    
                    # 检查是否是炸弹
                    if fruit.type == 'bomb':
                        # 炸弹切割惩罚：减少1点生命值
                        self.score_manager.increment_missed_fruits()
                        print("切割到炸弹！减少1点生命值")
                    else:
                        # 正常水果：更新分数
                        self.score_manager.update_score(fruit)
                        
                        # 播放切割音效
                        if self.cut_sound:
                            self.cut_sound.play()
                    
                    # 创建高质量的水果切割特效
                    # 计算切割方向向量
                    if len(self.gesture_tracker.get_smooth_trajectory()) >= 2:
                        trajectory = self.gesture_tracker.get_smooth_trajectory()
                        last_point = trajectory[-1]
                        second_last_point = trajectory[-2]
                        dx = last_point['x'] - second_last_point['x']
                        dy = last_point['y'] - second_last_point['y']
                        # 归一化方向向量
                        length = (dx**2 + dy**2)**0.5
                        if length > 0:
                            slice_direction = (dx / length, dy / length)
                        else:
                            slice_direction = (1, 0)
                    else:
                        slice_direction = (1, 0)
                    
                    # 调用新的水果切割特效方法
                    self.renderer.effects_manager.create_fruit_slice_effect(
                        fruit.x, fruit.y, fruit.color, fruit.type, slice_direction
                    )
        
        # 更新水果管理器
        self.fruit_manager.update(dt, current_time, self.physics_engine)
        
        # 检查并处理超出屏幕的水果（移除掉落惩罚）
        for fruit in self.fruit_manager.get_fruits()[:]:
            if fruit.is_off_screen() and not fruit.sliced:
                # 移除水果，但不移除生命值
                self.fruit_manager.remove_fruit(fruit)
        
        # 更新分数管理器
        self.score_manager.update_game_time(dt)
        
        # 检查游戏是否结束
        if self.score_manager.is_game_over():
            self.end_game('time_over')
    
    def render(self):
        """
        渲染游戏画面
        """
        # 清除屏幕
        self.renderer.clear()
        
        # 绘制背景
        self.renderer.render_bg()

        # 显示初始化进度
        if self.initializing:
            self.render_init_progress()
            return

        # 根据游戏状态渲染
        if self.game_state == GameConfig.GAME_STATES['TITLE']:
            self.renderer.render_title_screen()
            
            # 显示摄像头加载状态
            if not self.camera_preview_ready:
                self.render_camera_loading_status()
        elif self.game_state == GameConfig.GAME_STATES['COUNTDOWN']:
            self.renderer.render_countdown_screen(5 - int(time.time() - self.countdown_start_time))
            
            # 显示摄像头加载状态
            if not self.camera_preview_ready:
                self.render_camera_loading_status()
        elif self.game_state == GameConfig.GAME_STATES['PLAYING']:
            # 渲染水果
            fruits = self.fruit_manager.get_fruits()
            self.renderer.render_fruits(fruits)
            
            # 渲染UI
            score = self.score_manager.get_score()
            combo = self.score_manager.get_combo()
            missed = self.score_manager.get_missed_fruits()
            game_time = self.score_manager.get_game_time()
            
            self.renderer.render_ui(score, combo, missed, game_time)
        elif self.game_state == 'paused':
            self.renderer.render_pause_screen()
        elif self.game_state == GameConfig.GAME_STATES['GAME_OVER']:
            score = self.score_manager.get_score()
            max_combo = self.score_manager.get_max_combo()
            lives = GameConfig.INITIAL_LIVES - self.score_manager.get_missed_fruits()
            self.renderer.render_game_over_screen(score, max_combo, lives, self.end_reason)
            self.renderer.clear_effects()
        
        # 渲染摄像头预览窗口（仅在游戏正式开始后且摄像头准备就绪时显示）
        if (self.game_state == GameConfig.GAME_STATES['PLAYING'] and 
            self.camera_preview_ready and 
            hasattr(self, 'current_frame') and 
            self.current_frame is not None):
            hand_landmarks = getattr(self, 'current_hand_landmarks', None)
            self.renderer.render_camera_preview(self.current_frame, hand_landmarks)
        
        # 渲染特效
        self.renderer.render_effects()
        
        # 渲染手势轨迹（在最上层）
        if self.game_state == GameConfig.GAME_STATES['PLAYING']:
            trajectory = self.gesture_tracker.get_smooth_trajectory()
            self.renderer.render_gesture_trajectory(trajectory)
        
        # 更新显示
        self.renderer.update_display()
    
    def render_init_progress(self):
        """
        渲染初始化界面
        """
        import pygame
        from game.config import GameConfig
        from utils.resource import resource_manager
        
        # 使用title.png作为背景
        title_image = resource_manager.load_image('title.png')
        if title_image:
            # 计算图像和窗口的宽高比
            img_width, img_height = title_image.get_size()
            window_width, window_height = self.renderer.width, self.renderer.height
            
            # 计算最佳缩放比例，保持宽高比
            scale = min(window_width / img_width, window_height / img_height)
            
            # 计算缩放后的图像尺寸
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 缩放图像
            scaled_title = pygame.transform.scale(title_image, (new_width, new_height))
            
            # 计算居中位置
            x = (window_width - new_width) // 2
            y = (window_height - new_height) // 2
            
            # 绘制黑色背景
            self.renderer.screen.fill(GameConfig.BLACK)
            
            # 居中绘制背景图像
            self.renderer.screen.blit(scaled_title, (x, y))
        else:
            # 如果背景图像加载失败，使用黑色背景
            self.renderer.screen.fill(GameConfig.BLACK)
        
        # 绘制加载状态文本
        font = pygame.font.Font(None, 36)
        progress_text = font.render(f"{self.init_message}", True, GameConfig.WHITE)
        text_rect = progress_text.get_rect(center=(self.renderer.width // 2, self.renderer.height // 2))
        self.renderer.screen.blit(progress_text, text_rect)
        
        # 绘制游戏相关说明文本
        instructions = [
            "Welcome to Fruit Ninja!",
            "Please ensure your camera is connected and working properly",
            "Use gestures to slice fruits on the screen",
            "Avoid bombs, otherwise you will lose lives",
            "Are you ready to start the game?"
        ]
        
        # 绘制说明文本
        instruction_font = pygame.font.Font(None, 24)
        y_offset = 100
        for instruction in instructions:
            instruction_text = instruction_font.render(instruction, True, GameConfig.GOLD)
            instruction_rect = instruction_text.get_rect(center=(self.renderer.width // 2, self.renderer.height // 2 + y_offset))
            self.renderer.screen.blit(instruction_text, instruction_rect)
            y_offset += 40
        
        # 更新显示
        self.renderer.update_display()
    
    def start_countdown(self):
        """
        开始倒计时
        """
        self.game_state = GameConfig.GAME_STATES['COUNTDOWN']
        self.countdown_start_time = time.time()
        self.stop_music()
        self.logger.log("Starting countdown")
    
    def start_game(self):
        """
        开始游戏
        """
        self.game_state = GameConfig.GAME_STATES['PLAYING']
        self.score_manager.reset()
        self.fruit_manager.clear_fruits()
        
        # 设置游戏时长
        self.score_manager.set_game_duration(self.renderer.layout.get_selected_duration())
        
        # 播放游戏音乐
        self.play_music('bg.mp3')
        
        self.logger.log(f"游戏开始，时长：{self.renderer.layout.get_selected_duration()}秒")
    
    def pause_game(self):
        """
        暂停游戏
        """
        self.game_state = 'paused'
        self.logger.log("Game paused")
    
    def resume_game(self):
        """
        恢复游戏
        """
        self.game_state = GameConfig.GAME_STATES['PLAYING']
        self.logger.log("Game resumed")
    
    def end_game(self, reason):
        """
        结束游戏
        
        Args:
            reason (str): 结束原因
        """
        self.game_state = GameConfig.GAME_STATES['GAME_OVER']
        self.end_reason = reason
        self.stop_music()
        score = self.score_manager.get_score()
        self.logger.log(f"游戏结束，得分：{score}，原因：{reason}")
    
    def reset_game(self):
        """
        重置游戏
        """
        self.game_state = GameConfig.GAME_STATES['TITLE']
        self.score_manager.reset()
        self.fruit_manager.clear_fruits()
        self.play_music('happyfly.ogg')
        self.logger.log("Game reset")
    
    def quit(self):
        """
        退出游戏
        """
        self.running = False
        self.stop_music()
        
        # 释放摄像头资源
        if hasattr(self, 'camera') and self.camera:
            self.camera.release()
            self.logger.log("Camera resources released")
        
        self.logger.log("Game exited")
