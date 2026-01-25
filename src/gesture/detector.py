"""
手部检测器模块
兼容 MediaPipe 0.8.x (classic) 与 0.10+ (Tasks API)
"""
import cv2
import numpy as np

# ------------------ 版本探测 ------------------
try:
    import mediapipe as mp
    # 能 import solutions 说明是经典版
    mp.solutions.hands
    _USE_CLASSIC = True
except (ImportError, AttributeError):
    _USE_CLASSIC = False

if not _USE_CLASSIC:
    # 新版 Tasks 路径
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python import vision as mp_vision

# （可选）把 drawing_utils 也一起拷到本地，方便画线
# from drawing_utils import draw_landmarks   # 如需可视化可打开


class HandDetector:
    """
    手部检测器类
    对外接口与旧版完全一致，内部自动选择 MediaPipe 实现
    """

    def __init__(self, width=640, height=480):
        self.width, self.height = width, height

        # 1. 初始化 MediaPipe Hands / HandLandmarker
        if _USE_CLASSIC:
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
        else:
            base_options = mp_tasks.BaseOptions(
                model_asset_path=r'src\gesture/hand_landmarker.task'  # 官方模型，第一次需要下载
            )
            options = mp_vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,
                min_hand_detection_confidence=0.7,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.landmarker = mp_vision.HandLandmarker.create_from_options(options)

        # 2. 摄像头
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # ---------------------------- 对外接口保持完全一致 ----------------------------
    def detect_hands(self, frame):
        """返回格式与旧版 100% 相同"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detection_result = {
            'has_hand': False,
            'landmarks': [],
            'frame': frame
        }

        if _USE_CLASSIC:
            results = self.hands.process(rgb)
            if results.multi_hand_landmarks:
                detection_result['has_hand'] = True
                for hl in results.multi_hand_landmarks:
                    detection_result['landmarks'] = [
                        {'x': int(lm.x * self.width), 'y': int(lm.y * self.height)}
                        for lm in hl.landmark
                    ]
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self.landmarker.detect(mp_image)
            if result.hand_landmarks:
                detection_result['has_hand'] = True
                # 只取第一只手（num_hands=1）
                landmarks = result.hand_landmarks[0]
                detection_result['landmarks'] = [
                    {'x': int(lm.x * self.width), 'y': int(lm.y * self.height)}
                    for lm in landmarks
                ]
        return detection_result

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)

    def close(self):
        if self.cap.isOpened():
            self.cap.release()
        if _USE_CLASSIC:
            self.hands.close()
        else:
            self.landmarker.close()