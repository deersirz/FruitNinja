"""
手势轨迹跟踪模块
跟踪手部运动轨迹，分析运动速度和方向
"""

import numpy as np
from game.config import GameConfig


class GestureTracker:
    """
    手势跟踪器类
    跟踪手部关键点的运动轨迹，分析运动速度和方向
    """
    
    def __init__(self, max_trajectory_length=50, smoothing_window=5, smoothness=0.5):
        """
        初始化手势跟踪器
        
        Args:
            max_trajectory_length (int): 轨迹最大长度
            smoothing_window (int): 平滑窗口大小
            smoothness (float): 平滑度参数 (0-1, 默认0.5)
        """
        self.previous_landmarks = None
        self.current_landmarks = None
        self.trajectory = []
        self.middle_finger_trajectory = []  # 中指轨迹
        self.max_trajectory_length = max_trajectory_length
        self.smoothing_window = smoothing_window
        self.position_history = []
        # 平滑度参数
        self.smoothness = smoothness
        # 方向变化检测参数
        self.direction_history = []
        self.max_direction_history = 5
        # 卡尔曼滤波参数
        self.kalman_filter = None
        self._init_kalman_filter()
    
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
                    
                    # 应用正确的坐标映射，考虑摄像头逆时针旋转90度的影响
                    # 1. 摄像头帧被逆时针旋转90度，因此需要调整坐标
                    # 2. 确保现实中的左右运动对应游戏中的左右运动
                    # 3. 确保现实中的上下运动对应游戏中的上下运动
                    # 4. 考虑摄像头分辨率（320x240）与游戏窗口分辨率（800x600）的差异
                    # 计算摄像头旋转后的坐标映射
                    # 由于摄像头被逆时针旋转90度，我们需要调整坐标系统
                    # 旋转90度后的坐标转换：x和y互换
                    # 移除镜像效果，确保左右方向正确映射
                    # 计算缩放比例，确保手部轨迹能够覆盖整个游戏窗口
                    camera_width = 320
                    camera_height = 240
                    game_width = GameConfig.WINDOW_WIDTH
                    game_height = GameConfig.WINDOW_HEIGHT
                    
                    # 计算x和y方向的缩放比例
                    scale_x = game_width / camera_height  # 摄像头高度对应游戏宽度
                    scale_y = game_height / camera_width  # 摄像头宽度对应游戏高度
                    
                    # 为轨迹点添加时间戳和透明度属性，用于实现刀痕效果
                    import time
                    timestamp = time.time()
                    
                    # 应用缩放和坐标转换
                    adjusted_x = fingertip['y'] * scale_x
                    adjusted_y = fingertip['x'] * scale_y
                    current_point = {'x': adjusted_x, 'y': adjusted_y}
                    
                    # 计算移动速度
                    speed = 0
                    if len(self.trajectory) > 0:
                        last_point = self.trajectory[-1]
                        dx = current_point['x'] - last_point['x']
                        dy = current_point['y'] - last_point['y']
                        distance = np.sqrt(dx**2 + dy**2)
                        time_diff = timestamp - last_point.get('timestamp', timestamp)
                        if time_diff > 0:
                            speed = distance / time_diff
                    
                    # 跟踪中指指尖（索引12）
                    if len(self.current_landmarks) > 12:  # 12是中指指尖的索引
                        middle_fingertip = self.current_landmarks[12]
                        
                        # 应用相同的坐标映射
                        middle_adjusted_x = middle_fingertip['y'] * scale_x
                        middle_adjusted_y = middle_fingertip['x'] * scale_y
                        middle_current_point = {'x': middle_adjusted_x, 'y': middle_adjusted_y}
                        
                        # 计算中指移动速度
                        middle_speed = 0
                        if len(self.middle_finger_trajectory) > 0:
                            last_point = self.middle_finger_trajectory[-1]
                            dx = middle_current_point['x'] - last_point['x']
                            dy = middle_current_point['y'] - last_point['y']
                            distance = np.sqrt(dx**2 + dy**2)
                            time_diff = timestamp - last_point.get('timestamp', timestamp)
                            if time_diff > 0:
                                middle_speed = distance / time_diff
                        
                        # 为中指轨迹点添加时间戳和透明度属性
                        middle_point_with_properties = {
                            'x': middle_current_point['x'],
                            'y': middle_current_point['y'],
                            'timestamp': timestamp,
                            'alpha': 1.0,  # 初始透明度为1.0（完全不透明）
                            'speed': middle_speed  # 添加速度信息
                        }
                        
                        # 智能采样中指轨迹点
                        if not self.middle_finger_trajectory or len(self.middle_finger_trajectory) == 0:
                            # 轨迹为空，直接添加
                            self.middle_finger_trajectory.append(middle_point_with_properties)
                        else:
                            # 计算与最后一个轨迹点的距离
                            last_point = self.middle_finger_trajectory[-1]
                            dx = middle_point_with_properties['x'] - last_point['x']
                            dy = middle_point_with_properties['y'] - last_point['y']
                            # 使用平方距离比较，避免开方运算，提高性能
                            squared_distance = dx**2 + dy**2
                            
                            # 根据速度调整最小距离阈值
                            base_min_distance = 3
                            speed_factor = min(middle_speed / 200, 2)  # 速度越快，阈值越大
                            min_distance = base_min_distance + speed_factor * 2
                            min_squared_distance = min_distance**2
                            
                            # 只有当距离超过阈值时才添加新点
                            if squared_distance > min_squared_distance:
                                # 检查是否需要插入中间点，避免轨迹断裂
                                max_squared_distance = (min_distance * 3)**2
                                if squared_distance > max_squared_distance:  # 距离过大，可能导致轨迹断裂
                                    # 计算实际距离
                                    distance = squared_distance**0.5
                                    # 计算需要插入的中间点数量
                                    steps = max(2, int(distance / (min_distance * 2)))
                                    for i in range(1, steps):
                                        # 线性插值计算中间点
                                        t = i / steps
                                        interpolated_x = last_point['x'] + (middle_point_with_properties['x'] - last_point['x']) * t
                                        interpolated_y = last_point['y'] + (middle_point_with_properties['y'] - last_point['y']) * t
                                        interpolated_timestamp = last_point['timestamp'] + (timestamp - last_point['timestamp']) * t
                                        interpolated_alpha = 1.0 - t * 0.3  # 中间点透明度 slightly lower
                                        
                                        # 创建中间点
                                        interpolated_point = {
                                            'x': interpolated_x,
                                            'y': interpolated_y,
                                            'timestamp': interpolated_timestamp,
                                            'alpha': interpolated_alpha,
                                            'speed': middle_speed * (1 - t * 0.2)  # 中间点速度 slightly lower
                                        }
                                        self.middle_finger_trajectory.append(interpolated_point)
                                
                                # 添加当前点
                                self.middle_finger_trajectory.append(middle_point_with_properties)
                        
                        # 限制中指轨迹长度
                        if len(self.middle_finger_trajectory) > self.max_trajectory_length:
                            self.middle_finger_trajectory.pop(0)
                    
                    point_with_properties = {
                        'x': current_point['x'],
                        'y': current_point['y'],
                        'timestamp': timestamp,
                        'alpha': 1.0,  # 初始透明度为1.0（完全不透明）
                        'speed': speed  # 添加速度信息
                    }
                    
                    # 智能采样轨迹点，根据速度调整距离阈值
                    if not self.trajectory or len(self.trajectory) == 0:
                        # 轨迹为空，直接添加
                        self.trajectory.append(point_with_properties)
                    else:
                        # 计算与最后一个轨迹点的距离
                        last_point = self.trajectory[-1]
                        dx = point_with_properties['x'] - last_point['x']
                        dy = point_with_properties['y'] - last_point['y']
                        # 使用平方距离比较，避免开方运算，提高性能
                        squared_distance = dx**2 + dy**2
                        
                        # 根据速度调整最小距离阈值
                        base_min_distance = 3
                        speed_factor = min(speed / 200, 2)  # 速度越快，阈值越大
                        min_distance = base_min_distance + speed_factor * 2
                        min_squared_distance = min_distance**2
                        
                        # 只有当距离超过阈值时才添加新点
                        if squared_distance > min_squared_distance:
                            # 检查是否需要插入中间点，避免轨迹断裂
                            max_squared_distance = (min_distance * 3)**2
                            if squared_distance > max_squared_distance:  # 距离过大，可能导致轨迹断裂
                                # 计算实际距离
                                distance = squared_distance**0.5
                                # 计算需要插入的中间点数量
                                steps = max(2, int(distance / (min_distance * 2)))
                                for i in range(1, steps):
                                    # 线性插值计算中间点
                                    t = i / steps
                                    interpolated_x = last_point['x'] + (point_with_properties['x'] - last_point['x']) * t
                                    interpolated_y = last_point['y'] + (point_with_properties['y'] - last_point['y']) * t
                                    interpolated_timestamp = last_point['timestamp'] + (timestamp - last_point['timestamp']) * t
                                    interpolated_alpha = 1.0 - t * 0.3  # 中间点透明度 slightly lower
                                    
                                    # 创建中间点
                                    interpolated_point = {
                                        'x': interpolated_x,
                                        'y': interpolated_y,
                                        'timestamp': interpolated_timestamp,
                                        'alpha': interpolated_alpha,
                                        'speed': speed * (1 - t * 0.2)  # 中间点速度 slightly lower
                                    }
                                    self.trajectory.append(interpolated_point)
                            
                            # 添加当前点
                            self.trajectory.append(point_with_properties)
                    
                    # 限制轨迹长度
                    if len(self.trajectory) > self.max_trajectory_length:
                        self.trajectory.pop(0)
        else:
            self.current_landmarks = None
            # 清空轨迹和历史记录
            self.trajectory = []
            self.position_history = []
    
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
            
            # 计算方向（角度，反正切arctangent）
            if distance > 0:
                angle = np.arctan2(dy, dx) * 180 / np.pi  # arctangent
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
    
    def get_middle_finger_trajectory(self):
        """
        获取中指运动轨迹
        
        Returns:
            list: 中指运动轨迹
        """
        return self.middle_finger_trajectory
    
    def get_both_fingers_trajectory(self):
        """
        获取食指和中指运动轨迹
        
        Returns:
            dict: 包含食指和中指轨迹的字典
        """
        return {
            'index_finger': self.trajectory,
            'middle_finger': self.middle_finger_trajectory
        }
    
    def clear_trajectory(self):
        """
        清空轨迹
        """
        self.trajectory = []
        self.middle_finger_trajectory = []
        self.position_history = []
    
    def update_trajectory_alpha(self, dt):
        """
        更新轨迹点的透明度，实现动态消散效果
        
        Args:
            dt (float): 时间步长（秒）
        """
        import time
        current_time = time.time()
        
        # 计算每个轨迹点的透明度，基于其存在时间
        for point in self.trajectory:
            # 计算点的存在时间
            age = current_time - point['timestamp']
            
            # 透明度随时间衰减，调整为1.5秒后完全消失，更符合刀痕效果
            max_age = 1.5
            if age < max_age:
                # 使用非线性衰减，使轨迹消失更自然
                decay_factor = 1.0 - (age / max_age)
                point['alpha'] = decay_factor ** 1.2  # 非线性衰减
            else:
                point['alpha'] = 0.0
        
        # 计算中指轨迹点的透明度
        for point in self.middle_finger_trajectory:
            # 计算点的存在时间
            age = current_time - point['timestamp']
            
            # 透明度随时间衰减，调整为1.5秒后完全消失，更符合刀痕效果
            max_age = 1.5
            if age < max_age:
                # 使用非线性衰减，使轨迹消失更自然
                decay_factor = 1.0 - (age / max_age)
                point['alpha'] = decay_factor ** 1.2  # 非线性衰减
            else:
                point['alpha'] = 0.0
        
        # 移除完全透明的点
        self.trajectory = [point for point in self.trajectory if point['alpha'] > 0.01]
        self.middle_finger_trajectory = [point for point in self.middle_finger_trajectory if point['alpha'] > 0.01]
        
        # 确保轨迹点数量适中，避免过多点影响性能
        max_points = 30
        if len(self.trajectory) > max_points:
            # 均匀采样轨迹点
            step = len(self.trajectory) // max_points
            self.trajectory = self.trajectory[::step]
        
        if len(self.middle_finger_trajectory) > max_points:
            # 均匀采样中指轨迹点
            step = len(self.middle_finger_trajectory) // max_points
            self.middle_finger_trajectory = self.middle_finger_trajectory[::step]
    
    def _init_kalman_filter(self):
        """
        初始化卡尔曼滤波器
        """
        try:
            # 简单的卡尔曼滤波实现
            # 状态向量: [x, y, vx, vy]
            # 观测向量: [x, y]
            self.kalman_filter = {
                'x': 0,
                'y': 0,
                'vx': 0,
                'vy': 0,
                'error_measure': 0.1,
                'error_estimate': 0.1,
                'kalman_gain': 0
            }
        except Exception as e:
            print(f"Error initializing Kalman filter: {e}")
            self.kalman_filter = None
    
    def _apply_kalman_filter(self, x, y):
        """
        应用卡尔曼滤波平滑位置
        
        Args:
            x (float): 当前x坐标
            y (float): 当前y坐标
            
        Returns:
            dict: 平滑后的位置点
        """
        if not self.kalman_filter:
            return {'x': x, 'y': y}
        
        try:
            # 预测
            self.kalman_filter['x'] += self.kalman_filter['vx']
            self.kalman_filter['y'] += self.kalman_filter['vy']
            
            # 更新误差
            self.kalman_filter['error_estimate'] += 0.1
            
            # 计算卡尔曼增益（优化计算顺序，减少重复计算）
            error_sum = self.kalman_filter['error_estimate'] + self.kalman_filter['error_measure']
            if error_sum > 0:
                self.kalman_filter['kalman_gain'] = self.kalman_filter['error_estimate'] / error_sum
            else:
                self.kalman_filter['kalman_gain'] = 0
            
            # 更新状态
            dx = x - self.kalman_filter['x']
            dy = y - self.kalman_filter['y']
            
            # 应用卡尔曼增益
            kalman_gain = self.kalman_filter['kalman_gain']
            self.kalman_filter['x'] += kalman_gain * dx
            self.kalman_filter['y'] += kalman_gain * dy
            
            # 更新速度（使用固定系数，避免重复计算）
            self.kalman_filter['vx'] = 0.8 * self.kalman_filter['vx'] + 0.2 * dx
            self.kalman_filter['vy'] = 0.8 * self.kalman_filter['vy'] + 0.2 * dy
            
            # 更新误差估计
            self.kalman_filter['error_estimate'] = (1 - kalman_gain) * self.kalman_filter['error_estimate']
            
            return {'x': self.kalman_filter['x'], 'y': self.kalman_filter['y']}
        except Exception as e:
            print(f"Error applying Kalman filter: {e}")
            return {'x': x, 'y': y}
    
    def _apply_smoothing(self):
        """
        应用移动平均滤波平滑位置
        
        Returns:
            dict: 平滑后的位置点
        """
        if len(self.position_history) == 0:
            return {'x': 0, 'y': 0}
        
        # 计算移动速度
        speed = 0
        if len(self.position_history) > 1:
            last_point = self.position_history[-1]
            second_last_point = self.position_history[-2]
            dx = last_point['x'] - second_last_point['x']
            dy = last_point['y'] - second_last_point['y']
            distance = np.sqrt(dx**2 + dy**2)
            # 假设时间间隔为0.033秒（约30fps）
            time_diff = 0.033
            speed = distance / time_diff
        
        # 根据速度调整平滑窗口大小
        adaptive_window = min(max(3, int(self.smoothing_window - speed / 100)), self.smoothing_window)
        
        # 使用自适应窗口计算移动平均值
        if len(self.position_history) >= adaptive_window:
            recent_history = self.position_history[-adaptive_window:]
        else:
            recent_history = self.position_history
        
        # 计算加权移动平均值，最近的点权重更高
        weights = np.linspace(0.1, 1.0, len(recent_history))
        weights /= sum(weights)
        
        weighted_avg_x = sum(p['x'] * w for p, w in zip(recent_history, weights))
        weighted_avg_y = sum(p['y'] * w for p, w in zip(recent_history, weights))
        
        # 应用卡尔曼滤波进一步平滑
        return self._apply_kalman_filter(weighted_avg_x, weighted_avg_y)
    
    def _predict_next_point(self, current_point):
        """
        预测下一个位置点，减少轨迹抖动
        
        Args:
            current_point (dict): 当前位置点
            
        Returns:
            dict: 预测的位置点
        """
        if len(self.trajectory) < 2:
            return current_point
        
        # 计算当前速度
        current_speed = 0
        if len(self.trajectory) > 0:
            last_point = self.trajectory[-1]
            dx = current_point['x'] - last_point['x']
            dy = current_point['y'] - last_point['y']
            distance = np.sqrt(dx**2 + dy**2)
            # 假设时间间隔为0.033秒（约30fps）
            time_diff = 0.033
            current_speed = distance / time_diff
        
        # 根据轨迹长度和速度选择不同的预测策略
        if len(self.trajectory) >= 3:
            # 使用最近三个点计算速度和加速度
            prev_point = self.trajectory[-1]
            prev_prev_point = self.trajectory[-2]
            prev_prev_prev_point = self.trajectory[-3]
            
            # 计算速度
            vx1 = prev_point['x'] - prev_prev_point['x']
            vy1 = prev_point['y'] - prev_prev_point['y']
            
            vx2 = prev_prev_point['x'] - prev_prev_prev_point['x']
            vy2 = prev_prev_point['y'] - prev_prev_prev_point['y']
            
            # 计算加速度
            ax = vx1 - vx2
            ay = vy1 - vy2
            
            # 预测下一个速度
            predicted_vx = vx1 + ax * 0.1
            predicted_vy = vy1 + ay * 0.1
            
            # 根据速度调整预测强度
            if current_speed > 100:
                # 快速移动时，增加预测强度以减少延迟
                damping = 0.3
            else:
                # 慢速移动时，减少预测强度以避免过度预测
                damping = 0.15
            
            # 应用阻尼系数
            predicted_x = current_point['x'] + predicted_vx * damping
            predicted_y = current_point['y'] + predicted_vy * damping
        elif len(self.trajectory) == 2:
            # 使用最近两个点计算速度
            prev_point = self.trajectory[-1]
            prev_prev_point = self.trajectory[-2]
            
            # 计算速度
            vx = prev_point['x'] - prev_prev_point['x']
            vy = prev_point['y'] - prev_prev_point['y']
            
            # 根据速度调整预测强度
            if current_speed > 100:
                damping = 0.25
            else:
                damping = 0.1
            
            # 应用阻尼系数
            predicted_x = current_point['x'] + vx * damping
            predicted_y = current_point['y'] + vy * damping
        else:
            # 轨迹点不足，直接返回当前点
            predicted_x = current_point['x']
            predicted_y = current_point['y']
        
        return {'x': predicted_x, 'y': predicted_y}
    
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

    def is_swing_gesture(self, speed_threshold=40, min_trajectory_points=5):
        """
        判断是否为挥砍手势（快速挥动）
        Args:
            speed_threshold (float): 速度阈值，超过则判定为挥砍
            min_trajectory_points (int): 最少轨迹点数
        Returns:
            bool: 是否为挥砍手势
        """
        trajectory = self.get_trajectory()
        if len(trajectory) < min_trajectory_points:
            return False
        # 计算最近一段轨迹的平均速度
        total_dist = 0
        for i in range(1, len(trajectory)):
            dx = trajectory[i]['x'] - trajectory[i-1]['x']
            dy = trajectory[i]['y'] - trajectory[i-1]['y']
            total_dist += np.sqrt(dx**2 + dy**2)
        avg_speed = total_dist / (len(trajectory)-1)
        return avg_speed > speed_threshold
    
    def calculate_direction(self, point1, point2):
        """
        计算两点之间的方向向量
        
        Args:
            point1 (dict): 第一个点
            point2 (dict): 第二个点
            
        Returns:
            tuple: 方向向量 (dx, dy)
        """
        dx = point2['x'] - point1['x']
        dy = point2['y'] - point1['y']
        return dx, dy
    
    def calculate_angle(self, vector1, vector2):
        """
        计算两个向量之间的夹角
        
        Args:
            vector1 (tuple): 第一个向量 (dx1, dy1)
            vector2 (tuple): 第二个向量 (dx2, dy2)
            
        Returns:
            float: 夹角（度）
        """
        # 计算点积
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        
        # 计算向量长度
        len1 = np.sqrt(vector1[0]**2 + vector1[1]**2)
        len2 = np.sqrt(vector2[0]**2 + vector2[1]**2)
        
        if len1 == 0 or len2 == 0:
            return 0
        
        # 计算夹角（弧度）
        cos_theta = dot_product / (len1 * len2)
        # 确保值在[-1, 1]范围内
        cos_theta = max(-1, min(1, cos_theta))
        theta = np.arccos(cos_theta)
        
        # 转换为度
        return theta * 180 / np.pi
    
    def detect_direction_change(self):
        """
        检测手部运动方向的变化
        
        Returns:
            tuple: (has_change, change_angle, speed)
        """
        if len(self.trajectory) < 3:
            return False, 0, 0
        
        # 获取最近三个点
        p1 = self.trajectory[-3]
        p2 = self.trajectory[-2]
        p3 = self.trajectory[-1]
        
        # 计算方向向量
        vec1 = self.calculate_direction(p1, p2)
        vec2 = self.calculate_direction(p2, p3)
        
        # 计算夹角
        angle = self.calculate_angle(vec1, vec2)
        
        # 计算速度
        speed = p3.get('speed', 0)
        
        # 判断是否有显著的方向变化
        has_change = angle > 30  # 方向变化角度阈值
        
        # 更新方向历史
        self.direction_history.append((vec2, angle, speed))
        if len(self.direction_history) > self.max_direction_history:
            self.direction_history.pop(0)
        
        return has_change, angle, speed
    
    def calculate_bezier_points(self, p1, p2, p3, num_points=5):
        """
        计算二次贝塞尔曲线上的点
        
        Args:
            p1 (dict): 起点
            p2 (dict): 控制点
            p3 (dict): 终点
            num_points (int): 生成的点数量
            
        Returns:
            list: 贝塞尔曲线上的点列表
        """
        points = []
        for t in range(num_points + 1):
            t_normalized = t / num_points
            
            # 二次贝塞尔曲线公式
            x = (1 - t_normalized)**2 * p1['x'] + 2 * (1 - t_normalized) * t_normalized * p2['x'] + t_normalized**2 * p3['x']
            y = (1 - t_normalized)**2 * p1['y'] + 2 * (1 - t_normalized) * t_normalized * p2['y'] + t_normalized**2 * p3['y']
            
            # 计算速度（线性插值）
            speed = (1 - t_normalized) * p1.get('speed', 0) + t_normalized * p3.get('speed', 0)
            
            # 计算时间戳（线性插值）
            timestamp = (1 - t_normalized) * p1.get('timestamp', 0) + t_normalized * p3.get('timestamp', 0)
            
            # 计算透明度（线性插值）
            alpha = (1 - t_normalized) * p1.get('alpha', 1.0) + t_normalized * p3.get('alpha', 1.0)
            
            points.append({
                'x': x,
                'y': y,
                'speed': speed,
                'timestamp': timestamp,
                'alpha': alpha
            })
        
        return points
    
    def get_smooth_trajectory(self):
        """
        获取平滑后的轨迹
        
        Returns:
            list: 平滑后的轨迹点列表
        """
        if len(self.trajectory) < 2:
            return self.trajectory
        
        smooth_trajectory = []
        
        # 添加第一个点
        smooth_trajectory.append(self.trajectory[0])
        
        # 处理中间点
        for i in range(1, len(self.trajectory) - 1):
            p_prev = self.trajectory[i-1]
            p_curr = self.trajectory[i]
            p_next = self.trajectory[i+1]
            
            # 检测方向变化
            vec1 = self.calculate_direction(p_prev, p_curr)
            vec2 = self.calculate_direction(p_curr, p_next)
            angle = self.calculate_angle(vec1, vec2)
            
            # 如果方向变化较大，使用贝塞尔曲线平滑
            if angle > 30:
                # 计算控制点
                # 根据方向变化角度和速度调整控制点位置
                speed = p_curr.get('speed', 0)
                control_factor = min(self.smoothness * (angle / 90) * (speed / 200), 1.0)
                
                # 计算控制点（在当前点附近）
                dx1 = p_curr['x'] - p_prev['x']
                dy1 = p_curr['y'] - p_prev['y']
                dx2 = p_next['x'] - p_curr['x']
                dy2 = p_next['y'] - p_curr['y']
                
                # 控制点在两个方向的中间
                control_x = p_curr['x'] + (dx1 + dx2) * 0.1 * control_factor
                control_y = p_curr['y'] + (dy1 + dy2) * 0.1 * control_factor
                
                control_point = {
                    'x': control_x,
                    'y': control_y,
                    'speed': p_curr.get('speed', 0),
                    'timestamp': p_curr.get('timestamp', 0),
                    'alpha': p_curr.get('alpha', 1.0)
                }
                
                # 计算贝塞尔曲线上的点
                bezier_points = self.calculate_bezier_points(p_curr, control_point, p_next)
                
                # 添加贝塞尔曲线上的点（跳过第一个点，避免重复）
                smooth_trajectory.extend(bezier_points[1:])
            else:
                # 方向变化不大，直接添加当前点
                smooth_trajectory.append(p_curr)
        
        # 添加最后一个点
        if len(self.trajectory) > 1:
            smooth_trajectory.append(self.trajectory[-1])
        
        return smooth_trajectory
    
    def set_smoothness(self, value):
        """
        设置平滑度参数
        
        Args:
            value (float): 平滑度值 (0-1)
        """
        self.smoothness = max(0.0, min(1.0, value))
