"""
手部检测器模块
基于 MediaPipe 最新文档重新实现
"""
import cv2
import numpy as np
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2


class HandDetector:
    """
    手部检测器类
    基于 MediaPipe 最新文档重新实现
    """

    def __init__(self, width=320, height=240):
        self.width, self.height = width, height
        self.initialized = False
        self.error_message = ""
        self.last_results = None
        self.last_detection_time = 0
        self.detection_interval = 0.1  # 每秒最多检测10次，减少处理负担

        # 初始化 MediaPipe Hands
        try:
            print("初始化 MediaPipe Hands...")
            # 使用 MediaPipe Solutions Hands
            self.hands = solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            # 用于绘制手部关键点
            self.drawing = solutions.drawing_utils
            self.drawing_styles = solutions.drawing_styles
            self.initialized = True
            print("HandDetector 初始化成功")
        except ImportError as e:
            print(f"错误: 导入 MediaPipe 模块失败: {e}")
            print("请确保已安装 MediaPipe: pip install mediapipe")
            self.error_message = f"导入 MediaPipe 模块失败: {e}"
            self.hands = None
        except Exception as e:
            print(f"错误: 初始化 HandDetector 失败: {e}")
            print("详细错误信息:")
            import traceback
            traceback.print_exc()
            self.error_message = f"初始化失败: {e}"
            self.hands = None

    def detect_hands(self, frame):
        """
        检测手部关键点
        
        Args:
            frame: 摄像头帧
            
        Returns:
            dict: 包含检测结果的字典
        """
        import time
        
        detection_result = {
            'has_hand': False,
            'landmarks': [],
            'frame': frame,
            'initialized': self.initialized,
            'error_message': self.error_message
        }

        # 检查初始化状态
        if not self.initialized or self.hands is None:
            return detection_result

        # 检测频率控制
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            # 尚未到下次检测的时间，返回上次的结果
            if self.last_results:
                # 提取上次的关键点
                if self.last_results.multi_hand_landmarks:
                    detection_result['has_hand'] = True
                    for hand_landmarks in self.last_results.multi_hand_landmarks:
                        # 转换关键点坐标到屏幕空间
                        landmarks = []
                        for lm in hand_landmarks.landmark:
                            x = int(lm.x * self.width)
                            y = int(lm.y * self.height)
                            landmarks.append({'x': x, 'y': y})
                        detection_result['landmarks'] = landmarks
                        break  # 只取第一只手
            return detection_result

        try:
            # 转换为RGB格式
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 处理帧
            results = self.hands.process(rgb)
            self.last_results = results
            self.last_detection_time = current_time
            
            # 提取关键点
            if results.multi_hand_landmarks:
                detection_result['has_hand'] = True
                for hand_landmarks in results.multi_hand_landmarks:
                    # 转换关键点坐标到屏幕空间
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        x = int(lm.x * self.width)
                        y = int(lm.y * self.height)
                        landmarks.append({'x': x, 'y': y})
                    detection_result['landmarks'] = landmarks
                    break  # 只取第一只手
        except Exception:
            # 静默处理异常，避免影响游戏流畅度
            pass

        return detection_result

    def draw_hand_landmarks(self, frame, hand_landmarks=None):
        """
        在帧上绘制手部关键点
        
        Args:
            frame: 摄像头帧
            hand_landmarks: 手部关键点列表（可选）
            
        Returns:
            绘制后的帧
        """
        if not self.initialized or self.hands is None:
            return frame

        try:
            if hand_landmarks:
                # 使用传入的手部关键点
                # 注意：这里需要将hand_landmarks转换为MediaPipe的格式
                # 由于我们只有坐标，直接绘制关键点
                for lm in hand_landmarks:
                    x, y = lm['x'], lm['y']
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                
                # 重点标记关键逻辑点（指尖和关节）
                # 由于我们只有坐标列表，使用索引来识别关键点位
                fingertip_indices = [4, 8, 12, 16, 20]  # 指尖索引
                joint_indices = [2, 6, 10, 14, 18]  # 关节索引
                
                # 绘制指尖（红色，较大）
                for idx in fingertip_indices:
                    if idx < len(hand_landmarks):
                        lm = hand_landmarks[idx]
                        x, y = int(lm['x']), int(lm['y'])
                        cv2.circle(frame, (x, y), 8, (0, 0, 255), -1)  # 红色实心圆
                        cv2.circle(frame, (x, y), 10, (255, 255, 255), 2)  # 白色外圈
                
                # 绘制关节（蓝色，中等大小）
                for idx in joint_indices:
                    if idx < len(hand_landmarks):
                        lm = hand_landmarks[idx]
                        x, y = int(lm['x']), int(lm['y'])
                        cv2.circle(frame, (x, y), 6, (255, 0, 0), -1)  # 蓝色实心圆
                        cv2.circle(frame, (x, y), 8, (255, 255, 255), 2)  # 白色外圈
            elif self.last_results and self.last_results.multi_hand_landmarks:
                # 使用内部存储的手部关键点
                for hand_landmarks in self.last_results.multi_hand_landmarks:
                    # 绘制所有关键点和连接线
                    self.drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        solutions.hands.HAND_CONNECTIONS,
                        self.drawing_styles.get_default_hand_landmarks_style(),
                        self.drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # 重点标记关键逻辑点（指尖和关节）
                    self._draw_key_landmarks(frame, hand_landmarks)
        except Exception as e:
            print(f"错误: 绘制手部关键点时发生错误: {e}")

        return frame

    def _draw_key_landmarks(self, frame, hand_landmarks):
        """
        重点标记关键逻辑点
        
        Args:
            frame: 摄像头帧
            hand_landmarks: 手部关键点
        """
        # 指尖索引（拇指、食指、中指、无名指、小指）
        fingertip_indices = [4, 8, 12, 16, 20]
        # 指根关节索引
        joint_indices = [2, 6, 10, 14, 18]
        
        # 绘制指尖（红色，较大）
        for idx in fingertip_indices:
            lm = hand_landmarks.landmark[idx]
            x = int(lm.x * self.width)
            y = int(lm.y * self.height)
            cv2.circle(frame, (x, y), 8, (0, 0, 255), -1)  # 红色实心圆
            cv2.circle(frame, (x, y), 10, (255, 255, 255), 2)  # 白色外圈
        
        # 绘制指根关节（蓝色，中等大小）
        for idx in joint_indices:
            lm = hand_landmarks.landmark[idx]
            x = int(lm.x * self.width)
            y = int(lm.y * self.height)
            cv2.circle(frame, (x, y), 6, (255, 0, 0), -1)  # 蓝色实心圆
            cv2.circle(frame, (x, y), 8, (255, 255, 255), 2)  # 白色外圈

    def get_index_finger_tip_position(self, frame_width, frame_height):
        """
        获取食指指尖位置
        
        Args:
            frame_width: 帧宽度
            frame_height: 帧高度
            
        Returns:
            tuple: (x, y) 食指指尖位置
        """
        if not self.last_results or not self.last_results.multi_hand_landmarks:
            return None, None
        
        try:
            hand_landmarks = self.last_results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[8]  # 食指指尖索引
            x = int(index_finger_tip.x * frame_width)
            y = int(index_finger_tip.y * frame_height)
            return x, y
        except Exception:
            return None, None

    def get_two_finger_tips(self, frame_width, frame_height):
        """
        获取食指和中指指尖位置
        
        Args:
            frame_width: 帧宽度
            frame_height: 帧高度
            
        Returns:
            tuple: ((x1, y1), (x2, y2)) 食指和中指指尖位置
        """
        if not self.last_results or not self.last_results.multi_hand_landmarks:
            return None, None
        
        try:
            hand_landmarks = self.last_results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[8]  # 食指指尖索引
            middle_finger_tip = hand_landmarks.landmark[12]  # 中指指尖索引
            
            x1 = int(index_finger_tip.x * frame_width)
            y1 = int(index_finger_tip.y * frame_height)
            x2 = int(middle_finger_tip.x * frame_width)
            y2 = int(middle_finger_tip.y * frame_height)
            
            return (x1, y1), (x2, y2)
        except Exception:
            return None, None

    def is_palm_open(self):
        """
        检测手掌是否张开
        
        Returns:
            bool: 手掌是否张开
        """
        if not self.last_results or not self.last_results.multi_hand_landmarks:
            return False
        
        try:
            hand_landmarks = self.last_results.multi_hand_landmarks[0]
            
            # 计算手指是否张开
            # 简单实现：检查手指是否远离手掌中心
            palm_center = hand_landmarks.landmark[0]  # 手腕点
            
            # 检查食指是否张开
            index_finger_tip = hand_landmarks.landmark[8]
            index_finger_base = hand_landmarks.landmark[5]
            
            # 计算指尖到手腕的距离
            index_tip_dist = ((index_finger_tip.x - palm_center.x) ** 2 + 
                           (index_finger_tip.y - palm_center.y) ** 2) ** 0.5
            index_base_dist = ((index_finger_base.x - palm_center.x) ** 2 + 
                            (index_finger_base.y - palm_center.y) ** 2) ** 0.5
            
            # 如果指尖距离大于指根距离，认为手指张开
            return index_tip_dist > index_base_dist * 1.2
        except Exception:
            return False

    def close(self):
        """
        释放资源
        """
        try:
            if self.hands:
                self.hands.close()
            print("HandDetector resources released successfully")
        except Exception as e:
            print(f"Error releasing HandDetector resources: {e}")
    
    def is_initialized(self):
        """
        检查手部检测器是否已初始化
        
        Returns:
            bool: 是否已初始化
        """
        return self.initialized
    
    def get_error_message(self):
        """
        获取初始化错误信息
        
        Returns:
            str: 错误信息
        """
        return self.error_message
    
    def get_status(self):
        """
        获取手部检测器状态
        
        Returns:
            dict: 包含初始化状态和错误信息的字典
        """
        return {
            'initialized': self.initialized,
            'error_message': self.error_message,
            'version': 'mediapipe_solutions'
        }