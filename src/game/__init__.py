"""
游戏核心模块
"""

from .engine import GameEngine
from .fruit import Fruit, FruitManager
from .physics import PhysicsEngine
from .collision import CollisionDetector
from .score import ScoreManager
from .config import GameConfig

__all__ = [
    'GameEngine',
    'Fruit',
    'FruitManager',
    'PhysicsEngine',
    'CollisionDetector',
    'ScoreManager',
    'GameConfig'
]
