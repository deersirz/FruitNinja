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
    WINDOW_TITLE = "Fruit Ninja"
    
    # 游戏状态
    GAME_STATES = {
        'TITLE': 'TITLE',
        'COUNTDOWN': 'COUNTDOWN',
        'PLAYING': 'PLAYING',
        'GAME_OVER': 'GAME_OVER'
    }
    
    # 游戏配置
    FPS = 60
    DEFAULT_GAME_DURATION = 60  # 默认游戏时长（秒）
    INITIAL_LIVES = 3  # 初始生命数
    MAX_MISSED_FRUITS = 5  # 最大错过水果数
    
    # 水果配置
    FRUIT_TYPES = ['apple', 'banana', 'peach', 'watermelon', 'strawberry']
    FRUIT_RADIUS = 40  # 增大水果尺寸，提升容错率
    FRUIT_SPAWN_RATE = 1.5  # 水果生成频率（秒）
    FRUIT_VELOCITY = 500  # 水果初始速度（像素/秒）
    FRUIT_ANGULAR_VELOCITY = 180  # 水果角速度（度/秒）
    
    # 物理配置
    GRAVITY = 720  # 重力加速度（像素/秒²），增强下落真实感
    
    # 分数配置
    BASE_SCORE_PER_FRUIT = 10  # 每个水果的基础分数
    COMBO_MULTIPLIER = 1.5  # 连击倍数
    
    # 音效配置
    SOUND_VOLUME = 0.7
    
    # 难度配置
    DIFFICULTY_LEVEL = 1  # 1-简单，2-中等，3-困难
    
    # 手势识别配置
    SWIPE_THRESHOLD = 30  # 挥砍动作阈值
    NOD_THRESHOLD = 2  # 点头开始游戏的阈值
    
    # 慢动作配置
    SLOW_MOTION_DURATION = 60  # 慢动作持续时间（帧）
    
    # 颜色配置
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    GOLD = (255, 215, 0)
    
    # 渲染配置
    BACKGROUND_COLOR = (30, 30, 30)
    FRUIT_COLORS = {
        'apple': (255, 0, 0),
        'banana': (255, 255, 0),
        'peach': (255, 192, 203),
        'watermelon': (0, 255, 0),
        'strawberry': (255, 0, 0)
    }
    
    # 粒子颜色配置
    PARTICLE_COLORS = {
        0: (255, 0, 0),      # apple
        1: (255, 255, 0),    # banana
        2: (255, 192, 203),  # peach
        3: (0, 255, 0),      # watermelon
        4: (255, 0, 0)       # strawberry
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
    
    @classmethod
    def get_game_state(cls, state_name):
        """
        获取游戏状态
        
        Args:
            state_name: 状态名称
            
        Returns:
            str: 游戏状态
        """
        return cls.GAME_STATES.get(state_name, 'TITLE')
