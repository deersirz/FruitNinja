"""
手势轨迹跟踪模块
跟踪手部运动轨迹，分析运动速度和方向
"""

import numpy as np


class GestureTracker:
    """
    手势跟踪器类
    跟踪手部关键点的运动轨迹，分析运动速度和方向
    """
    
    def __init__(self, max_trajectory_length=50):
        """
        初始化手势跟踪器
        
        Args:
            max_trajectory_length (int): 轨迹最大长度
        """
        self.previous_landmarks = None
        self.current_landmarks = None
        self.trajectory = []
        self.max_trajectory_length = max_trajectory_length
        
    def update_landmarks(self, landmarks):
        """
        更新手部关键点
        
        Args:
            landmarks (list): 手部关键点列表
        """
        if landmarks:
            self.previous_landmarks = self.current_landmarks
            self.current_landmarks = landmarks
            
            # 更新轨迹
            if self.current_landmarks:
                # 使用食指指尖作为轨迹点
                if len(self.current_landmarks) > 8:  # 8是食指指尖的索引
                    fingertip = self.current_landmarks[8]
                    self.trajectory.append({'x': fingertip['x'], 'y': fingertip['y']})
                    
                    # 限制轨迹长度
                    if len(self.trajectory) > self.max_trajectory_length:
                        self.trajectory.pop(0)
        else:
            self.current_landmarks = None
            # 清空轨迹
            self.trajectory = []
    
    def track_movement(self):
        """
        计算手部移动速度和方向
        
        Returns:
            tuple: (速度, 方向)
        """
        if not self.previous_landmarks or not self.current_landmarks:
            return 0.0, 0.0
        
        # 使用食指指尖计算移动
        if len(self.previous_landmarks) > 8 and len(self.current_landmarks) > 8:
            prev_x = self.previous_landmarks[8]['x']
            prev_y = self.previous_landmarks[8]['y']
            curr_x = self.current_landmarks[8]['x']
            curr_y = self.current_landmarks[8]['y']
            
            # 计算距离
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            distance = np.sqrt(dx**2 + dy**2)
            
            # 计算方向（角度）
            if distance > 0:
                angle = np.arctan2(dy, dx) * 180 / np.pi
            else:
                angle = 0.0
            
            return distance, angle
        
        return 0.0, 0.0
    
    def get_trajectory(self):
        """
        获取手部运动轨迹
        
        Returns:
            list: 手部运动轨迹
        """
        return self.trajectory
    
    def clear_trajectory(self):
        """
        清空轨迹
        """
        self.trajectory = []
    
    def get_movement_vector(self):
        """
        获取移动向量
        
        Returns:
            tuple: (dx, dy)
        """
        if not self.previous_landmarks or not self.current_landmarks:
            return 0, 0
        
        # 使用食指指尖计算移动向量
        if len(self.previous_landmarks) > 8 and len(self.current_landmarks) > 8:
            prev_x = self.previous_landmarks[8]['x']
            prev_y = self.previous_landmarks[8]['y']
            curr_x = self.current_landmarks[8]['x']
            curr_y = self.current_landmarks[8]['y']
            
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            
            return dx, dy
        
        return 0, 0
