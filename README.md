# 基于MediaPipe的水果忍者游戏

## 项目介绍

本项目是一款基于MediaPipe手势识别的水果忍者游戏，使用Python技术栈开发。玩家通过摄像头捕捉手部动作，在屏幕上切割水果获得分数，体验类似经典水果忍者游戏的玩法。

### 主要特性

- **手势识别**：使用MediaPipe Hands实时检测手部关键点，识别挥砍动作
- **物理模拟**：实现水果的抛物线运动和旋转效果
- **视觉特效**：切割水果时的粒子特效和动画
- **音频反馈**：游戏音效和背景音乐
- **计分系统**：记录玩家分数和游戏状态

## 技术栈

| 类别 | 技术/库 | 版本 |
|------|---------|------|
| 编程语言 | Python | 3.8+ |
| 手势识别 | MediaPipe Hands | 0.10.32 |
| 图形渲染 | PyGame | 2.5.2 |
| 摄像头捕获 | OpenCV | 4.8.1.78 |
| 数学计算 | NumPy | 1.26.4 |

## 项目结构

```
fruit-ninja/
├── main.py                # 游戏主入口文件
├── requirements.txt       # 项目依赖文件
├── README.md              # 项目说明文档
├── 项目架构.md             # 架构设计文档
├── assets/                # 静态资源目录
│   ├── fonts/             # 字体资源
│   │   ├── Artier.ttf     # 主要游戏字体
│   │   └── NotoSansSC.ttf # 中文字体
│   ├── images/            # 图片资源
│   │   ├── title.png      # 游戏标题图片
│   │   └── background.jpg # 游戏背景图片
│   └── sounds/            # 音频资源
│       ├── effects/       # 音效文件
│       └── music/         # 背景音乐
└── src/                   # 源代码目录
    ├── gesture/           # 手势识别模块
    │   ├── __init__.py     # 模块初始化文件
    │   ├── detector.py     # MediaPipe Hands集成
    │   ├── tracker.py      # 手势轨迹跟踪
    │   ├── mapper.py       # 手势与操作映射
    │   └── hand_landmarker.task # MediaPipe手部检测模型
    ├── game/              # 游戏核心模块
    │   ├── __init__.py     # 模块初始化文件
    │   ├── engine.py       # 游戏引擎
    │   ├── fruit.py        # 水果对象
    │   ├── physics.py      # 物理系统
    │   ├── collision.py    # 碰撞检测
    │   ├── score.py        # 计分系统
    │   ├── config.py       # 游戏配置参数
    │   └── factory.py      # 游戏模块工厂
    ├── ui/                # 界面模块
    │   ├── resource/       # UI资源目录
    │   │   └── font/        # 字体资源
    │   ├── __init__.py     # 模块初始化文件
    │   ├── renderer.py     # PyGame渲染器
    │   ├── effects.py      # 视觉效果
    │   ├── layout.py       # 界面布局
    │   └── fonts.py        # 字体管理
    ├── audio/             # 音频模块
    │   ├── __init__.py     # 模块初始化文件
    │   ├── manager.py      # 音频管理器
    │   ├── feedback.py     # 游戏反馈机制
    │   └── sounds.py       # 音效定义
    └── utils/             # 工具模块
        ├── __init__.py     # 模块初始化文件
        ├── camera.py       # 摄像头工具
        ├── timer.py        # 计时器工具
        ├── logger.py       # 日志工具
        └── resource.py     # 资源管理
```

## 安装说明

### 1. 环境要求

- Python 3.8 或更高版本
- 支持摄像头的设备
- Windows、macOS 或 Linux 操作系统

### 2. 安装依赖

使用pip安装项目依赖：

```bash
pip install -r requirements.txt
```

### 3. 运行游戏

直接运行主入口文件：

```bash
python main.py
```

## 游戏操作

1. **开始游戏**：运行游戏后，点击屏幕开始游戏
2. **切割水果**：使用手势在屏幕上挥砍，切割飞出来的水果
3. **游戏结束**：当错过一定数量的水果后，游戏结束
4. **重新开始**：游戏结束后，点击屏幕重新开始

## 游戏设置

游戏设置可以在 `src/game/config.py` 文件中修改：

- **水果生成频率**：调整 `SPAWN_RATE` 参数
- **水果速度**：调整 `FRUIT_VELOCITY` 参数
- **游戏难度**：调整 `DIFFICULTY_LEVEL` 参数
- **音效音量**：调整 `SOUND_VOLUME` 参数

## 开发指南

### 项目分工

- **手势识别模块**：负责集成MediaPipe Hands，实现手势检测和跟踪
- **游戏核心模块**：负责游戏逻辑，包括水果生成、物理模拟、碰撞检测等
- **界面模块**：负责游戏渲染和视觉效果
- **音频模块**：负责游戏音效和背景音乐

### 代码规范

- 遵循 PEP 8 代码规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查

### 测试

运行测试：

```bash
pytest
```

## 打包发布

使用 PyInstaller 打包游戏：

```bash
pyinstaller --onefile --windowed main.py
```

## 贡献

欢迎贡献代码和提出建议！请按照以下步骤：

1. Fork 项目仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请联系项目维护者。

---

**享受游戏！** 🎮
