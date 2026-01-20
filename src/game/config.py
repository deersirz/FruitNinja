"""
游戏配置模块
定义游戏的配置参数
"""


class GameConfig:
    """
    游戏配置类
    """
    # 游戏窗口配置
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "水果忍者"
    
    # 游戏配置
    FPS = 60
    GAME_DURATION = 60  # 游戏时长（秒）
    MAX_MISSED_FRUITS = 5  # 最大错过水果数
    
    # 水果配置
    FRUIT_TYPES = ['apple', 'banana', 'orange', 'watermelon', 'pineapple']
    FRUIT_RADIUS = 30
    FRUIT_SPAWN_RATE = 1.0  # 水果生成频率（秒）
    FRUIT_VELOCITY = 500  # 水果初始速度（像素/秒）
    FRUIT_ANGULAR_VELOCITY = 180  # 水果角速度（度/秒）
    
    # 物理配置
    GRAVITY = 980  # 重力加速度（像素/秒²）
    
    # 分数配置
    BASE_SCORE_PER_FRUIT = 10  # 每个水果的基础分数
    COMBO_MULTIPLIER = 1.5  # 连击倍数
    
    # 音效配置
    SOUND_VOLUME = 0.7
    
    # 难度配置
    DIFFICULTY_LEVEL = 1  # 1-简单，2-中等，3-困难
    
    # 手势识别配置
    SWIPE_THRESHOLD = 30  # 挥砍动作阈值
    
    # 渲染配置
    BACKGROUND_COLOR = (30, 30, 30)
    FRUIT_COLORS = {
        'apple': (255, 0, 0),
        'banana': (255, 255, 0),
        'orange': (255, 165, 0),
        'watermelon': (0, 255, 0),
        'pineapple': (255, 215, 0)
    }
    
    @classmethod
    def get_difficulty_settings(cls):
        """
        根据难度级别获取设置
        
        Returns:
            dict: 难度设置
        """
        if cls.DIFFICULTY_LEVEL == 1:
            return {
                'fruit_spawn_rate': cls.FRUIT_SPAWN_RATE,
                'fruit_velocity': cls.FRUIT_VELOCITY,
                'max_missed_fruits': cls.MAX_MISSED_FRUITS
            }
        elif cls.DIFFICULTY_LEVEL == 2:
            return {
                'fruit_spawn_rate': cls.FRUIT_SPAWN_RATE * 0.8,
                'fruit_velocity': cls.FRUIT_VELOCITY * 1.2,
                'max_missed_fruits': cls.MAX_MISSED_FRUITS - 1
            }
        else:
            return {
                'fruit_spawn_rate': cls.FRUIT_SPAWN_RATE * 0.6,
                'fruit_velocity': cls.FRUIT_VELOCITY * 1.5,
                'max_missed_fruits': cls.MAX_MISSED_FRUITS - 2
            }
