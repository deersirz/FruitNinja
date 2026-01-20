#!/usr/bin/env python3
"""
基于MediaPipe的水果忍者游戏主入口文件
"""

import pygame
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.engine import GameEngine
from gesture.detector import HandDetector
from ui.renderer import Renderer
from audio.manager import AudioManager
from utils.logger import Logger


def main():
    """游戏主函数"""
    # 初始化日志
    logger = Logger()
    logger.log("开始初始化游戏...")
    
    try:
        # 初始化PyGame
        pygame.init()
        
        # 初始化音频管理器
        audio_manager = AudioManager()
        audio_manager.init()
        
        # 初始化手部检测器
        hand_detector = HandDetector(width=640, height=480)
        
        # 初始化渲染器
        renderer = Renderer(width=800, height=600)
        
        # 初始化游戏引擎
        game_engine = GameEngine(
            hand_detector=hand_detector,
            renderer=renderer,
            audio_manager=audio_manager,
            logger=logger
        )
        
        # 启动游戏主循环
        logger.log("游戏初始化完成，启动主循环...")
        game_engine.run()
        
    except Exception as e:
        logger.log(f"游戏初始化失败: {e}", level="error")
    finally:
        # 清理资源
        if 'hand_detector' in locals():
            hand_detector.close()
        
        if 'audio_manager' in locals():
            audio_manager.quit()
        
        pygame.quit()
        logger.log("游戏已退出")


if __name__ == "__main__":
    main()
