"""
碰撞检测模块
检测手势轨迹与水果的碰撞
"""

import math
from game.config import GameConfig


class CollisionDetector:
    """
    碰撞检测器类
    """
    def __init__(self):
        """
        初始化碰撞检测器
        """
        pass
    
    def detect_collision(self, gesture_trajectory, fruit):
        """
        检测手势轨迹与水果的碰撞
        
        Args:
            gesture_trajectory (list): 手势轨迹点列表
            fruit (Fruit): 水果对象
            
        Returns:
            bool: 是否碰撞
        """
        if fruit.sliced:
            return False
        
        # 如果轨迹点不足，无法检测碰撞
        if len(gesture_trajectory) < 2:
            return False
        
        # 检测轨迹线段与水果的碰撞
        for i in range(len(gesture_trajectory) - 1):
            start_point = gesture_trajectory[i]
            end_point = gesture_trajectory[i + 1]
            
            # 检测线段与圆的碰撞
            if self.line_circle_collision(
                (start_point['x'], start_point['y']),
                (end_point['x'], end_point['y']),
                (fruit.x, fruit.y),
                fruit.radius
            ):
                return True
        
        return False
    
    def line_circle_collision(self, line_start, line_end, circle_center, radius):
        """
        检测线段与圆的碰撞
        
        Args:
            line_start (tuple): 线段起点 (x1, y1)
            line_end (tuple): 线段终点 (x2, y2)
            circle_center (tuple): 圆心 (cx, cy)
            radius (float): 圆半径
            
        Returns:
            bool: 是否碰撞
        """
        x1, y1 = line_start
        x2, y2 = line_end
        cx, cy = circle_center
        
        # 计算线段的向量
        dx = x2 - x1
        dy = y2 - y1
        
        # 计算线段长度的平方
        line_length_sq = dx**2 + dy**2
        
        if line_length_sq == 0:
            # 线段长度为0，检测点是否在圆内
            distance_sq = (x1 - cx)**2 + (y1 - cy)**2
            return distance_sq <= radius**2
        
        # 计算参数t，使得点在线段上的投影
        t = max(0, min(1, ((cx - x1) * dx + (cy - y1) * dy) / line_length_sq))
        
        # 计算线段上的最近点
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # 计算最近点到圆心的距离
        distance_sq = (closest_x - cx)**2 + (closest_y - cy)**2
        
        # 如果距离小于半径，则碰撞
        return distance_sq <= radius**2
    
    def detect_multiple_collisions(self, gesture_trajectory, middle_finger_trajectory, fruits):
        """
        检测手势轨迹与多个水果的碰撞
        
        Args:
            gesture_trajectory (list): 手势轨迹点列表
            middle_finger_trajectory (list): 中指轨迹点列表
            fruits (list): 水果列表
            
        Returns:
            list: 碰撞的水果列表
        """
        collided_fruits = []
        
        for fruit in fruits:
            if fruit.type == 'watermelon':
                # 西瓜需要食指和中指同时滑动才能切割
                if self.detect_double_gesture_collision(gesture_trajectory, middle_finger_trajectory, fruit):
                    collided_fruits.append(fruit)
            else:
                # 其他水果只需要单个手势轨迹即可切割
                if self.detect_collision(gesture_trajectory, fruit):
                    collided_fruits.append(fruit)
        
        return collided_fruits
    
    def detect_double_gesture_collision(self, index_finger_trajectory, middle_finger_trajectory, fruit):
        """
        检测双手势轨迹（食指和中指）与水果的碰撞
        
        Args:
            index_finger_trajectory (list): 食指轨迹点列表
            middle_finger_trajectory (list): 中指轨迹点列表
            fruit (Fruit): 水果对象
            
        Returns:
            bool: 是否碰撞
        """
        if fruit.sliced:
            return False
        
        # 要求两个手指都有轨迹
        if len(index_finger_trajectory) < 2 or len(middle_finger_trajectory) < 2:
            return False
        
        # 检测食指轨迹与水果碰撞
        index_collision = self.detect_collision(index_finger_trajectory, fruit)
        
        # 检测中指轨迹与水果碰撞
        middle_collision = self.detect_collision(middle_finger_trajectory, fruit)
        
        # 西瓜需要两个手指都碰撞才能切割
        return index_collision and middle_collision
    
    def calculate_collision_point(self, line_start, line_end, circle_center, radius):
        """
        计算线段与圆的碰撞点
        
        Args:
            line_start (tuple): 线段起点 (x1, y1)
            line_end (tuple): 线段终点 (x2, y2)
            circle_center (tuple): 圆心 (cx, cy)
            radius (float): 圆半径
            
        Returns:
            tuple: 碰撞点 (x, y)，如果没有碰撞则返回None
        """
        x1, y1 = line_start
        x2, y2 = line_end
        cx, cy = circle_center
        
        # 计算线段的向量
        dx = x2 - x1
        dy = y2 - y1
        
        # 计算线段长度的平方
        line_length_sq = dx**2 + dy**2
        
        if line_length_sq == 0:
            return None
        
        # 计算参数t，使得点在线段上的投影
        t = max(0, min(1, ((cx - x1) * dx + (cy - y1) * dy) / line_length_sq))
        
        # 计算线段上的最近点
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # 计算最近点到圆心的距离
        distance_sq = (closest_x - cx)**2 + (closest_y - cy)**2
        
        # 如果距离小于半径，则碰撞
        if distance_sq <= radius**2:
            return (closest_x, closest_y)
        
        return None
    
    def get_collision_direction(self, collision_point, fruit_center):
        """
        获取碰撞方向
        
        Args:
            collision_point (tuple): 碰撞点 (x, y)
            fruit_center (tuple): 水果中心 (cx, cy)
            
        Returns:
            tuple: 碰撞方向向量 (dx, dy)
        """
        if not collision_point:
            return (0, 0)
        
        x, y = collision_point
        cx, cy = fruit_center
        
        # 计算方向向量
        dx = x - cx
        dy = y - cy
        
        # 归一化向量
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
        
        return (dx, dy)
