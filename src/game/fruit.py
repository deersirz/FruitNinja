"""
水果模块
define水果对象和水果管理器
"""

import random
import math
from game.config import GameConfig
from game.physics import PhysicsEngine


class Fruit:
    """
    水果类
    """
    def __init__(self, x, y, fruit_type):
        """
        初始化水果对象
        
        Args:
            x (float): 水果x坐标
            y (float): 水果y坐标
            fruit_type (str): 水果类型
        """
        self.x = x
        self.y = y
        self.radius = GameConfig.FRUIT_RADIUS
        self.type = fruit_type
        self.color = GameConfig.FRUIT_COLORS.get(fruit_type, (255, 255, 255))
        
        # 随机速度和方向
        angle = random.uniform(-45, 45)
        speed = GameConfig.FRUIT_VELOCITY
        self.velocity_x = speed * math.cos(math.radians(angle))
        self.velocity_y = -speed * math.sin(math.radians(angle))
        
        # 随机角速度
        self.angular_velocity = random.uniform(-GameConfig.FRUIT_ANGULAR_VELOCITY, 
                                               GameConfig.FRUIT_ANGULAR_VELOCITY)
        self.rotation = 0
        
        self.sliced = False
        self.sliced_time = 0
        
    def update(self, dt, physics_engine=None):
        """
        更新水果状态
        
        Args:
            dt (float): 时间步长（秒）
            physics_engine (PhysicsEngine, optional): 物理引擎实例
        """
        if not self.sliced:
            if physics_engine:
                # 使用物理引擎更新
                physics_engine.apply_physics(self, dt)
            else:
                # 内置物理更新（备用）
                # 更新位置
                self.x += self.velocity_x * dt
                self.y += self.velocity_y * dt
                
                # 应用重力
                self.velocity_y += GameConfig.GRAVITY * dt
                
                # 更新旋转
                self.rotation += self.angular_velocity * dt
            
    def draw(self, surface):
        """
        绘制水果
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 这里将在renderer.py中实现具体的绘制逻辑
        pass
    
    def slice(self, slice_time=0):
        """
        标记水果为已切割
        
        Args:
            slice_time (float, optional): 切割时间（秒）
        """
        self.sliced = True
        self.sliced_time = slice_time
        
    def is_off_screen(self):
        """
        判断水果是否超出屏幕
        
        Returns:
            bool: 是否超出屏幕
        """
        return (self.x < -self.radius or 
                self.x > GameConfig.WINDOW_WIDTH + self.radius or 
                self.y > GameConfig.WINDOW_HEIGHT + self.radius)


class FruitManager:
    """
    水果管理器类
    """
    def __init__(self, spawn_rate=GameConfig.FRUIT_SPAWN_RATE):
        """
        初始化水果管理器
        
        Args:
            spawn_rate (float): 水果生成频率（秒）
        """
        self.fruits = []
        self.spawn_rate = spawn_rate
        self.last_spawn_time = 0
        self.fruit_types = GameConfig.FRUIT_TYPES
        
    def update(self, dt, current_time, physics_engine=None):
        """
        更新水果管理器状态
        
        Args:
            dt (float): 时间步长（秒）
            current_time (float): 当前时间（秒）
            physics_engine (PhysicsEngine, optional): 物理引擎实例
        """
        # 生成新水果
        if current_time - self.last_spawn_time > self.spawn_rate:
            self.spawn_fruit()
            self.last_spawn_time = current_time
        
        # 更新水果状态
        for fruit in self.fruits[:]:
            fruit.update(dt, physics_engine)
            
            # 移除已切割的水果（延迟移除，以便特效显示）
            if fruit.sliced and current_time - fruit.sliced_time > 1.0:
                self.fruits.remove(fruit)
    
    def spawn_fruit(self):
        """
        生成新水果
        """
        # 随机位置（屏幕底部）
        x = random.randint(GameConfig.FRUIT_RADIUS, 
                          GameConfig.WINDOW_WIDTH - GameConfig.FRUIT_RADIUS)
        y = GameConfig.WINDOW_HEIGHT
        
        # 随机水果类型
        fruit_type = random.choice(self.fruit_types)
        
        # 创建水果对象
        fruit = Fruit(x, y, fruit_type)
        self.fruits.append(fruit)
    
    def get_fruits(self):
        """
        获取水果列表
        
        Returns:
            list: 水果列表
        """
        return self.fruits
    
    def remove_fruit(self, fruit):
        """
        移除水果
        
        Args:
            fruit (Fruit): 要移除的水果
        """
        if fruit in self.fruits:
            self.fruits.remove(fruit)
    
    def clear_fruits(self):
        """
        清空所有水果
        """
        self.fruits.clear()



