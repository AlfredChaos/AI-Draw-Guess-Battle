"""配置模块

提供游戏的所有配置管理功能，包括游戏配置、UI配置、AI配置和统一的配置管理器。
"""

from .game_config import (
    GameConfig,
    get_game_config,
    load_game_config,
    save_game_config
)

from .ui_config import (
    UIConfig,
    WindowConfig,
    ColorTheme,
    FontConfig,
    LayoutConfig,
    AnimationConfig,
    get_ui_config,
    load_ui_config,
    save_ui_config
)

from .ai_config import (
    AIConfig,
    LLMConfig,
    TextToImageConfig,
    CacheConfig,
    AIBehaviorConfig,
    get_ai_config,
    load_ai_config,
    save_ai_config
)

from .config_manager import (
    ConfigManager,
    ConfigValidationError,
    ConfigLoadError,
    get_config_manager,
    initialize_configs
)

__all__ = [
    # 游戏配置
    'GameConfig',
    'get_game_config',
    'load_game_config',
    'save_game_config',
    
    # UI配置
    'UIConfig',
    'WindowConfig',
    'ColorTheme',
    'FontConfig',
    'LayoutConfig',
    'AnimationConfig',
    'get_ui_config',
    'load_ui_config',
    'save_ui_config',
    
    # AI配置
    'AIConfig',
    'LLMConfig',
    'TextToImageConfig',
    'CacheConfig',
    'AIBehaviorConfig',
    'get_ai_config',
    'load_ai_config',
    'save_ai_config',
    
    # 配置管理器
    'ConfigManager',
    'ConfigValidationError',
    'ConfigLoadError',
    'get_config_manager',
    'initialize_configs'
]