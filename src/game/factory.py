"""
游戏工厂模块
负责创建和管理游戏中的各种模块
"""

from game.fruit import FruitManager
from game.score import ScoreManager
from game.collision import CollisionDetector
from game.physics import PhysicsEngine
from gesture.tracker import GestureTracker
from gesture.mapper import GestureMapper


class GameFactory:
    """
    游戏工厂类
    负责创建和管理游戏中的各种模块
    """
    
    def __init__(self):
        """
        初始化游戏工厂
        """
        pass
    
    def create_fruit_manager(self):
        """
        创建水果管理器
        
        Returns:
            FruitManager: 水果管理器实例
        """
        return FruitManager()
    
    def create_score_manager(self):
        """
        创建分数管理器
        
        Returns:
            ScoreManager: 分数管理器实例
        """
        return ScoreManager()
    
    def create_collision_detector(self):
        """
        创建碰撞检测器
        
        Returns:
            CollisionDetector: 碰撞检测器实例
        """
        return CollisionDetector()
    
    def create_physics_engine(self):
        """
        创建物理引擎
        
        Returns:
            PhysicsEngine: 物理引擎实例
        """
        return PhysicsEngine()
    
    def create_gesture_system(self):
        """
        创建手势识别系统
        
        Returns:
            tuple: (GestureTracker, GestureMapper) 手势跟踪器和映射器实例
        """
        tracker = GestureTracker()
        mapper = GestureMapper(tracker)
        return tracker, mapper
    
    def create_all_modules(self):
        """
        创建所有游戏模块
        
        Returns:
            dict: 包含所有游戏模块的字典
        """
        # 创建手势系统
        gesture_tracker, gesture_mapper = self.create_gesture_system()
        
        return {
            'fruit_manager': self.create_fruit_manager(),
            'score_manager': self.create_score_manager(),
            'collision_detector': self.create_collision_detector(),
            'physics_engine': self.create_physics_engine(),
            'gesture_tracker': gesture_tracker,
            'gesture_mapper': gesture_mapper
        }
