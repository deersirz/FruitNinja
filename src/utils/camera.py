"""
摄像头工具模块
管理摄像头的初始化和视频流捕获
"""

import cv2


class Camera:
    """
    摄像头类
    """
    def __init__(self, camera_id=0, width=320, height=240, max_fps=20):
        """
        初始化摄像头
        
        Args:
            camera_id (int): 摄像头ID
            width (int): 摄像头宽度
            height (int): 摄像头高度
            max_fps (int): 最大帧率
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.max_fps = max_fps
        self.cap = None
        self.is_opened = False
        self.loading = False
        self.ready = False
        self.warmup_frames = 0
        self.max_warmup_frames = 3  # 进一步减少预热帧数，加快初始化速度
        self.last_frame_time = 0
        self.frame_interval = 1.0 / max_fps
        self.frame_buffer = None  # 添加帧缓冲区，减少闪烁
        
        # 初始化摄像头
        self._init_camera()
    
    def _init_camera(self):
        """
        初始化摄像头
        """
        try:
            # 设置加载状态
            self.loading = True
            print(f"开始初始化摄像头 {self.camera_id}...")
            
            # 打开摄像头
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if self.cap.isOpened():
                # 设置摄像头参数
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                
                # 验证设置是否成功
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                self.is_opened = True
                print(f"摄像头初始化成功: {actual_width}x{actual_height}")
                print("摄像头正在预热中...")
                
                # 开始预热过程
                self._start_warmup()
            else:
                self.is_opened = False
                self.loading = False
                print(f"无法打开摄像头: {self.camera_id}")
                print("可能的原因:")
                print("1. 摄像头硬件未连接或损坏")
                print("2. 摄像头被其他应用程序占用")
                print("3. 应用程序未获得摄像头访问权限")
        except Exception as e:
            self.is_opened = False
            self.loading = False
            print(f"初始化摄像头时发生错误: {e}")
            print("详细错误信息:")
            import traceback
            traceback.print_exc()
    
    def _start_warmup(self):
        """
        开始摄像头预热过程
        捕获几帧以让摄像头调整曝光和白平衡
        """
        # 预热过程在get_frame方法中进行
        pass
    
    def get_frame(self):
        """
        获取摄像头帧
        
        Returns:
            numpy.ndarray: 摄像头帧，如果失败返回None
        """
        import time
        
        if not self.is_opened or not self.cap:
            return self.frame_buffer
        
        # 帧率控制
        current_time = time.time()
        need_new_frame = not self.ready or current_time - self.last_frame_time >= self.frame_interval
        
        try:
            # 使用非阻塞方式读取帧
            ret, frame = self.cap.read()
            if ret:
                try:
                    # 逆时针旋转90度
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    
                    # 处理预热过程
                    if self.loading:
                        self.warmup_frames += 1
                        
                        if self.warmup_frames >= self.max_warmup_frames:
                            self.loading = False
                            self.ready = True
                    elif need_new_frame:
                        # 更新最后一帧的时间
                        self.last_frame_time = current_time
                    
                    # 更新帧缓冲区
                    self.frame_buffer = frame
                    return frame
                except Exception:
                    # 即使旋转失败也返回原始帧
                    self.frame_buffer = frame
                    return frame
            else:
                # 返回帧缓冲区中的最新帧，保持预览连续性
                return self.frame_buffer
        except Exception:
            # 捕获所有异常，避免影响主线程，返回帧缓冲区中的最新帧
            return self.frame_buffer
    
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
    
    def is_loading(self):
        """
        检查摄像头是否正在加载
        
        Returns:
            bool: 是否正在加载
        """
        return self.loading
    
    def is_ready(self):
        """
        检查摄像头是否准备就绪
        
        Returns:
            bool: 是否准备就绪
        """
        return self.ready
    
    def is_available(self):
        """
        检查摄像头是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.is_opened and self.cap is not None and self.ready
    
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
    
    def get_camera_info(self):
        """
        获取摄像头信息
        
        Returns:
            dict: 摄像头信息字典
        """
        info = {
            'camera_id': self.camera_id,
            'is_available': self.is_available(),
            'is_loading': self.is_loading(),
            'is_ready': self.is_ready(),
            'resolution': self.get_resolution(),
            'requested_width': self.width,
            'requested_height': self.height,
            'warmup_frames': self.warmup_frames,
            'max_warmup_frames': self.max_warmup_frames
        }
        return info
    
    @staticmethod
    def list_available_cameras():
        """
        列出所有可用的摄像头设备
        
        Returns:
            list: 可用摄像头ID列表
        """
        available_cameras = []
        print("扫描可用摄像头...")
        
        # 尝试打开前10个摄像头ID
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                print(f"Found camera {i}")
                cap.release()
        
        if available_cameras:
            print(f"Found {len(available_cameras)} available cameras")
        else:
            print("No available camera found")
        
        return available_cameras
    
    def __del__(self):
        """
        析构函数
        """
        self.release()
