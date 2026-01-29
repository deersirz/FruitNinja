"""
渲染器模块
负责游戏的渲染逻辑
"""

import pygame
import cv2
from game.config import GameConfig
from ui.effects import EffectsManager
from ui.layout import UILayout
from utils.resource import resource_manager


class Renderer:
    """
    渲染器类
    """
    def __init__(self, width=GameConfig.WINDOW_WIDTH, height=GameConfig.WINDOW_HEIGHT, hand_detector=None):
        """
        初始化渲染器
        
        Args:
            width (int): 屏幕宽度
            height (int): 屏幕高度
            hand_detector (HandDetector): 手部检测器实例
        """
        # 初始化PyGame显示
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(GameConfig.WINDOW_TITLE)
        
        # 保存手部检测器实例
        self.hand_detector = hand_detector
        
        # 初始化特效管理器
        self.effects_manager = EffectsManager()
        
        # 初始化布局管理器
        self.layout = UILayout(width, height)
        
        # 背景色
        self.background_color = GameConfig.BACKGROUND_COLOR
        
        # 预创建轨迹绘制的临时Surface，避免频繁创建和销毁
        self.trajectory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 加载水果图片
        self.load_fruit_images()
    
    def load_fruit_images(self):
        """
        加载水果图片资源
        """
        # 水果图片映射
        self.fruit_images = {}
        self.fruit_left_images = {}
        self.fruit_right_images = {}
        
        # 水果类型与图片文件名的映射
        fruit_mapping = {
            'apple': 'apple.png',
            'banana': 'banana.png',
            'peach': 'peach.png',
            'watermelon': 'watermelon.png',
            'strawberry': 'strawberry.png',
            'bomb': 'boom.png'
        }
        
        # 加载完整水果图片
        for fruit_type, filename in fruit_mapping.items():
            image = resource_manager.load_image(filename)
            if image:
                # 缩放图片以适应水果大小（增大尺寸）
                if fruit_type == 'bomb':
                    # 炸弹使用不同的大小
                    scaled_image = pygame.transform.scale(image, (90, 90))
                else:
                    scaled_image = pygame.transform.scale(image, (80, 80))
                self.fruit_images[fruit_type] = scaled_image
            else:
                print(f"Warning: Failed to load fruit image for {fruit_type}")
                self.fruit_images[fruit_type] = None
        
        # 加载切割后的水果图片
        for fruit_type, filename in fruit_mapping.items():
            if fruit_type != 'bomb':  # 炸弹不需要切割后的图片
                left_image = resource_manager.load_image(f"{fruit_type.split('.')[0]}-1.png")
                right_image = resource_manager.load_image(f"{fruit_type.split('.')[0]}-2.png")
                
                if left_image:
                    self.fruit_left_images[fruit_type] = left_image
                else:
                    self.fruit_left_images[fruit_type] = None
                
                if right_image:
                    self.fruit_right_images[fruit_type] = right_image
                else:
                    self.fruit_right_images[fruit_type] = None
    
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
                # 使用图片渲染水果
                fruit_image = self.fruit_images.get(fruit.type)
                if fruit_image:
                    # 计算图片位置（居中显示）
                    image_rect = fruit_image.get_rect()
                    
                    # 调整香蕉图形大小：高度减少50%，保持宽度不变
                    if fruit.type == 'banana':
                        original_width = image_rect.width
                        original_height = image_rect.height
                        new_height = original_height // 2
                        # 保持宽度不变，只减少高度
                        resized_image = pygame.transform.scale(fruit_image, (original_width, new_height))
                        image_rect = resized_image.get_rect()
                        image_rect.center = (int(fruit.x), int(fruit.y))
                        self.screen.blit(resized_image, image_rect)
                    else:
                        # 其他水果正常渲染
                        image_rect.center = (int(fruit.x), int(fruit.y))
                        self.screen.blit(fruit_image, image_rect)
                else:
                    # 降级方案：使用几何图形绘制
                    pygame.draw.circle(self.screen, fruit.color, 
                                     (int(fruit.x), int(fruit.y)), fruit.radius)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (int(fruit.x), int(fruit.y)), fruit.radius, 2)
            else:
                # 绘制切割后的水果
                left_image = self.fruit_left_images.get(fruit.type)
                right_image = self.fruit_right_images.get(fruit.type)
                
                if left_image and right_image:
                    # 计算左右半部分的位置
                    left_rect = left_image.get_rect()
                    right_rect = right_image.get_rect()
                    
                    # 根据水果类型调整切片方向和位置
                    if fruit.type == 'banana':
                        # 香蕉是长条形水果，切片应该横向摆放
                        # 旋转切片图片90度
                        rotated_left = pygame.transform.rotate(left_image, 90)
                        rotated_right = pygame.transform.rotate(right_image, 90)
                        
                        # 重新获取旋转后的矩形
                        left_rect = rotated_left.get_rect()
                        right_rect = rotated_right.get_rect()
                        
                        # 调整偏移量，确保横向正确显示
                        offset = 20  # 香蕉切片的横向偏移量
                        left_rect.center = (int(fruit.x) - offset, int(fruit.y))
                        right_rect.center = (int(fruit.x) + offset, int(fruit.y))
                        
                        # 绘制旋转后的切片
                        self.screen.blit(rotated_left, left_rect)
                        self.screen.blit(rotated_right, right_rect)
                    else:
                        # 其他水果（如苹果、草莓等圆形水果）正常渲染
                        # 调整切片水果的位置计算，适应宽度变化
                        # 根据水果类型调整偏移量
                        if fruit.type == 'watermelon':
                            offset = 16  # 西瓜切片的偏移量
                        elif fruit.type == 'peach':
                            offset = 15  # 桃子切片的偏移量
                        else:
                            offset = 14  # 其他水果的默认偏移量
                        
                        left_rect.center = (int(fruit.x) - offset, int(fruit.y))
                        right_rect.center = (int(fruit.x) + offset, int(fruit.y))
                        
                        self.screen.blit(left_image, left_rect)
                        self.screen.blit(right_image, right_rect)
                else:
                    # 降级方案：绘制简化的切割效果
                    pygame.draw.circle(self.screen, fruit.color, 
                                     (int(fruit.x) - 10, int(fruit.y)), fruit.radius // 2)
                    pygame.draw.circle(self.screen, fruit.color, 
                                     (int(fruit.x) + 10, int(fruit.y)), fruit.radius // 2)
    
    def render_gesture_trajectory(self, trajectory):
        """
        渲染手势轨迹
        
        Args:
            trajectory (list): 手势轨迹点列表
        """
        if trajectory and len(trajectory) >= 2:
            # 清空预创建的轨迹Surface
            self.trajectory_surface.fill((0, 0, 0, 0))
            
            # 限制轨迹点数量，避免过多点影响性能
            max_render_points = 30  # 增加最大渲染点数量，支持平滑曲线
            if len(trajectory) > max_render_points:
                # 均匀采样轨迹点
                step = len(trajectory) // max_render_points
                rendered_trajectory = trajectory[::step]
            else:
                rendered_trajectory = trajectory
            
            # 批量绘制平滑轨迹线
            for i in range(len(rendered_trajectory) - 1):
                p1 = rendered_trajectory[i]
                p2 = rendered_trajectory[i+1]
                
                # 计算当前段的平均透明度
                avg_alpha = (p1.get('alpha', 1.0) + p2.get('alpha', 1.0)) / 2
                
                # 调整透明度曲线，使其更自然
                alpha_factor = avg_alpha ** 1.5  # 非线性透明度衰减
                
                # 创建带有透明度的颜色，从亮白色过渡到淡白色
                brightness = int(200 + 55 * avg_alpha)  # 亮度随透明度变化
                color_with_alpha = (brightness, brightness, brightness, int(alpha_factor * 150))  # 减少透明度，提高性能
                
                # 计算线宽，随透明度变化
                base_width = 2  # 基础线宽
                line_width = max(base_width, int(base_width * alpha_factor))
                
                # 绘制轨迹线（使用直线连接，因为平滑已经在轨迹生成时处理）
                pygame.draw.line(self.trajectory_surface, color_with_alpha, 
                               (int(p1['x']), int(p1['y'])), (int(p2['x']), int(p2['y'])), line_width)
                
                # 绘制轨迹的发光效果（简化版本，提高性能）
                if alpha_factor > 0.5:  # 只对透明度较高的部分绘制发光效果
                    glow_color = (255, 255, 255, int(alpha_factor * 30))  # 减少发光效果的透明度，提高性能
                    glow_width = line_width * 2
                    pygame.draw.line(self.trajectory_surface, glow_color, 
                                   (int(p1['x']), int(p1['y'])), (int(p2['x']), int(p2['y'])), glow_width)
            
            # 将轨迹Surface一次性绘制到主屏幕
            self.screen.blit(self.trajectory_surface, (0, 0))
    
    def render_bg(self):
        """
        xuan ran bei jing
        """
        self.layout.draw_bg(self.screen)
        pass

    def render_ui(self, score, combo, missed, game_time, game_duration):
        """
        渲染UI元素
        
        Args:
            score (int): 当前分数
            combo (int): 当前连击数
            missed (int): 错过的水果数
            game_time (float): 游戏时间
            game_duration (int): 游戏时长
        """
        self.layout.draw_ui(self.screen, score, combo, missed, game_time, game_duration)
    
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
    
    def render_title_screen(self):
        """
        渲染开始页面
        """
        self.layout.draw_title_screen(self.screen)
        
        # 绘制规则覆盖层
        if self.layout.get_show_rules():
            self.layout.draw_rules_overlay(self.screen)
    
    def render_countdown_screen(self, countdown):
        """
        渲染倒计时界面
        
        Args:
            countdown (int): 倒计时秒数
        """
        # 绘制背景
        self.layout.draw_bg(self.screen)
        
        # 绘制倒计时文本
        from ui.fonts import FontManager
        font_manager = FontManager()
        font = font_manager.get_font(100)
        text = font.render(f'Game Start {countdown}...', True, GameConfig.WHITE)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)
    
    def render_game_over_screen(self, score, max_combo, lives, end_reason):
        """
        渲染游戏结束界面
        
        Args:
            score (int): 最终分数
            max_combo (int): 最大连击数
            lives (int): 剩余生命数
            end_reason (str): 结束原因
        """
        self.layout.draw_game_over_screen(self.screen, score, max_combo, lives, end_reason)
    
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
    
    def render_camera_preview(self, frame, hand_landmarks=None):
        """
        渲染摄像头预览窗口
        
        Args:
            frame (numpy.ndarray): 摄像头帧
            hand_landmarks (list, optional): 手部关键点列表
        """
        if frame is not None:
            try:
                # 调整帧大小（适配旋转后的画面比例）
                preview_size = (100, 133)  # 减小预览窗口大小，提高性能
                resized_frame = cv2.resize(frame, preview_size)
                
                # 移除所有识别点，确保干净的视觉呈现
                
                # 转换为pygame表面
                frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(frame_rgb)
                # 移除固定水平翻转，改为使用Camera类的翻转状态
                
                # 绘制预览窗口
                preview_pos = self.layout.ui_positions['camera_preview']
                self.screen.blit(frame_surface, preview_pos)
            except Exception as e:
                print(f"Error rendering camera preview: {e}")
