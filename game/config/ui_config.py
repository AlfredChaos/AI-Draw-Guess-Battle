"""UI界面配置模块

定义用户界面相关的配置参数，包括窗口设置、颜色主题、字体配置、布局参数等。
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class WindowConfig:
    """窗口配置"""
    width: int = 1200
    height: int = 800
    title: str = "AI Sketch Duel"
    resizable: bool = True
    fullscreen: bool = False
    vsync: bool = True
    fps_limit: int = 60
    
    def get_size(self) -> Tuple[int, int]:
        """获取窗口尺寸"""
        return (self.width, self.height)


@dataclass
class ColorTheme:
    """颜色主题配置"""
    # 主色调
    primary: Tuple[int, int, int] = (74, 144, 226)  # 蓝色
    secondary: Tuple[int, int, int] = (156, 39, 176)  # 紫色
    accent: Tuple[int, int, int] = (255, 193, 7)  # 黄色
    
    # 背景色
    background: Tuple[int, int, int] = (18, 18, 18)  # 深灰
    surface: Tuple[int, int, int] = (33, 33, 33)  # 中灰
    
    # 文本色
    text_primary: Tuple[int, int, int] = (255, 255, 255)  # 白色
    text_secondary: Tuple[int, int, int] = (189, 189, 189)  # 浅灰
    text_disabled: Tuple[int, int, int] = (117, 117, 117)  # 深灰
    
    # 状态色
    success: Tuple[int, int, int] = (76, 175, 80)  # 绿色
    warning: Tuple[int, int, int] = (255, 152, 0)  # 橙色
    error: Tuple[int, int, int] = (244, 67, 54)  # 红色
    info: Tuple[int, int, int] = (33, 150, 243)  # 蓝色
    
    # 玻璃拟态效果
    glass_background: Tuple[int, int, int, int] = (255, 255, 255, 20)  # 半透明白色
    glass_border: Tuple[int, int, int, int] = (255, 255, 255, 40)  # 边框色
    
    def get_rgba(self, color_name: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """获取带透明度的颜色
        
        Args:
            color_name: 颜色名称
            alpha: 透明度 (0-255)
            
        Returns:
            RGBA颜色元组
        """
        color = getattr(self, color_name, self.primary)
        if len(color) == 3:
            return (*color, alpha)
        return color


@dataclass
class FontConfig:
    """字体配置"""
    # 字体族
    primary_font: str = "Arial"
    secondary_font: str = "Helvetica"
    monospace_font: str = "Courier New"
    
    # 字体大小
    title_size: int = 32
    heading_size: int = 24
    body_size: int = 16
    caption_size: int = 12
    small_size: int = 10
    
    # 字体样式
    title_bold: bool = True
    heading_bold: bool = True
    body_bold: bool = False
    
    def get_font_info(self, font_type: str) -> Dict[str, Any]:
        """获取字体信息
        
        Args:
            font_type: 字体类型 ('title', 'heading', 'body', 'caption', 'small')
            
        Returns:
            字体信息字典
        """
        size_map = {
            'title': self.title_size,
            'heading': self.heading_size,
            'body': self.body_size,
            'caption': self.caption_size,
            'small': self.small_size
        }
        
        bold_map = {
            'title': self.title_bold,
            'heading': self.heading_bold,
            'body': self.body_bold,
            'caption': False,
            'small': False
        }
        
        return {
            'family': self.primary_font,
            'size': size_map.get(font_type, self.body_size),
            'bold': bold_map.get(font_type, False)
        }


@dataclass
class LayoutConfig:
    """布局配置"""
    # 边距和间距
    margin_small: int = 8
    margin_medium: int = 16
    margin_large: int = 24
    margin_xlarge: int = 32
    
    # 组件尺寸
    button_height: int = 40
    input_height: int = 36
    panel_min_width: int = 200
    panel_min_height: int = 150
    
    # 白板配置
    whiteboard_width: int = 600
    whiteboard_height: int = 400
    whiteboard_border_width: int = 2
    
    # 聊天面板配置
    chat_panel_width: int = 300
    chat_panel_height: int = 400
    chat_message_height: int = 30
    chat_max_messages: int = 50
    
    # Live2D模型配置
    live2d_model_width: int = 200
    live2d_model_height: int = 300
    live2d_position_x: int = 50
    live2d_position_y: int = 50
    
    # 圆角半径
    border_radius_small: int = 4
    border_radius_medium: int = 8
    border_radius_large: int = 12
    
    def get_whiteboard_rect(self, window_width: int, window_height: int) -> Tuple[int, int, int, int]:
        """获取白板矩形区域
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            
        Returns:
            (x, y, width, height) 矩形坐标
        """
        x = (window_width - self.whiteboard_width) // 2
        y = (window_height - self.whiteboard_height) // 2
        return (x, y, self.whiteboard_width, self.whiteboard_height)
    
    def get_chat_panel_rect(self, window_width: int, window_height: int) -> Tuple[int, int, int, int]:
        """获取聊天面板矩形区域"""
        x = window_width - self.chat_panel_width - self.margin_medium
        y = self.margin_medium
        return (x, y, self.chat_panel_width, self.chat_panel_height)


@dataclass
class AnimationConfig:
    """动画配置"""
    # 动画持续时间 (毫秒)
    fade_duration: int = 300
    slide_duration: int = 250
    scale_duration: int = 200
    
    # 缓动函数类型
    easing_type: str = "ease_out"
    
    # 动画开关
    enable_animations: bool = True
    enable_transitions: bool = True
    enable_particle_effects: bool = True
    
    # 粒子效果配置
    particle_count: int = 50
    particle_lifetime: float = 2.0
    particle_speed: float = 100.0


@dataclass
class UIConfig:
    """UI总配置类"""
    window: WindowConfig
    colors: ColorTheme
    fonts: FontConfig
    layout: LayoutConfig
    animation: AnimationConfig
    
    # UI行为配置
    show_fps: bool = False
    show_debug_info: bool = False
    enable_tooltips: bool = True
    tooltip_delay: int = 500  # 毫秒
    
    # 输入配置
    double_click_time: int = 300  # 毫秒
    long_press_time: int = 500  # 毫秒
    
    def __init__(self):
        self.window = WindowConfig()
        self.colors = ColorTheme()
        self.fonts = FontConfig()
        self.layout = LayoutConfig()
        self.animation = AnimationConfig()
    
    def validate(self) -> None:
        """验证UI配置的有效性"""
        if self.window.width <= 0 or self.window.height <= 0:
            raise ValueError("Window dimensions must be positive")
        
        if self.window.fps_limit <= 0:
            raise ValueError("FPS limit must be positive")
        
        if self.tooltip_delay < 0:
            raise ValueError("Tooltip delay cannot be negative")
        
        if self.double_click_time <= 0 or self.long_press_time <= 0:
            raise ValueError("Input timing must be positive")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'UIConfig':
        """从JSON文件加载UI配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            UIConfig: UI配置实例
        """
        try:
            with config_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls()
            
            # 加载各个子配置
            if 'window' in data:
                config.window = WindowConfig(**data['window'])
            if 'colors' in data:
                config.colors = ColorTheme(**data['colors'])
            if 'fonts' in data:
                config.fonts = FontConfig(**data['fonts'])
            if 'layout' in data:
                config.layout = LayoutConfig(**data['layout'])
            if 'animation' in data:
                config.animation = AnimationConfig(**data['animation'])
            
            # 加载主配置属性
            for key in ['show_fps', 'show_debug_info', 'enable_tooltips', 
                       'tooltip_delay', 'double_click_time', 'long_press_time']:
                if key in data:
                    setattr(config, key, data[key])
            
            config.validate()
            logger.info(f"Loaded UI config from {config_path}")
            return config
            
        except FileNotFoundError:
            logger.warning(f"UI config file not found: {config_path}, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Error loading UI config from {config_path}: {e}")
            raise
    
    def save_to_file(self, config_path: Path) -> None:
        """保存UI配置到JSON文件"""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'window': self.window.__dict__,
                'colors': self.colors.__dict__,
                'fonts': self.fonts.__dict__,
                'layout': self.layout.__dict__,
                'animation': self.animation.__dict__,
                'show_fps': self.show_fps,
                'show_debug_info': self.show_debug_info,
                'enable_tooltips': self.enable_tooltips,
                'tooltip_delay': self.tooltip_delay,
                'double_click_time': self.double_click_time,
                'long_press_time': self.long_press_time
            }
            
            with config_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved UI config to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving UI config to {config_path}: {e}")
            raise


# 全局UI配置实例
_ui_config: Optional[UIConfig] = None


def get_ui_config() -> UIConfig:
    """获取全局UI配置实例
    
    Returns:
        UIConfig: UI配置实例
    """
    global _ui_config
    if _ui_config is None:
        _ui_config = UIConfig()
    return _ui_config


def load_ui_config(config_path: Optional[Path] = None) -> UIConfig:
    """加载UI配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        UIConfig: UI配置实例
    """
    global _ui_config
    
    if config_path is None:
        config_path = Path(__file__).parent / 'ui_settings.json'
    
    _ui_config = UIConfig.load_from_file(config_path)
    return _ui_config


def save_ui_config(config_path: Optional[Path] = None) -> None:
    """保存当前UI配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    config = get_ui_config()
    
    if config_path is None:
        config_path = Path(__file__).parent / 'ui_settings.json'
    
    config.save_to_file(config_path)