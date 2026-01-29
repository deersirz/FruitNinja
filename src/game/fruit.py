"""
水果模块
define水果对象和水果管理器
"""

import random
import math
from game.config import GameConfig
from game.physics import PhysicsEngine


class Fruit:
    """
    水果类
    """
    def __init__(self, x, y, fruit_type):
        """
        初始化水果对象
        
        Args:
            x (float): 水果x坐标
            y (float): 水果y坐标
            fruit_type (str): 水果类型
        """
        self.x = x
        self.y = y
        self.radius = GameConfig.FRUIT_RADIUS
        self.type = fruit_type
        
        # 设置颜色（炸弹使用红色）
        if fruit_type == 'bomb':
            self.color = (255, 0, 0)  # 炸弹为红色
        else:
            self.color = GameConfig.FRUIT_COLORS.get(fruit_type, (255, 255, 255))
        
        # 定义中心区域（200*100像素）
        CENTER_REGION_WIDTH = 200
        CENTER_REGION_HEIGHT = 100
        CENTER_REGION_X_MIN = GameConfig.WINDOW_WIDTH // 2 - CENTER_REGION_WIDTH // 2
        CENTER_REGION_X_MAX = GameConfig.WINDOW_WIDTH // 2 + CENTER_REGION_WIDTH // 2
        CENTER_REGION_Y_MIN = GameConfig.WINDOW_HEIGHT // 2 - CENTER_REGION_HEIGHT // 2
        CENTER_REGION_Y_MAX = GameConfig.WINDOW_HEIGHT // 2 + CENTER_REGION_HEIGHT // 2
        
        # 计算中心区域的中间点
        center_x = (CENTER_REGION_X_MIN + CENTER_REGION_X_MAX) // 2
        center_y = (CENTER_REGION_Y_MIN + CENTER_REGION_Y_MAX) // 2
        
        # 实现路径强制约束机制，确保所有水果和炸弹经过中心区域
        # 1. 实现横坐标参数动态限制算法
        # 根据初始x坐标计算水平方向参数范围
        horizontal_param_range = self._calculate_horizontal_param_range(x)
        
        # 2. 计算确保经过中心区域的轨迹
        velocity_x, velocity_y = self._calculate_trajectory(
            x, y, center_x, center_y, horizontal_param_range
        )
        
        # 3. 保持原有的随机速度生成机制
        speed = GameConfig.FRUIT_VELOCITY + 400
        
        # 4. 计算速度向量
        self.velocity_x = velocity_x * speed
        self.velocity_y = velocity_y * speed
        
        # 5. 随机角速度
        self.angular_velocity = random.uniform(-GameConfig.FRUIT_ANGULAR_VELOCITY, 
                                               GameConfig.FRUIT_ANGULAR_VELOCITY)
        self.rotation = 0
        
        self.sliced = False
        self.sliced_time = 0
    
    def _calculate_horizontal_param_range(self, x):
        """
        根据初始x坐标计算水平方向参数范围
        
        Args:
            x (float): 初始x坐标
            
        Returns:
            tuple: (min_horizontal_param, max_horizontal_param)
        """
        window_width = GameConfig.WINDOW_WIDTH
        center_x = window_width // 2
        
        # 根据x坐标位置设置不同的水平方向参数范围
        if x < center_x - 100:
            # 左侧生成，需要向右运动
            return (0.3, 0.7)  # 正方向，较大值
        elif x > center_x + 100:
            # 右侧生成，需要向左运动
            return (-0.7, -0.3)  # 负方向，较小值
        else:
            # 中间生成，可左右运动
            return (-0.5, 0.5)
    
    def _calculate_trajectory(self, start_x, start_y, center_x, center_y, horizontal_param_range):
        """
        计算确保经过中心区域的轨迹
        
        Args:
            start_x (float): 起始x坐标
            start_y (float): 起始y坐标
            center_x (float): 中心区域x坐标
            center_y (float): 中心区域y坐标
            horizontal_param_range (tuple): 水平方向参数范围
            
        Returns:
            tuple: (velocity_x, velocity_y) 归一化的速度向量
        """
        # 1. 实现轴对称轨迹分布
        # 计算水果生成点到屏幕左右两端的距离
        distance_to_left = start_x
        distance_to_right = GameConfig.WINDOW_WIDTH - start_x
        
        # 确定距离更远的一端作为对称轴的另一端点
        if distance_to_left > distance_to_right:
            # 左边更远，对称轴另一端在左侧
            symmetry_end_x = 0
        else:
            # 右边更远，对称轴另一端在右侧
            symmetry_end_x = GameConfig.WINDOW_WIDTH
        
        # 计算对称轴的中点（生成点和更远端点的中点）
        symmetry_axis_x = (start_x + symmetry_end_x) / 2
        
        # 2. 计算从起始位置到中心区域的向量
        dx = center_x - start_x
        dy = center_y - start_y
        
        # 3. 计算向量长度
        length = math.sqrt(dx**2 + dy**2)
        
        # 4. 归一化向量
        if length > 0:
            normalized_dx = dx / length
            normalized_dy = dy / length
        else:
            # 如果已经在中心区域，使用默认向上的方向
            normalized_dx = 0
            normalized_dy = -1
        
        # 5. 根据水平参数范围调整水平方向
        min_horizontal, max_horizontal = horizontal_param_range
        
        # 计算水平方向参数，确保轨迹沿对称轴对称分布
        horizontal_param = random.uniform(min_horizontal, max_horizontal)
        
        # 6. 调整速度向量，确保水平方向符合参数范围
        # 保持垂直方向基本不变，调整水平方向
        velocity_x = horizontal_param
        
        # 计算垂直方向，确保整体速度向量长度为1
        velocity_y = -math.sqrt(1 - velocity_x**2)
        
        # 7. 添加小范围的随机偏移，保持随机性
        random_offset_x = random.uniform(-0.1, 0.1)
        random_offset_y = random.uniform(-0.1, 0.1)
        
        velocity_x += random_offset_x
        velocity_y += random_offset_y
        
        # 8. 精确控制最高点高度，确保在指定范围内
        # 屏幕高度的五分之一：600/5 = 120像素（从顶部开始计算）
        # 从底部开始计算：600 - 120 = 480像素
        max_max_height = 480
        
        # 屏幕高度的三分之一：600/3 = 200像素（从顶部开始计算）
        # 从底部开始计算：600 - 200 = 400像素
        min_max_height = 400
        
        # 9. 计算所需的初始垂直速度范围
        # 根据物理公式：h = (v_y^2) / (2 * g)
        # 这里h是从起始位置到最高高度的距离
        g = GameConfig.GRAVITY
        
        # 计算最小和最大所需高度
        min_required_height = min_max_height - start_y
        max_required_height = max_max_height - start_y
        
        # 确保高度值为正数
        min_required_height = max(min_required_height, 100)  # 至少需要100像素的高度
        max_required_height = max(max_required_height, 100)  # 至少需要100像素的高度
        
        # 计算最小和最大初始垂直速度（绝对值）
        min_vertical_velocity = math.sqrt(2 * g * min_required_height)
        max_vertical_velocity = math.sqrt(2 * g * max_required_height)
        
        # 10. 确保垂直速度在指定范围内
        # 计算当前速度向量的垂直分量
        current_speed = GameConfig.FRUIT_VELOCITY + 400
        current_vertical_velocity = velocity_y * current_speed
        
        # 如果垂直速度过大，调整速度向量
        if abs(current_vertical_velocity) > max_vertical_velocity:
            # 计算所需的垂直速度比例
            velocity_y = -max_vertical_velocity / current_speed
            # 重新计算水平速度，确保速度向量长度为1
            velocity_x = math.sqrt(1 - velocity_y**2)
            # 根据水平参数范围调整水平方向和符号
            min_horizontal, max_horizontal = horizontal_param_range
            # 确定水平速度的符号
            if min_horizontal < 0 and max_horizontal < 0:
                # 右侧生成，水平速度应该为负
                velocity_x = -velocity_x
            elif min_horizontal > 0 and max_horizontal > 0:
                # 左侧生成，水平速度应该为正
                pass  # 保持速度为正
            # 确保水平速度在参数范围内
            velocity_x = max(min_horizontal, min(max_horizontal, velocity_x))
            # 重新计算垂直速度，确保速度向量长度为1
            velocity_y = -math.sqrt(1 - velocity_x**2)
        # 如果垂直速度过小，调整速度向量
        elif abs(current_vertical_velocity) < min_vertical_velocity:
            # 计算所需的垂直速度比例
            velocity_y = -min_vertical_velocity / current_speed
            # 重新计算水平速度，确保速度向量长度为1
            velocity_x = math.sqrt(1 - velocity_y**2)
            # 根据水平参数范围调整水平方向和符号
            min_horizontal, max_horizontal = horizontal_param_range
            # 确定水平速度的符号
            if min_horizontal < 0 and max_horizontal < 0:
                # 右侧生成，水平速度应该为负
                velocity_x = -velocity_x
            elif min_horizontal > 0 and max_horizontal > 0:
                # 左侧生成，水平速度应该为正
                pass  # 保持速度为正
            # 确保水平速度在参数范围内
            velocity_x = max(min_horizontal, min(max_horizontal, velocity_x))
            # 重新计算垂直速度，确保速度向量长度为1
            velocity_y = -math.sqrt(1 - velocity_x**2)
        
        # 11. 重新归一化
        new_length = math.sqrt(velocity_x**2 + velocity_y**2)
        if new_length > 0:
            velocity_x /= new_length
            velocity_y /= new_length
        
        return velocity_x, velocity_y
    
    def _check_center_pass(self, x, y):
        """
        检查水果是否经过中心区域
        
        Args:
            x (float): 当前x坐标
            y (float): 当前y坐标
            
        Returns:
            bool: 是否经过中心区域
        """
        # 定义中心区域（200*100像素）
        CENTER_REGION_WIDTH = 200
        CENTER_REGION_HEIGHT = 100
        CENTER_REGION_X_MIN = GameConfig.WINDOW_WIDTH // 2 - CENTER_REGION_WIDTH // 2
        CENTER_REGION_X_MAX = GameConfig.WINDOW_WIDTH // 2 + CENTER_REGION_WIDTH // 2
        CENTER_REGION_Y_MIN = GameConfig.WINDOW_HEIGHT // 2 - CENTER_REGION_HEIGHT // 2
        CENTER_REGION_Y_MAX = GameConfig.WINDOW_HEIGHT // 2 + CENTER_REGION_HEIGHT // 2
        
        # 检查是否在中心区域内
        return (CENTER_REGION_X_MIN - self.radius <= x <= CENTER_REGION_X_MAX + self.radius and
                CENTER_REGION_Y_MIN - self.radius <= y <= CENTER_REGION_Y_MAX + self.radius)
    
    def _correct_trajectory(self):
        """
        修正轨迹，确保水果经过中心区域
        """
        # 定义中心区域
        CENTER_REGION_WIDTH = 200
        CENTER_REGION_HEIGHT = 100
        center_x = GameConfig.WINDOW_WIDTH // 2
        center_y = GameConfig.WINDOW_HEIGHT // 2
        
        # 计算从当前位置到中心区域的向量
        dx = center_x - self.x
        dy = center_y - self.y
        
        # 计算向量长度
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            # 归一化向量
            normalized_dx = dx / length
            normalized_dy = dy / length
            
            # 计算当前速度向量长度
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            
            # 重新计算速度向量，指向中心区域
            # 保持当前速度大小，调整方向
            self.velocity_x = normalized_dx * current_speed * 0.8
            self.velocity_y = normalized_dy * current_speed * 0.8
            
            # 确保有向上的速度分量
            if self.velocity_y > 0:
                self.velocity_y = -abs(self.velocity_y)
        
    def update(self, dt, physics_engine=None):
        """
        更新水果状态
        
        Args:
            dt (float): 时间步长（秒）
            physics_engine (PhysicsEngine, optional): 物理引擎实例
        """
        if not self.sliced:
            if physics_engine:
                # 使用物理引擎更新
                physics_engine.apply_physics(self, dt)
            else:
                # 内置物理更新（备用）
                # 更新位置
                self.x += self.velocity_x * dt
                self.y += self.velocity_y * dt
                
                # 应用重力
                self.velocity_y += GameConfig.GRAVITY * dt
                
                # 更新旋转
                self.rotation += self.angular_velocity * dt
                
                # 移除碰撞反弹机制，保留边界检查用于判断水果是否超出屏幕
                # 水果触碰边界后不会反弹，而是直接移出屏幕
        
        # 检查是否经过中心区域，只标记，不进行轨迹修正
        # 移除可能导致边界反弹的轨迹修正逻辑
        if not self.sliced and not hasattr(self, 'passed_center'):
            if self._check_center_pass(self.x, self.y):
                # 标记为已经过中心区域
                self.passed_center = True
            # 不再进行轨迹修正，避免边界反弹
            
    def draw(self, surface):
        """
        绘制水果
        
        Args:
            surface (pygame.Surface): 绘制表面
        """
        # 这里将在renderer.py中实现具体的绘制逻辑
        pass
    
    def slice(self, slice_time=0):
        """
        标记水果为已切割
        
        Args:
            slice_time (float, optional): 切割时间（秒）
        """
        self.sliced = True
        self.sliced_time = slice_time
        
    def is_off_screen(self):
        """
        判断水果是否超出屏幕
        
        Returns:
            bool: 是否超出屏幕
        """
        return (self.x < -self.radius or 
                self.x > GameConfig.WINDOW_WIDTH + self.radius or 
                self.y > GameConfig.WINDOW_HEIGHT + self.radius)


class FruitManager:
    """
    水果管理器类
    """
    def __init__(self, spawn_rate=GameConfig.FRUIT_SPAWN_RATE):
        """
        初始化水果管理器
        
        Args:
            spawn_rate (float): 水果生成频率（秒）
        """
        self.fruits = []
        self.spawn_rate = spawn_rate
        self.last_spawn_time = 0
        self.fruit_types = GameConfig.FRUIT_TYPES
        
        # 引导阶段相关
        self.guide_phase = True
        self.guide_start_time = 0
        self.guide_fruits = ['apple', 'apple', 'strawberry', 'strawberry', 'banana', 'banana', 'watermelon', 'watermelon', 'bomb']
        self.guide_index = 0
        
    def update(self, dt, current_time, physics_engine=None):
        """
        更新水果管理器状态
        
        Args:
            dt (float): 时间步长（秒）
            current_time (float): 当前时间（秒）
            physics_engine (PhysicsEngine, optional): 物理引擎实例
        """
        # 初始化引导开始时间
        if self.guide_phase and self.guide_start_time == 0:
            self.guide_start_time = current_time
        
        # 检查引导阶段是否结束
        if self.guide_phase and current_time - self.guide_start_time >= 5:
            self.guide_phase = False
            print("引导阶段结束，开始正常水果生成")
        
        # 生成新水果
        if current_time - self.last_spawn_time > self.spawn_rate:
            if self.guide_phase and self.guide_index < len(self.guide_fruits):
                # 引导阶段：按顺序生成特定水果
                self.spawn_guide_fruit()
            else:
                # 正常阶段：随机生成水果
                self.spawn_fruit()
            self.last_spawn_time = current_time
        
        # 更新水果状态
        for fruit in self.fruits[:]:
            fruit.update(dt, physics_engine)
            
            # 移除已切割的水果（延迟移除，以便特效显示）
            if fruit.sliced and current_time - fruit.sliced_time > 1.0:
                self.fruits.remove(fruit)
    
    def spawn_fruit(self):
        """
        生成新水果
        """
        # 计算屏幕总宽度的十分之一
        screen_tenth = GameConfig.WINDOW_WIDTH / 10
        # 计算中线位置
        center_line = GameConfig.WINDOW_WIDTH / 2
        
        # 计算限制区域的左右边界
        limit_left = center_line - screen_tenth
        limit_right = center_line + screen_tenth
        
        # 生成不在限制区域内的位置
        while True:
            # 随机位置（屏幕底部）
            x = random.randint(GameConfig.FRUIT_RADIUS, 
                              GameConfig.WINDOW_WIDTH - GameConfig.FRUIT_RADIUS)
            
            # 检查是否在限制区域外
            if x < limit_left or x > limit_right:
                break
        
        y = GameConfig.WINDOW_HEIGHT
        
        # 随机水果类型（80%水果，20%炸弹）
        if random.random() < 0.8:
            fruit_type = random.choice(self.fruit_types)
        else:
            fruit_type = 'bomb'
        
        # 创建水果对象
        fruit = Fruit(x, y, fruit_type)
        self.fruits.append(fruit)
    
    def spawn_guide_fruit(self):
        """
        在引导阶段生成特定水果
        """
        # 计算屏幕总宽度的十分之一
        screen_tenth = GameConfig.WINDOW_WIDTH / 10
        # 计算中线位置
        center_line = GameConfig.WINDOW_WIDTH / 2
        
        # 计算限制区域的左右边界
        limit_left = center_line - screen_tenth
        limit_right = center_line + screen_tenth
        
        # 生成不在限制区域内的位置
        while True:
            # 随机位置（屏幕底部）
            x = random.randint(GameConfig.FRUIT_RADIUS, 
                              GameConfig.WINDOW_WIDTH - GameConfig.FRUIT_RADIUS)
            
            # 检查是否在限制区域外
            if x < limit_left or x > limit_right:
                break
        
        y = GameConfig.WINDOW_HEIGHT
        
        # 获取当前引导水果类型
        fruit_type = self.guide_fruits[self.guide_index]
        
        # 创建水果对象
        fruit = Fruit(x, y, fruit_type)
        self.fruits.append(fruit)
        
        # 移动到下一个引导水果
        self.guide_index += 1
        print(f"引导阶段生成: {fruit_type}")
    
    def get_fruits(self):
        """
        获取水果列表
        
        Returns:
            list: 水果列表
        """
        return self.fruits
    
    def remove_fruit(self, fruit):
        """
        移除水果
        
        Args:
            fruit (Fruit): 要移除的水果
        """
        if fruit in self.fruits:
            self.fruits.remove(fruit)
    
    def clear_fruits(self):
        """
        清空所有水果
        """
        self.fruits.clear()



