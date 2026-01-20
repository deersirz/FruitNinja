"""
手势映射模块
将手势轨迹映射到游戏操作
"""

import numpy as np


class GestureMapper:
    """
    手势映射器类
    将手势轨迹映射到游戏操作
    """
    
    def __init__(self, tracker):
        """
        初始化手势映射器
        
        Args:
            tracker (GestureTracker): 手势跟踪器实例
        """
        self.tracker = tracker
        self.swipe_threshold = 30  # 挥砍动作阈值
        self.actions = {
            'swipe_left': '向左挥砍',
            'swipe_right': '向右挥砍',
            'swipe_up': '向上挥砍',
            'swipe_down': '向下挥砍',
            'no_action': '无操作'
        }
    
    def map_gesture_to_action(self):
        """
        将手势映射到游戏操作
        
        Returns:
            str: 游戏操作
        """
        # 获取轨迹
        trajectory = self.tracker.get_trajectory()
        
        if len(trajectory) < 3:
            return 'no_action'
        
        # 计算轨迹的移动方向和距离
        start_point = trajectory[0]
        end_point = trajectory[-1]
        
        dx = end_point['x'] - start_point['x']
        dy = end_point['y'] - start_point['y']
        distance = np.sqrt(dx**2 + dy**2)
        
        # 如果移动距离超过阈值
        if distance > self.swipe_threshold:
            # 计算移动方向
            angle = np.arctan2(dy, dx) * 180 / np.pi
            
            # 根据角度判断挥砍方向
            if -45 <= angle < 45:
                return 'swipe_right'
            elif 45 <= angle < 135:
                return 'swipe_down'
            elif -135 <= angle < -45:
                return 'swipe_up'
            else:
                return 'swipe_left'
        
        return 'no_action'
    
    def is_swipe(self):
        """
        判断是否为挥砍动作
        
        Returns:
            bool: 是否为挥砍动作
        """
        action = self.map_gesture_to_action()
        return action != 'no_action'
    
    def get_swipe_direction(self):
        """
        获取挥砍方向
        
        Returns:
            str: 挥砍方向
        """
        return self.map_gesture_to_action()
    
    def get_swipe_vector(self):
        """
        获取挥砍向量
        
        Returns:
            tuple: (dx, dy)
        """
        trajectory = self.tracker.get_trajectory()
        
        if len(trajectory) < 3:
            return 0, 0
        
        start_point = trajectory[0]
        end_point = trajectory[-1]
        
        dx = end_point['x'] - start_point['x']
        dy = end_point['y'] - start_point['y']
        
        return dx, dy
    
    def get_action_name(self, action):
        """
        获取操作名称
        
        Args:
            action (str): 操作代码
            
        Returns:
            str: 操作名称
        """
        return self.actions.get(action, '未知操作')
