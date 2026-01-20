"""
日志工具模块
记录游戏运行过程中的日志信息
"""

import time
import os


class Logger:
    """
    日志记录器类
    """
    def __init__(self, log_file=None, log_level="INFO"):
        """
        初始化日志记录器
        
        Args:
            log_file (str): 日志文件路径，如果为None则只输出到控制台
            log_level (str): 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        self.log_file = log_file
        self.log_level = log_level.upper()
        
        # 日志级别映射
        self.level_map = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        
        # 创建日志目录（如果需要）
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
        
        # 记录初始化日志
        self.log("Logger initialized", level="INFO")
    
    def _should_log(self, level):
        """
        检查是否应该记录该级别的日志
        
        Args:
            level (str): 日志级别
            
        Returns:
            bool: 是否应该记录
        """
        current_level = self.level_map.get(self.log_level, 1)
        log_level = self.level_map.get(level.upper(), 1)
        return log_level >= current_level
    
    def log(self, message, level="INFO"):
        """
        记录日志
        
        Args:
            message (str): 日志消息
            level (str): 日志级别
        """
        level = level.upper()
        
        if not self._should_log(level):
            return
        
        # 格式化日志消息
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # 输出到控制台
        print(log_message)
        
        # 输出到文件
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"Failed to write to log file: {e}")
    
    def debug(self, message):
        """
        记录DEBUG级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.log(message, level="DEBUG")
    
    def info(self, message):
        """
        记录INFO级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.log(message, level="INFO")
    
    def warning(self, message):
        """
        记录WARNING级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.log(message, level="WARNING")
    
    def error(self, message):
        """
        记录ERROR级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.log(message, level="ERROR")
    
    def critical(self, message):
        """
        记录CRITICAL级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.log(message, level="CRITICAL")
    
    def set_log_level(self, level):
        """
        设置日志级别
        
        Args:
            level (str): 日志级别
        """
        if level.upper() in self.level_map:
            self.log_level = level.upper()
            self.log(f"Log level set to {self.log_level}", level="INFO")
        else:
            self.log(f"Invalid log level: {level}", level="WARNING")
    
    def set_log_file(self, log_file):
        """
        设置日志文件
        
        Args:
            log_file (str): 日志文件路径
        """
        self.log_file = log_file
        
        # 创建日志目录（如果需要）
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
        
        self.log(f"Log file set to {self.log_file}", level="INFO")
    
    def get_log_level(self):
        """
        获取当前日志级别
        
        Returns:
            str: 当前日志级别
        """
        return self.log_level
    
    def get_log_file(self):
        """
        获取当前日志文件路径
        
        Returns:
            str: 当前日志文件路径
        """
        return self.log_file


# 创建默认的日志记录器实例
default_logger = Logger()


def get_logger():
    """
    获取默认的日志记录器
    
    Returns:
        Logger: 默认的日志记录器实例
    """
    return default_logger
