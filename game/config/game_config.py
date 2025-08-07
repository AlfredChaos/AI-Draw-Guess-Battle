"""游戏基础配置模块

定义游戏的核心配置参数，包括游戏规则、时间限制、积分系统等。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameConfig:
    """游戏基础配置数据类"""
    
    # 游戏基本设置
    max_rounds: int = 3
    max_players: int = 2
    drawing_time_limit: int = 60  # 绘画时间限制(秒)
    guessing_time_limit: int = 30  # 猜测时间限制(秒)
    
    # 积分系统
    base_score_per_correct: int = 10
    time_bonus_multiplier: float = 2.0
    max_time_bonus: int = 60
    
    # 游戏难度设置
    default_difficulty: str = 'medium'
    available_difficulties: tuple = ('easy', 'medium', 'hard')
    
    # 词汇设置
    min_word_length: int = 2
    max_word_length: int = 10
    words_per_difficulty: int = 100
    
    # 系统设置
    debug_mode: bool = False
    auto_save_interval: int = 30  # 自动保存间隔(秒)
    log_level: str = 'INFO'
    
    # 文件路径
    words_file_path: str = 'words.json'
    save_directory: str = 'saves'
    log_directory: str = 'logs'
    
    def __post_init__(self) -> None:
        """初始化后验证配置"""
        self.validate()
    
    def validate(self) -> None:
        """验证配置参数的有效性"""
        if self.max_rounds <= 0:
            raise ValueError("max_rounds must be positive")
        
        if self.max_players < 1:
            raise ValueError("max_players must be at least 1")
        
        if self.drawing_time_limit <= 0 or self.guessing_time_limit <= 0:
            raise ValueError("Time limits must be positive")
        
        if self.default_difficulty not in self.available_difficulties:
            raise ValueError(f"default_difficulty must be one of {self.available_difficulties}")
        
        if self.min_word_length >= self.max_word_length:
            raise ValueError("min_word_length must be less than max_word_length")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError("Invalid log_level")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'GameConfig':
        """从JSON文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            GameConfig: 配置实例
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON格式错误
            ValueError: 配置参数无效
        """
        try:
            with config_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded game config from {config_path}")
            return cls(**data)
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            raise
    
    def save_to_file(self, config_path: Path) -> None:
        """保存配置到JSON文件
        
        Args:
            config_path: 配置文件路径
        """
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with config_path.open('w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved game config to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config to {config_path}: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'max_rounds': self.max_rounds,
            'max_players': self.max_players,
            'drawing_time_limit': self.drawing_time_limit,
            'guessing_time_limit': self.guessing_time_limit,
            'base_score_per_correct': self.base_score_per_correct,
            'time_bonus_multiplier': self.time_bonus_multiplier,
            'max_time_bonus': self.max_time_bonus,
            'default_difficulty': self.default_difficulty,
            'available_difficulties': list(self.available_difficulties),
            'min_word_length': self.min_word_length,
            'max_word_length': self.max_word_length,
            'words_per_difficulty': self.words_per_difficulty,
            'debug_mode': self.debug_mode,
            'auto_save_interval': self.auto_save_interval,
            'log_level': self.log_level,
            'words_file_path': self.words_file_path,
            'save_directory': self.save_directory,
            'log_directory': self.log_directory
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """从字典更新配置
        
        Args:
            data: 包含配置参数的字典
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 重新验证配置
        self.validate()
        logger.info("Game config updated from dictionary")
    
    def get_difficulty_settings(self, difficulty: str) -> Dict[str, Any]:
        """获取特定难度的设置
        
        Args:
            difficulty: 难度级别
            
        Returns:
            Dict: 难度相关的设置
        """
        if difficulty not in self.available_difficulties:
            difficulty = self.default_difficulty
        
        # 根据难度调整时间限制和积分
        difficulty_multipliers = {
            'easy': {'time': 1.5, 'score': 0.8},
            'medium': {'time': 1.0, 'score': 1.0},
            'hard': {'time': 0.7, 'score': 1.5}
        }
        
        multiplier = difficulty_multipliers.get(difficulty, difficulty_multipliers['medium'])
        
        return {
            'drawing_time_limit': int(self.drawing_time_limit * multiplier['time']),
            'guessing_time_limit': int(self.guessing_time_limit * multiplier['time']),
            'score_multiplier': multiplier['score']
        }


# 全局配置实例
_game_config: Optional[GameConfig] = None


def get_game_config() -> GameConfig:
    """获取全局游戏配置实例
    
    Returns:
        GameConfig: 游戏配置实例
    """
    global _game_config
    if _game_config is None:
        _game_config = GameConfig()
    return _game_config


def load_game_config(config_path: Optional[Path] = None) -> GameConfig:
    """加载游戏配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        GameConfig: 游戏配置实例
    """
    global _game_config
    
    if config_path is None:
        config_path = Path(__file__).parent / 'game_settings.json'
    
    _game_config = GameConfig.load_from_file(config_path)
    return _game_config


def save_game_config(config_path: Optional[Path] = None) -> None:
    """保存当前游戏配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    config = get_game_config()
    
    if config_path is None:
        config_path = Path(__file__).parent / 'game_settings.json'
    
    config.save_to_file(config_path)