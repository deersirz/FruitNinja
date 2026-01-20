"""
视觉效果模块
管理游戏中的视觉特效
"""

import pygame
import random
import math


class Particle:
    """
    粒子类
    """
    def __init__(self, x, y, color, velocity, lifetime):
        """
        初始化粒子
        
        Args:
            x (float): 初始x坐标
            y (float): 初始y坐标
            color (tuple): 粒子颜色
            velocity (tuple): 粒子速度 (vx, vy)
            lifetime (float): 粒子生命周期（秒）
        """
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]
        self.lifetime = lifetime
        self.alive = True
        self.age = 0
        self.size = random.randint(3, 6)
    
    def update(self, dt):
        """
        更新粒子状态
        
        Args:
            dt (float): 时间步长（秒）
        """
        if self.alive:
            # 更新位置
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # 应用重力
            self.velocity_y += 200 * dt
            
            # 更新年龄
            self.age += dt
            
            # 检查是否死亡
            if self.age >= self.lifetime:
                self.alive = False
    
    def draw(self, surface):
        """
        绘制粒子
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        if self.alive:
            # 计算透明度
            alpha = int(255 * (1 - self.age / self.lifetime))
            color = (*self.color, alpha)
            
            # 创建临时表面
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            
            # 绘制到主表面
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))


class SliceEffect:
    """
    切割效果类
    """
    def __init__(self, x, y, color):
        """
        初始化切割效果
        
        Args:
            x (float): 切割位置x坐标
            y (float): 切割位置y坐标
            color (tuple): 切割效果颜色
        """
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 0.5
        self.alive = True
        self.age = 0
        self.length = 80
        self.thickness = 3
    
    def update(self, dt):
        """
        更新切割效果
        
        Args:
            dt (float): 时间步长（秒）
        """
        if self.alive:
            self.age += dt
            if self.age >= self.lifetime:
                self.alive = False
    
    def draw(self, surface):
        """
        绘制切割效果
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        if self.alive:
            # 计算透明度
            alpha = int(255 * (1 - self.age / self.lifetime))
            color = (*self.color, alpha)
            
            # 创建临时表面
            temp_surface = pygame.Surface((self.length * 2, self.length * 2), pygame.SRCALPHA)
            
            # 绘制切割线
            start_x = int(self.length - self.length * math.cos(self.age * 10))
            start_y = int(self.length - self.length * math.sin(self.age * 10))
            end_x = int(self.length + self.length * math.cos(self.age * 10))
            end_y = int(self.length + self.length * math.sin(self.age * 10))
            
            pygame.draw.line(temp_surface, color, (start_x, start_y), (end_x, end_y), self.thickness)
            
            # 绘制到主表面
            surface.blit(temp_surface, (int(self.x - self.length), int(self.y - self.length)))


class EffectsManager:
    """
    特效管理器类
    """
    def __init__(self):
        """
        初始化特效管理器
        """
        self.particles = []
        self.slice_effects = []
    
    def create_explosion(self, x, y, color, particle_count=30):
        """
        创建爆炸特效
        
        Args:
            x (float): 爆炸位置x坐标
            y (float): 爆炸位置y坐标
            color (tuple): 爆炸颜色
            particle_count (int): 粒子数量
        """
        for _ in range(particle_count):
            # 随机速度
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 300)
            velocity_x = speed * math.cos(math.radians(angle))
            velocity_y = speed * math.sin(math.radians(angle))
            
            # 随机生命周期
            lifetime = random.uniform(0.5, 1.0)
            
            # 创建粒子
            particle = Particle(x, y, color, (velocity_x, velocity_y), lifetime)
            self.particles.append(particle)
    
    def create_slice_effect(self, x, y, color):
        """
        创建切割特效
        
        Args:
            x (float): 切割位置x坐标
            y (float): 切割位置y坐标
            color (tuple): 切割效果颜色
        """
        slice_effect = SliceEffect(x, y, color)
        self.slice_effects.append(slice_effect)
    
    def update(self, dt):
        """
        更新特效状态
        
        Args:
            dt (float): 时间步长（秒）
        """
        # 更新粒子
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # 更新切割效果
        for slice_effect in self.slice_effects[:]:
            slice_effect.update(dt)
            if not slice_effect.alive:
                self.slice_effects.remove(slice_effect)
    
    def draw(self, surface):
        """
        绘制特效
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 绘制粒子
        for particle in self.particles:
            particle.draw(surface)
        
        # 绘制切割效果
        for slice_effect in self.slice_effects:
            slice_effect.draw(surface)
    
    def clear(self):
        """
        清空所有特效
        """
        self.particles.clear()
        self.slice_effects.clear()
