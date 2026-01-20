"""
手部检测器模块
集成MediaPipe Hands进行手部关键点检测
"""

import cv2
import numpy as np

# 兼容不同版本的 MediaPipe 导入路径
try:
    import mediapipe as mp
    MP_HANDS = mp.solutions.hands  # 旧版/经典路径
except Exception:
    # 新版可能没有 mp.solutions，改用 python.solutions
    from mediapipe.python.solutions import hands as MP_HANDS


class HandDetector:
    """
    手部检测器类
    使用MediaPipe Hands检测手部关键点
    """
    
    def __init__(self, width=640, height=480):
        """
        初始化手部检测器
        
        Args:
            width (int): 摄像头宽度
            height (int): 摄像头高度
        """
        # 初始化MediaPipe Hands
        self.hands = MP_HANDS.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        self.width = width
        self.height = height
        
    def detect_hands(self, frame):
        """
        检测手部关键点
        
        Args:
            frame (np.ndarray): 输入帧
            
        Returns:
            dict: 检测结果，包含手部关键点坐标
        """
        # 转换为RGB格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检测手部
        results = self.hands.process(rgb_frame)
        
        detection_result = {
            'has_hand': False,
            'landmarks': [],
            'frame': frame
        }
        
        # 如果检测到手部
        if results.multi_hand_landmarks:
            detection_result['has_hand'] = True
            
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    # 转换为像素坐标
                    x = int(lm.x * self.width)
                    y = int(lm.y * self.height)
                    landmarks.append({'x': x, 'y': y})
                detection_result['landmarks'] = landmarks
        
        return detection_result
    
    def get_frame(self):
        """
        获取摄像头帧
        
        Returns:
            np.ndarray: 摄像头帧
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # 水平翻转帧
        frame = cv2.flip(frame, 1)
        return frame
    
    def close(self):
        """
        关闭摄像头
        """
        if self.cap.isOpened():
            self.cap.release()
        
        # 关闭MediaPipe Hands
        self.hands.close()
