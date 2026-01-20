"""
游戏反馈模块
管理游戏事件的音频反馈
"""

from audio.sounds import SoundManager


class FeedbackSystem:
    """
    游戏反馈系统类
    """
    def __init__(self, sound_manager):
        """
        初始化游戏反馈系统
        
        Args:
            sound_manager (SoundManager): 音效管理器实例
        """
        self.sound_manager = sound_manager
        
        # 事件与音效的映射
        self.event_sound_map = {
            'fruit_sliced': 'slice',
            'game_start': 'start',
            'game_pause': 'pause',
            'game_resume': 'resume',
            'game_over': 'game_over',
            'combo': 'combo'
        }
    
    def process_event(self, event_type, **kwargs):
        """
        处理游戏事件，生成相应的反馈
        
        Args:
            event_type (str): 事件类型
            **kwargs: 事件参数
        """
        # 播放对应的音效
        if event_type in self.event_sound_map:
            sound_name = self.event_sound_map[event_type]
            self.sound_manager.play_sound(sound_name)
        
        # 处理特殊事件
        if event_type == 'combo':
            # 处理连击事件
            combo = kwargs.get('combo', 0)
            if combo > 5:
                # 播放连击音效
                self.sound_manager.play_sound('combo')
        elif event_type == 'fruit_sliced':
            # 处理水果切割事件
            pass
        elif event_type == 'game_over':
            # 处理游戏结束事件
            pass
    
    def register_event(self, event_type, sound_name):
        """
        注册新的事件与音效映射
        
        Args:
            event_type (str): 事件类型
            sound_name (str): 音效名称
        """
        self.event_sound_map[event_type] = sound_name
    
    def unregister_event(self, event_type):
        """
        注销事件与音效映射
        
        Args:
            event_type (str): 事件类型
        """
        if event_type in self.event_sound_map:
            del self.event_sound_map[event_type]
    
    def get_event_sound(self, event_type):
        """
        获取事件对应的音效
        
        Args:
            event_type (str): 事件类型
            
        Returns:
            str: 音效名称
        """
        return self.event_sound_map.get(event_type, None)
