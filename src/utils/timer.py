"""
计时器工具模块
提供游戏中的计时功能
"""

import time


class Timer:
    """
    计时器类
    """
    def __init__(self):
        """
        初始化计时器
        """
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
    
    def start(self):
        """
        开始计时
        """
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True
    
    def pause(self):
        """
        暂停计时
        """
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
    
    def reset(self):
        """
        重置计时器
        """
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
    
    def get_elapsed(self):
        """
        获取已经过的时间
        
        Returns:
            float: 已经过的时间（秒）
        """
        if self.running:
            return time.time() - self.start_time
        else:
            return self.elapsed_time
    
    def is_running(self):
        """
        检查计时器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.running
    
    def restart(self):
        """
        重启计时器
        """
        self.reset()
        self.start()
    
    def get_elapsed_ms(self):
        """
        获取已经过的时间（毫秒）
        
        Returns:
            int: 已经过的时间（毫秒）
        """
        return int(self.get_elapsed() * 1000)
    
    def get_elapsed_minutes(self):
        """
        获取已经过的时间（分钟）
        
        Returns:
            float: 已经过的时间（分钟）
        """
        return self.get_elapsed() / 60
    
    def format_time(self, format_str="%H:%M:%S"):
        """
        格式化时间
        
        Args:
            format_str (str): 时间格式字符串
            
        Returns:
            str: 格式化后的时间字符串
        """
        elapsed = self.get_elapsed()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed % 1) * 1000)
        
        # 根据格式字符串格式化时间
        if "%H" in format_str:
            format_str = format_str.replace("%H", f"{hours:02d}")
        if "%M" in format_str:
            format_str = format_str.replace("%M", f"{minutes:02d}")
        if "%S" in format_str:
            format_str = format_str.replace("%S", f"{seconds:02d}")
        if "%ms" in format_str:
            format_str = format_str.replace("%ms", f"{milliseconds:03d}")
        
        return format_str


class CountdownTimer(Timer):
    """
    倒计时计时器类
    """
    def __init__(self, duration):
        """
        初始化倒计时计时器
        
        Args:
            duration (float): 倒计时持续时间（秒）
        """
        super().__init__()
        self.duration = duration
    
    def get_remaining(self):
        """
        获取剩余时间
        
        Returns:
            float: 剩余时间（秒）
        """
        remaining = self.duration - self.get_elapsed()
        return max(0, remaining)
    
    def is_finished(self):
        """
        检查倒计时是否结束
        
        Returns:
            bool: 是否结束
        """
        return self.get_remaining() <= 0
    
    def get_progress(self):
        """
        获取倒计时进度
        
        Returns:
            float: 进度（0-1）
        """
        if self.duration <= 0:
            return 1.0
        progress = self.get_elapsed() / self.duration
        return min(1.0, progress)
    
    def reset(self, duration=None):
        """
        重置倒计时计时器
        
        Args:
            duration (float): 新的倒计时持续时间，如果为None则保持原 duration
        """
        if duration is not None:
            self.duration = duration
        super().reset()
