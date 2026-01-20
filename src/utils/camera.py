"""
摄像头工具模块
管理摄像头的初始化和视频流捕获
"""

import cv2


class Camera:
    """
    摄像头类
    """
    def __init__(self, camera_id=0, width=640, height=480):
        """
        初始化摄像头
        
        Args:
            camera_id (int): 摄像头ID
            width (int): 摄像头宽度
            height (int): 摄像头高度
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_opened = False
        
        # 初始化摄像头
        self._init_camera()
    
    def _init_camera(self):
        """
        初始化摄像头
        """
        try:
            # 打开摄像头
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if self.cap.isOpened():
                # 设置摄像头参数
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.is_opened = True
                print(f"Camera initialized successfully: {self.width}x{self.height}")
            else:
                self.is_opened = False
                print(f"Failed to open camera: {self.camera_id}")
        except Exception as e:
            self.is_opened = False
            print(f"Error initializing camera: {e}")
    
    def get_frame(self):
        """
        获取摄像头帧
        
        Returns:
            numpy.ndarray: 摄像头帧，如果失败返回None
        """
        if not self.is_opened or not self.cap:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # 水平翻转帧，使镜像效果更自然
                frame = cv2.flip(frame, 1)
                return frame
            else:
                print("Failed to read frame from camera")
                return None
        except Exception as e:
            print(f"Error getting frame: {e}")
            return None
    
    def get_resolution(self):
        """
        获取摄像头分辨率
        
        Returns:
            tuple: (width, height)
        """
        if not self.is_opened or not self.cap:
            return (0, 0)
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        except Exception as e:
            print(f"Error getting resolution: {e}")
            return (0, 0)
    
    def set_resolution(self, width, height):
        """
        设置摄像头分辨率
        
        Args:
            width (int): 宽度
            height (int): 高度
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_opened or not self.cap:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # 更新分辨率
            self.width, self.height = self.get_resolution()
            print(f"Camera resolution set to: {self.width}x{self.height}")
            return True
        except Exception as e:
            print(f"Error setting resolution: {e}")
            return False
    
    def is_available(self):
        """
        检查摄像头是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.is_opened and self.cap is not None
    
    def release(self):
        """
        释放摄像头
        """
        if self.cap:
            try:
                self.cap.release()
                print("Camera released successfully")
            except Exception as e:
                print(f"Error releasing camera: {e}")
        
        self.is_opened = False
        self.cap = None
    
    def __del__(self):
        """
        析构函数
        """
        self.release()
