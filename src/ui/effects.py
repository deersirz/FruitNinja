"""
视觉效果模块
管理游戏中的视觉特效
"""

import pygame
import random
import math


class Particle:
    """
    粒子基类
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
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)  # 度/秒
        self.gravity = 200
        self.air_resistance = 0.99
    
    def update(self, dt):
        """
        更新粒子状态
        
        Args:
            dt (float): 时间步长（秒）
        """
        if self.alive:
            # 应用空气阻力
            self.velocity_x *= self.air_resistance
            self.velocity_y *= self.air_resistance
            
            # 更新位置
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # 应用重力
            self.velocity_y += self.gravity * dt
            
            # 更新旋转
            self.rotation += self.rotation_speed * dt
            
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


class FruitParticle(Particle):
    """
    水果碎片粒子类
    """
    def __init__(self, x, y, color, velocity, lifetime, fruit_type):
        """
        初始化水果碎片粒子
        
        Args:
            x (float): 初始x坐标
            y (float): 初始y坐标
            color (tuple): 粒子颜色
            velocity (tuple): 粒子速度 (vx, vy)
            lifetime (float): 粒子生命周期（秒）
            fruit_type (str): 水果类型
        """
        super().__init__(x, y, color, velocity, lifetime)
        self.fruit_type = fruit_type
        # 根据水果类型调整大小和物理参数
        self.size = random.randint(4, 8)
        self.rotation_speed = random.uniform(-360, 360)  # 更快的旋转
        self.gravity = 300  # 更大的重力
        self.air_resistance = 0.98
    
    def update(self, dt):
        """
        更新水果碎片粒子状态
        
        Args:
            dt (float): 时间步长（秒）
        """
        if self.alive:
            super().update(dt)
            
            # 检查是否碰撞地面
            if self.y > 600:  # 假设地面高度为600
                self.y = 600
                # 反弹效果
                self.velocity_y = -abs(self.velocity_y) * 0.6
                self.velocity_x *= 0.8
    
    def draw(self, surface):
        """
        绘制水果碎片粒子
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        if self.alive:
            # 计算透明度
            alpha = int(255 * (1 - self.age / self.lifetime))
            color = (*self.color, alpha)
            
            # 创建临时表面
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            
            # 根据水果类型绘制不同形状
            if self.fruit_type in ['apple', 'strawberry']:
                # 圆形水果
                pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            elif self.fruit_type == 'banana':
                # 香蕉形状
                pygame.draw.ellipse(temp_surface, color, (0, self.size//2, self.size*2, self.size))
            elif self.fruit_type == 'watermelon':
                # 西瓜形状
                pygame.draw.rect(temp_surface, color, (0, 0, self.size*2, self.size*2))
            else:
                # 默认圆形
                pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            
            # 绘制到主表面
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))


class JuiceParticle(Particle):
    """
    果汁粒子类
    """
    def __init__(self, x, y, color, velocity, lifetime):
        """
        初始化果汁粒子
        
        Args:
            x (float): 初始x坐标
            y (float): 初始y坐标
            color (tuple): 粒子颜色
            velocity (tuple): 粒子速度 (vx, vy)
            lifetime (float): 粒子生命周期（秒）
        """
        super().__init__(x, y, color, velocity, lifetime)
        self.size = random.randint(2, 4)
        self.gravity = 150  # 较小的重力
        self.air_resistance = 0.95
    
    def draw(self, surface):
        """
        绘制果汁粒子
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        if self.alive:
            # 计算透明度
            alpha = int(200 * (1 - self.age / self.lifetime))
            color = (*self.color, alpha)
            
            # 创建临时表面
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            # 绘制圆形果汁滴
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
    
    def update(self, dt:float):
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
    
    def create_fruit_slice_effect(self, x, y, color, fruit_type, slice_direction=(1, 0)):
        """
        创建水果切割特效
        
        Args:
            x (float): 切割位置x坐标
            y (float): 切割位置y坐标
            color (tuple): 水果颜色
            fruit_type (str): 水果类型
            slice_direction (tuple): 切割方向向量 (dx, dy)
        """
        # 检查是否是炸弹
        if fruit_type == 'bomb':
            # 为炸弹创建爆炸特效
            self.create_bomb_explosion(x, y)
        else:
            # 创建切割线效果
            self.create_slice_effect(x, y, color)
            
            # 创建水果碎片粒子
            fragment_count = random.randint(8, 12)
            for _ in range(fragment_count):
                # 计算发射方向，基于切割方向
                angle = math.atan2(slice_direction[1], slice_direction[0])
                # 添加随机角度偏移
                random_angle = angle + random.uniform(-math.pi/3, math.pi/3)
                speed = random.uniform(150, 300)
                velocity_x = speed * math.cos(random_angle)
                velocity_y = speed * math.sin(random_angle)
                
                # 随机生命周期
                lifetime = random.uniform(1.0, 2.0)
                
                # 创建水果碎片粒子
                particle = FruitParticle(x, y, color, (velocity_x, velocity_y), lifetime, fruit_type)
                self.particles.append(particle)
            
            # 创建果汁粒子
            juice_count = random.randint(15, 25)
            for _ in range(juice_count):
                # 计算发射方向，更加分散
                angle = math.atan2(slice_direction[1], slice_direction[0])
                random_angle = angle + random.uniform(-math.pi/2, math.pi/2)
                speed = random.uniform(100, 250)
                velocity_x = speed * math.cos(random_angle)
                velocity_y = speed * math.sin(random_angle)
                
                # 随机生命周期
                lifetime = random.uniform(0.8, 1.5)
                
                # 创建果汁粒子
                particle = JuiceParticle(x, y, color, (velocity_x, velocity_y), lifetime)
                self.particles.append(particle)
    
    def create_bomb_explosion(self, x, y):
        """
        创建炸弹爆炸特效
        
        Args:
            x (float): 爆炸位置x坐标
            y (float): 爆炸位置y坐标
        """
        # 创建爆炸核心效果（红色和橙色粒子）
        explosion_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
        
        # 创建大量爆炸粒子
        explosion_count = 50
        for _ in range(explosion_count):
            # 随机方向和速度
            angle = random.uniform(0, 360)
            speed = random.uniform(200, 400)
            velocity_x = speed * math.cos(math.radians(angle))
            velocity_y = speed * math.sin(math.radians(angle))
            
            # 随机生命周期
            lifetime = random.uniform(0.8, 1.5)
            
            # 随机颜色
            color = random.choice(explosion_colors)
            
            # 创建爆炸粒子
            particle = Particle(x, y, color, (velocity_x, velocity_y), lifetime)
            # 调整爆炸粒子参数
            particle.size = random.randint(4, 8)
            particle.gravity = 50  # 减小重力，使爆炸效果更持久
            particle.air_resistance = 0.95
            self.particles.append(particle)
        
        # 创建爆炸冲击波效果
        shockwave_count = 8
        for _ in range(shockwave_count):
            # 随机方向
            angle = random.uniform(0, 360)
            speed = random.uniform(300, 500)
            velocity_x = speed * math.cos(math.radians(angle))
            velocity_y = speed * math.sin(math.radians(angle))
            
            # 较短的生命周期
            lifetime = random.uniform(0.3, 0.6)
            
            # 白色粒子模拟冲击波
            color = (255, 255, 255)
            
            # 创建冲击波粒子
            particle = Particle(x, y, color, (velocity_x, velocity_y), lifetime)
            particle.size = random.randint(2, 4)
            particle.gravity = 0  # 无重力
            particle.air_resistance = 0.9
            self.particles.append(particle)
    
    def update(self, dt):
        """
        更新特效状态
        
        Args:
            dt (float): 时间步长（秒）
        """
        # 限制粒子数量，避免过多粒子影响性能
        max_particles = 60  # 减少最大粒子数量，提高性能
        if len(self.particles) > max_particles:
            # 保留较新的粒子
            self.particles = self.particles[-max_particles:]
        
        # 更新粒子
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # 限制切割效果数量
        max_slice_effects = 5  # 减少最大切割效果数量，提高性能
        if len(self.slice_effects) > max_slice_effects:
            self.slice_effects = self.slice_effects[-max_slice_effects:]
        
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
        # 实现粒子效果的LOD（Level of Detail）系统
        # 根据粒子数量调整绘制精度
        particle_count = len(self.particles)
        
        if particle_count > 80:
            # 高粒子数量时，降低绘制精度
            draw_step = max(1, particle_count // 80)
            particles_to_draw = self.particles[::draw_step]
        elif particle_count > 40:
            # 中等粒子数量时，正常绘制
            particles_to_draw = self.particles
        else:
            # 低粒子数量时，完整绘制
            particles_to_draw = self.particles
        
        # 绘制粒子
        for particle in particles_to_draw:
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
