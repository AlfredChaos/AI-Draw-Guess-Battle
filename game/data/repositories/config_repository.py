"""
配置管理仓库模块

负责加载、管理和访问游戏配置数据。
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from ...utils.helpers import load_json_file


class ConfigRepository:
    """配置管理仓库"""
    
    def __init__(self, config_dir_path: Optional[str] = None):
        """
        初始化配置仓库
        
        Args:
            config_dir_path: 配置文件目录路径，默认为game/config
        """
        if config_dir_path is None:
            # 默认使用game/config目录
            self.config_dir_path = Path(__file__).parent.parent.parent / "config"
        else:
            self.config_dir_path = Path(config_dir_path)
        
        # 配置数据
        self.game_config: Dict[str, Any] = {}
        self.ui_config: Dict[str, Any] = {}
        self.ai_config: Dict[str, Any] = {}
        
        # 加载配置
        self._load_configs()
    
    def _load_configs(self) -> None:
        """加载所有配置文件"""
        # 加载游戏配置
        game_config_path = self.config_dir_path / "game_config.py"
        if game_config_path.exists():
            self.game_config = self._load_python_config(str(game_config_path))
        
        # 加载UI配置
        ui_config_path = self.config_dir_path / "ui_config.py"
        if ui_config_path.exists():
            self.ui_config = self._load_python_config(str(ui_config_path))
        
        # 加载AI配置
        ai_config_path = self.config_dir_path / "ai_config.py"
        if ai_config_path.exists():
            self.ai_config = self._load_python_config(str(ai_config_path))
    
    def _load_python_config(self, config_file_path: str) -> Dict[str, Any]:
        """
        加载Python配置文件
        
        Args:
            config_file_path: 配置文件路径
            
        Returns:
            配置数据字典
        """
        try:
            # 动态导入配置模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("config_module", config_file_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # 提取配置数据
            config_data = {}
            for attr_name in dir(config_module):
                # 跳过私有属性和内置属性
                if not attr_name.startswith('_'):
                    attr_value = getattr(config_module, attr_name)
                    # 只保存非函数、非模块类型的属性
                    if not callable(attr_value) and not str(type(attr_value)).startswith("<class 'module"):
                        config_data[attr_name] = attr_value
            
            return config_data
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_file_path}: {e}")
            return {}
    
    def _load_json_config(self, config_file_path: str) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        Args:
            config_file_path: 配置文件路径
            
        Returns:
            配置数据字典
        """
        data = load_json_file(config_file_path)
        return data if data is not None else {}
    
    def get_game_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取游戏配置
        
        Args:
            key: 配置键名，如果为None则返回所有游戏配置
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if key is None:
            return self.game_config.copy()
        
        return self.game_config.get(key, default)
    
    def get_ui_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取UI配置
        
        Args:
            key: 配置键名，如果为None则返回所有UI配置
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if key is None:
            return self.ui_config.copy()
        
        return self.ui_config.get(key, default)
    
    def get_ai_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取AI配置
        
        Args:
            key: 配置键名，如果为None则返回所有AI配置
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if key is None:
            return self.ai_config.copy()
        
        return self.ai_config.get(key, default)
    
    def get_config(self, config_type: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取指定类型的配置
        
        Args:
            config_type: 配置类型 ('game', 'ui', 'ai')
            key: 配置键名，如果为None则返回该类型的所有配置
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        config_type = config_type.lower()
        
        if config_type == 'game':
            return self.get_game_config(key, default)
        elif config_type == 'ui':
            return self.get_ui_config(key, default)
        elif config_type == 'ai':
            return self.get_ai_config(key, default)
        else:
            raise ValueError(f"不支持的配置类型: {config_type}")
    
    def reload_configs(self) -> None:
        """重新加载所有配置文件"""
        self.game_config.clear()
        self.ui_config.clear()
        self.ai_config.clear()
        self._load_configs()
    
    def update_game_config(self, key: str, value: Any) -> None:
        """
        更新游戏配置
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.game_config[key] = value
    
    def update_ui_config(self, key: str, value: Any) -> None:
        """
        更新UI配置
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.ui_config[key] = value
    
    def update_ai_config(self, key: str, value: Any) -> None:
        """
        更新AI配置
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.ai_config[key] = value