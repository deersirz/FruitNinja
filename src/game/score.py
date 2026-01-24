"""
计分系统模块
管理游戏分数和游戏状态
"""

from game.config import GameConfig


class ScoreManager:
    """
    分数管理器类
    """
    def __init__(self):
        """
        初始化分数管理器
        """
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.missed_fruits = 0
        self.game_time = 0
        self.game_over = False
        self.start_time = 0
    
    def update_score(self, fruit):
        """
        更新分数
        
        Args:
            fruit (Fruit): 被切割的水果
        """
        # 增加分数
        fruit_score = GameConfig.BASE_SCORE_PER_FRUIT
        
        # 增加连击数
        self.combo += 1
        
        # 计算连击倍数
        combo_multiplier = 1 + (self.combo - 1) * GameConfig.COMBO_MULTIPLIER
        
        # 计算最终分数
        final_score = int(fruit_score * combo_multiplier)
        self.score += final_score
        
        # 更新最大连击数
        if self.combo > self.max_combo:
            self.max_combo = self.combo
    
    def reset_combo(self):
        """
        重置连击数
        """
        self.combo = 0
    
    def increment_missed_fruits(self):
        """
        增加错过的水果数
        """
        self.missed_fruits += 1
        
        # 重置连击数
        self.reset_combo()
        
        # 检查游戏是否结束
        if self.missed_fruits >= GameConfig.MAX_MISSED_FRUITS:
            self.game_over = True
    
    def update_game_time(self, dt):
        """
        更新游戏时间
        
        Args:
            dt (float): 时间步长（秒）
        """
        self.game_time += dt
        
        # 检查游戏是否结束
        if self.game_time >= GameConfig.GAME_DURATION:
            self.game_over = True
    
    def reset(self):
        """
        重置分数管理器
        """
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.missed_fruits = 0
        self.game_time = 0
        self.game_over = False
        self.start_time = 0
    
    def get_score(self):
        """
        获取当前分数
        
        Returns:
            int: 当前分数
        """
        return self.score
    
    def get_combo(self):
        """
        获取当前连击数
        
        Returns:
            int: 当前连击数
        """
        return self.combo
    
    def get_max_combo(self):
        """
        获取最大连击数
        
        Returns:
            int: 最大连击数
        """
        return self.max_combo
    
    def get_missed_fruits(self):
        """
        获取错过的水果数
        
        Returns:
            int: 错过的水果数
        """
        return self.missed_fruits
    
    def get_game_time(self):
        """
        获取游戏时间
        
        Returns:
            float: 游戏时间（秒）
        """
        return self.game_time
    
    def is_game_over(self):
        """
        判断游戏是否结束
        
        Returns:
            bool: 游戏是否结束
        """
        return self.game_over
    
    def get_game_stats(self):
        """
        获取游戏统计信息
        
        Returns:
            dict: 游戏统计信息
        """
        return {
            'score': self.score,
            'combo': self.combo,
            'max_combo': self.max_combo,
            'missed_fruits': self.missed_fruits,
            'game_time': self.game_time,
            'game_over': self.game_over
        }
