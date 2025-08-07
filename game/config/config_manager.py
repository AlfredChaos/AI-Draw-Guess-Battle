"""配置管理器模块

提供统一的配置加载、验证和管理机制，整合游戏、UI和AI配置。
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import json
import logging
from dataclasses import asdict

from .game_config import GameConfig, get_game_config, load_game_config, save_game_config
from .ui_config import UIConfig, get_ui_config, load_ui_config, save_ui_config
from .ai_config import AIConfig, get_ai_config, load_ai_config, save_ai_config

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigLoadError(Exception):
    """配置加载错误"""
    pass


class ConfigManager:
    """配置管理器
    
    统一管理游戏的所有配置，提供加载、保存、验证和热重载功能。
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，如果为None则使用默认目录
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.game_config_path = self.config_dir / 'game_settings.json'
        self.ui_config_path = self.config_dir / 'ui_settings.json'
        self.ai_config_path = self.config_dir / 'ai_settings.json'
        self.master_config_path = self.config_dir / 'master_config.json'
        
        # 配置实例
        self._game_config: Optional[GameConfig] = None
        self._ui_config: Optional[UIConfig] = None
        self._ai_config: Optional[AIConfig] = None
        
        # 配置变更监听器
        self._change_listeners: Dict[str, list] = {
            'game': [],
            'ui': [],
            'ai': [],
            'all': []
        }
        
        logger.info(f"ConfigManager initialized with config directory: {self.config_dir}")
    
    @property
    def game_config(self) -> GameConfig:
        """获取游戏配置"""
        if self._game_config is None:
            self._game_config = get_game_config()
        return self._game_config
    
    @property
    def ui_config(self) -> UIConfig:
        """获取UI配置"""
        if self._ui_config is None:
            self._ui_config = get_ui_config()
        return self._ui_config
    
    @property
    def ai_config(self) -> AIConfig:
        """获取AI配置"""
        if self._ai_config is None:
            self._ai_config = get_ai_config()
        return self._ai_config
    
    def load_all_configs(self, use_defaults_on_error: bool = True) -> bool:
        """加载所有配置文件
        
        Args:
            use_defaults_on_error: 当加载失败时是否使用默认配置
            
        Returns:
            bool: 是否成功加载所有配置
        """
        success = True
        
        try:
            # 加载游戏配置
            self._game_config = load_game_config(self.game_config_path)
            logger.info("Game config loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load game config: {e}")
            if use_defaults_on_error:
                self._game_config = GameConfig()
                logger.info("Using default game config")
            else:
                success = False
        
        try:
            # 加载UI配置
            self._ui_config = load_ui_config(self.ui_config_path)
            logger.info("UI config loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load UI config: {e}")
            if use_defaults_on_error:
                self._ui_config = UIConfig()
                logger.info("Using default UI config")
            else:
                success = False
        
        try:
            # 加载AI配置
            self._ai_config = load_ai_config(self.ai_config_path)
            logger.info("AI config loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI config: {e}")
            if use_defaults_on_error:
                self._ai_config = AIConfig()
                logger.info("Using default AI config")
            else:
                success = False
        
        if success:
            self._notify_listeners('all')
            logger.info("All configurations loaded successfully")
        
        return success
    
    def save_all_configs(self) -> bool:
        """保存所有配置文件
        
        Returns:
            bool: 是否成功保存所有配置
        """
        success = True
        
        try:
            save_game_config(self.game_config_path)
            logger.info("Game config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save game config: {e}")
            success = False
        
        try:
            save_ui_config(self.ui_config_path)
            logger.info("UI config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save UI config: {e}")
            success = False
        
        try:
            save_ai_config(self.ai_config_path)
            logger.info("AI config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save AI config: {e}")
            success = False
        
        if success:
            logger.info("All configurations saved successfully")
        
        return success
    
    def validate_all_configs(self) -> Dict[str, list]:
        """验证所有配置
        
        Returns:
            Dict: 包含各配置验证错误的字典
        """
        errors = {
            'game': [],
            'ui': [],
            'ai': []
        }
        
        # 验证游戏配置
        try:
            self.game_config.validate()
        except Exception as e:
            errors['game'].append(str(e))
        
        # 验证UI配置
        try:
            self.ui_config.validate()
        except Exception as e:
            errors['ui'].append(str(e))
        
        # 验证AI配置
        try:
            self.ai_config.validate()
        except Exception as e:
            errors['ai'].append(str(e))
        
        # 跨配置验证
        cross_validation_errors = self._cross_validate_configs()
        for category, error_list in cross_validation_errors.items():
            errors[category].extend(error_list)
        
        return errors
    
    def _cross_validate_configs(self) -> Dict[str, list]:
        """跨配置验证
        
        检查不同配置之间的一致性和兼容性
        """
        errors = {
            'game': [],
            'ui': [],
            'ai': []
        }
        
        # 检查窗口尺寸与白板尺寸的兼容性
        if (self.ui_config.layout.whiteboard_width > self.ui_config.window.width or
            self.ui_config.layout.whiteboard_height > self.ui_config.window.height):
            errors['ui'].append("Whiteboard size exceeds window size")
        
        # 检查AI配置与游戏配置的兼容性
        if (self.ai_config.llm.timeout > self.game_config.drawing_time_limit and
            self.ai_config.enable_ai):
            errors['ai'].append("LLM timeout exceeds drawing time limit")
        
        # 检查缓存目录权限
        cache_dir = Path(self.ai_config.cache.cache_directory)
        if not cache_dir.exists():
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                errors['ai'].append(f"Cannot create cache directory: {cache_dir}")
        
        return errors
    
    def export_master_config(self) -> Dict[str, Any]:
        """导出主配置文件
        
        Returns:
            Dict: 包含所有配置的字典
        """
        master_config = {
            'version': '1.0.0',
            'game': self._config_to_dict(self.game_config),
            'ui': self._config_to_dict(self.ui_config),
            'ai': self._config_to_dict(self.ai_config),
            'metadata': {
                'created_by': 'ConfigManager',
                'config_dir': str(self.config_dir)
            }
        }
        
        return master_config
    
    def import_master_config(self, config_data: Dict[str, Any]) -> bool:
        """导入主配置文件
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            bool: 是否成功导入
        """
        try:
            # 验证配置版本
            version = config_data.get('version', '1.0.0')
            if version != '1.0.0':
                logger.warning(f"Config version mismatch: {version}, expected 1.0.0")
            
            # 导入各个配置
            if 'game' in config_data:
                self._game_config = GameConfig(**config_data['game'])
            
            if 'ui' in config_data:
                ui_data = config_data['ui']
                self._ui_config = UIConfig()
                # 这里需要更复杂的导入逻辑，因为UIConfig包含嵌套的dataclass
                # 简化处理，实际使用时需要完善
            
            if 'ai' in config_data:
                ai_data = config_data['ai']
                self._ai_config = AIConfig()
                # 同样需要更复杂的导入逻辑
            
            # 验证导入的配置
            validation_errors = self.validate_all_configs()
            if any(errors for errors in validation_errors.values()):
                logger.error(f"Validation errors after import: {validation_errors}")
                return False
            
            self._notify_listeners('all')
            logger.info("Master config imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import master config: {e}")
            return False
    
    def save_master_config(self) -> bool:
        """保存主配置文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            master_config = self.export_master_config()
            
            with self.master_config_path.open('w', encoding='utf-8') as f:
                json.dump(master_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Master config saved to {self.master_config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save master config: {e}")
            return False
    
    def load_master_config(self) -> bool:
        """加载主配置文件
        
        Returns:
            bool: 是否成功加载
        """
        try:
            if not self.master_config_path.exists():
                logger.info("Master config file not found, loading individual configs")
                return self.load_all_configs()
            
            with self.master_config_path.open('r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return self.import_master_config(config_data)
            
        except Exception as e:
            logger.error(f"Failed to load master config: {e}")
            return self.load_all_configs(use_defaults_on_error=True)
    
    def add_change_listener(self, config_type: str, callback) -> None:
        """添加配置变更监听器
        
        Args:
            config_type: 配置类型 ('game', 'ui', 'ai', 'all')
            callback: 回调函数
        """
        if config_type in self._change_listeners:
            self._change_listeners[config_type].append(callback)
        else:
            raise ValueError(f"Invalid config type: {config_type}")
    
    def remove_change_listener(self, config_type: str, callback) -> None:
        """移除配置变更监听器"""
        if config_type in self._change_listeners:
            try:
                self._change_listeners[config_type].remove(callback)
            except ValueError:
                pass
    
    def _notify_listeners(self, config_type: str) -> None:
        """通知配置变更监听器"""
        for callback in self._change_listeners.get(config_type, []):
            try:
                callback(config_type, self)
            except Exception as e:
                logger.error(f"Error in config change listener: {e}")
    
    def _config_to_dict(self, config) -> Dict[str, Any]:
        """将配置对象转换为字典"""
        if hasattr(config, '__dict__'):
            result = {}
            for key, value in config.__dict__.items():
                if hasattr(value, '__dict__'):
                    result[key] = self._config_to_dict(value)
                else:
                    result[key] = value
            return result
        else:
            return asdict(config) if hasattr(config, '__dataclass_fields__') else config
    
    def reset_to_defaults(self, config_type: Optional[str] = None) -> None:
        """重置配置为默认值
        
        Args:
            config_type: 要重置的配置类型，如果为None则重置所有配置
        """
        if config_type is None or config_type == 'game':
            self._game_config = GameConfig()
            self._notify_listeners('game')
            logger.info("Game config reset to defaults")
        
        if config_type is None or config_type == 'ui':
            self._ui_config = UIConfig()
            self._notify_listeners('ui')
            logger.info("UI config reset to defaults")
        
        if config_type is None or config_type == 'ai':
            self._ai_config = AIConfig()
            self._notify_listeners('ai')
            logger.info("AI config reset to defaults")
        
        if config_type is None:
            self._notify_listeners('all')
            logger.info("All configs reset to defaults")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要信息
        
        Returns:
            Dict: 配置摘要
        """
        return {
            'game': {
                'max_rounds': self.game_config.max_rounds,
                'max_players': self.game_config.max_players,
                'debug_mode': self.game_config.debug_mode
            },
            'ui': {
                'window_size': self.ui_config.window.get_size(),
                'fullscreen': self.ui_config.window.fullscreen,
                'theme': 'dark'  # 简化处理
            },
            'ai': {
                'enabled': self.ai_config.enable_ai,
                'llm_provider': self.ai_config.llm.provider,
                'image_provider': self.ai_config.text_to_image.provider
            }
        }


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例
    
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def initialize_configs(config_dir: Optional[Path] = None) -> bool:
    """初始化配置系统
    
    Args:
        config_dir: 配置文件目录
        
    Returns:
        bool: 是否成功初始化
    """
    global _config_manager
    _config_manager = ConfigManager(config_dir)
    return _config_manager.load_all_configs()