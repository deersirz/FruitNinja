"""
物理系统模块
模拟水果的物理运动
"""

import math
from game.config import GameConfig


class PhysicsEngine:
    """
    物理引擎类
    """
    def __init__(self):
        """
        初始化物理引擎
        """
        self.gravity = GameConfig.GRAVITY
    
    def apply_physics(self, fruit, dt):
        """
        应用物理效果到水果
        
        Args:
            fruit (Fruit): 水果对象
            dt (float): 时间步长（秒）
        """
        if not fruit.sliced:
            # 应用重力
            fruit.velocity_y += self.gravity * dt
            
            # 更新位置
            fruit.x += fruit.velocity_x * dt
            fruit.y += fruit.velocity_y * dt
            
            # 更新旋转
            fruit.rotation += fruit.angular_velocity * dt
    
    def calculate_trajectory(self, start_pos, velocity, duration):
        """
        计算物体的运动轨迹
        
        Args:
            start_pos (tuple): 起始位置 (x, y)
            velocity (tuple): 初始速度 (vx, vy)
            duration (float): 持续时间（秒）
            
        Returns:
            list: 轨迹点列表
        """
        trajectory = []
        x, y = start_pos
        vx, vy = velocity
        
        # 计算轨迹点
        for t in range(int(duration * 60)):
            dt = t / 60
            
            # 计算位置
            current_x = x + vx * dt
            current_y = y + vy * dt + 0.5 * self.gravity * dt**2
            
            trajectory.append((current_x, current_y))
        
        return trajectory
    
    def calculate_bounce(self, velocity, normal, restitution=0.5):
        """
        计算碰撞后的反弹速度
        
        Args:
            velocity (tuple): 碰撞前速度 (vx, vy)
            normal (tuple): 碰撞法线向量 (nx, ny)
            restitution (float):  restitution系数（0-1）
            
        Returns:
            tuple: 碰撞后速度 (vx', vy')
        """
        vx, vy = velocity
        nx, ny = normal
        
        # 计算速度在法线方向的分量
        dot_product = vx * nx + vy * ny
        
        # 计算反弹速度
        vx_new = vx - 2 * dot_product * nx * restitution
        vy_new = vy - 2 * dot_product * ny * restitution
        
        return (vx_new, vy_new)
    
    def is_point_in_circle(self, point, circle_center, radius):
        """
        判断点是否在圆内
        
        Args:
            point (tuple): 点坐标 (x, y)
            circle_center (tuple): 圆心坐标 (cx, cy)
            radius (float): 圆半径
            
        Returns:
            bool: 点是否在圆内
        """
        px, py = point
        cx, cy = circle_center
        
        distance = math.sqrt((px - cx)**2 + (py - cy)**2)
        return distance <= radius
    
    def calculate_distance(self, point1, point2):
        """
        计算两点之间的距离
        
        Args:
            point1 (tuple): 第一个点 (x1, y1)
            point2 (tuple): 第二个点 (x2, y2)
            
        Returns:
            float: 两点之间的距离
        """
        x1, y1 = point1
        x2, y2 = point2
        
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def calculate_angle(self, vector):
        """
        计算向量的角度
        
        Args:
            vector (tuple): 向量 (dx, dy)
            
        Returns:
            float: 角度（度）
        """
        dx, dy = vector
        
        if dx == 0:
            return 90 if dy > 0 else 270
        
        angle = math.atan2(dy, dx) * 180 / math.pi
        return angle
