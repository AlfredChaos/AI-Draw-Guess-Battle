"""AI服务配置模块

定义AI相关的配置参数，包括LLM模型配置、文生图模型配置、API设置等。
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """大语言模型配置"""
    # 模型基本信息
    provider: str = "openai"  # openai, anthropic, local, etc.
    model_name: str = "gpt-3.5-turbo"
    api_key: str = ""
    api_base_url: str = "https://api.openai.com/v1"
    
    # 生成参数
    max_tokens: int = 150
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # 请求配置
    timeout: int = 30  # 秒
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    
    # 功能开关
    enable_streaming: bool = False
    enable_function_calling: bool = False
    
    # 提示词模板
    system_prompt: str = "你是一个友好的AI助手，专门帮助玩家进行绘画猜词游戏。"
    drawing_prompt_template: str = "请为词汇'{word}'生成一个简单的绘画描述，适合{difficulty}难度。"
    guessing_prompt_template: str = "根据这个绘画描述，猜测可能的词汇：{description}"
    hint_prompt_template: str = "为词汇'{word}'提供一个{difficulty}难度的提示。"
    
    def validate(self) -> None:
        """验证LLM配置"""
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        
        if not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")


@dataclass
class TextToImageConfig:
    """文生图模型配置"""
    # 模型基本信息
    provider: str = "openai"  # openai, stability, midjourney, local, etc.
    model_name: str = "dall-e-3"
    api_key: str = ""
    api_base_url: str = "https://api.openai.com/v1"
    
    # 图像生成参数
    image_size: str = "1024x1024"  # 支持的尺寸
    image_quality: str = "standard"  # standard, hd
    image_style: str = "natural"  # natural, vivid
    
    # 生成配置
    num_images: int = 1
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    
    # 请求配置
    timeout: int = 60  # 秒，图像生成通常需要更长时间
    max_retries: int = 2
    retry_delay: float = 2.0  # 秒
    
    # 图像处理
    auto_resize: bool = True
    target_width: int = 512
    target_height: int = 512
    save_original: bool = True
    
    # 提示词增强
    enable_prompt_enhancement: bool = True
    style_suffix: str = ", simple drawing style, clean lines, minimal details"
    negative_prompt: str = "text, watermark, signature, complex details"
    
    # 支持的图像尺寸
    supported_sizes: List[str] = None
    
    def __post_init__(self):
        if self.supported_sizes is None:
            self.supported_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
    
    def validate(self) -> None:
        """验证文生图配置"""
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        
        if self.image_size not in self.supported_sizes:
            raise ValueError(f"image_size must be one of {self.supported_sizes}")
        
        if self.num_images <= 0:
            raise ValueError("num_images must be positive")
        
        if self.guidance_scale <= 0:
            raise ValueError("guidance_scale must be positive")
        
        if self.num_inference_steps <= 0:
            raise ValueError("num_inference_steps must be positive")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if self.target_width <= 0 or self.target_height <= 0:
            raise ValueError("Target dimensions must be positive")


@dataclass
class CacheConfig:
    """缓存配置"""
    # 缓存开关
    enable_llm_cache: bool = True
    enable_image_cache: bool = True
    
    # 缓存大小限制
    max_llm_cache_size: int = 100  # 最大缓存条目数
    max_image_cache_size: int = 50
    
    # 缓存过期时间 (秒)
    llm_cache_ttl: int = 3600  # 1小时
    image_cache_ttl: int = 7200  # 2小时
    
    # 缓存目录
    cache_directory: str = "cache"
    llm_cache_file: str = "llm_cache.json"
    image_cache_directory: str = "images"
    
    # 缓存策略
    cache_strategy: str = "lru"  # lru, fifo, lfu
    
    def validate(self) -> None:
        """验证缓存配置"""
        if self.max_llm_cache_size <= 0:
            raise ValueError("max_llm_cache_size must be positive")
        
        if self.max_image_cache_size <= 0:
            raise ValueError("max_image_cache_size must be positive")
        
        if self.llm_cache_ttl <= 0 or self.image_cache_ttl <= 0:
            raise ValueError("Cache TTL must be positive")
        
        if self.cache_strategy not in ['lru', 'fifo', 'lfu']:
            raise ValueError("cache_strategy must be one of: lru, fifo, lfu")


@dataclass
class AIBehaviorConfig:
    """AI行为配置"""
    # AI难度设置
    ai_difficulty_levels: Dict[str, float] = None
    default_ai_difficulty: str = "medium"
    
    # AI绘画行为
    ai_drawing_speed: float = 1.0  # 绘画速度倍数
    ai_drawing_accuracy: float = 0.8  # 绘画准确度 (0-1)
    ai_use_hints: bool = True
    
    # AI猜测行为
    ai_guessing_delay: float = 2.0  # 猜测延迟 (秒)
    ai_confidence_threshold: float = 0.7  # 置信度阈值
    ai_max_guesses: int = 3
    
    # AI个性化
    ai_personality: str = "friendly"  # friendly, competitive, helpful
    ai_response_style: str = "casual"  # casual, formal, playful
    
    # 学习和适应
    enable_adaptive_difficulty: bool = True
    learning_rate: float = 0.1
    
    def __post_init__(self):
        if self.ai_difficulty_levels is None:
            self.ai_difficulty_levels = {
                "easy": 0.6,
                "medium": 0.8,
                "hard": 1.0,
                "expert": 1.2
            }
    
    def validate(self) -> None:
        """验证AI行为配置"""
        if self.default_ai_difficulty not in self.ai_difficulty_levels:
            raise ValueError(f"default_ai_difficulty must be one of {list(self.ai_difficulty_levels.keys())}")
        
        if not 0 <= self.ai_drawing_accuracy <= 1:
            raise ValueError("ai_drawing_accuracy must be between 0 and 1")
        
        if self.ai_guessing_delay < 0:
            raise ValueError("ai_guessing_delay cannot be negative")
        
        if not 0 <= self.ai_confidence_threshold <= 1:
            raise ValueError("ai_confidence_threshold must be between 0 and 1")
        
        if self.ai_max_guesses <= 0:
            raise ValueError("ai_max_guesses must be positive")


@dataclass
class AIConfig:
    """AI总配置类"""
    llm: LLMConfig
    text_to_image: TextToImageConfig
    cache: CacheConfig
    behavior: AIBehaviorConfig
    
    # 全局AI设置
    enable_ai: bool = True
    enable_offline_mode: bool = False
    fallback_to_local: bool = True
    
    # 安全和限制
    content_filter_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    max_concurrent_requests: int = 5
    
    # 监控和日志
    log_api_calls: bool = True
    log_response_times: bool = True
    enable_usage_tracking: bool = True
    
    def __init__(self):
        self.llm = LLMConfig()
        self.text_to_image = TextToImageConfig()
        self.cache = CacheConfig()
        self.behavior = AIBehaviorConfig()
    
    def validate(self) -> None:
        """验证AI配置的有效性"""
        self.llm.validate()
        self.text_to_image.validate()
        self.cache.validate()
        self.behavior.validate()
        
        if self.rate_limit_requests_per_minute <= 0:
            raise ValueError("rate_limit_requests_per_minute must be positive")
        
        if self.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be positive")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'AIConfig':
        """从JSON文件加载AI配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            AIConfig: AI配置实例
        """
        try:
            with config_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls()
            
            # 加载各个子配置
            if 'llm' in data:
                config.llm = LLMConfig(**data['llm'])
            if 'text_to_image' in data:
                config.text_to_image = TextToImageConfig(**data['text_to_image'])
            if 'cache' in data:
                config.cache = CacheConfig(**data['cache'])
            if 'behavior' in data:
                config.behavior = AIBehaviorConfig(**data['behavior'])
            
            # 加载主配置属性
            main_attrs = ['enable_ai', 'enable_offline_mode', 'fallback_to_local',
                         'content_filter_enabled', 'rate_limit_requests_per_minute',
                         'max_concurrent_requests', 'log_api_calls', 'log_response_times',
                         'enable_usage_tracking']
            
            for attr in main_attrs:
                if attr in data:
                    setattr(config, attr, data[attr])
            
            config.validate()
            logger.info(f"Loaded AI config from {config_path}")
            return config
            
        except FileNotFoundError:
            logger.warning(f"AI config file not found: {config_path}, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Error loading AI config from {config_path}: {e}")
            raise
    
    def save_to_file(self, config_path: Path) -> None:
        """保存AI配置到JSON文件"""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'llm': self.llm.__dict__,
                'text_to_image': self.text_to_image.__dict__,
                'cache': self.cache.__dict__,
                'behavior': self.behavior.__dict__,
                'enable_ai': self.enable_ai,
                'enable_offline_mode': self.enable_offline_mode,
                'fallback_to_local': self.fallback_to_local,
                'content_filter_enabled': self.content_filter_enabled,
                'rate_limit_requests_per_minute': self.rate_limit_requests_per_minute,
                'max_concurrent_requests': self.max_concurrent_requests,
                'log_api_calls': self.log_api_calls,
                'log_response_times': self.log_response_times,
                'enable_usage_tracking': self.enable_usage_tracking
            }
            
            with config_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved AI config to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving AI config to {config_path}: {e}")
            raise
    
    def get_provider_config(self, service_type: str) -> Dict[str, Any]:
        """获取特定服务的提供商配置
        
        Args:
            service_type: 服务类型 ('llm' 或 'text_to_image')
            
        Returns:
            提供商配置字典
        """
        if service_type == 'llm':
            return {
                'provider': self.llm.provider,
                'model_name': self.llm.model_name,
                'api_key': self.llm.api_key,
                'api_base_url': self.llm.api_base_url,
                'timeout': self.llm.timeout,
                'max_retries': self.llm.max_retries
            }
        elif service_type == 'text_to_image':
            return {
                'provider': self.text_to_image.provider,
                'model_name': self.text_to_image.model_name,
                'api_key': self.text_to_image.api_key,
                'api_base_url': self.text_to_image.api_base_url,
                'timeout': self.text_to_image.timeout,
                'max_retries': self.text_to_image.max_retries
            }
        else:
            raise ValueError(f"Unknown service type: {service_type}")


# 全局AI配置实例
_ai_config: Optional[AIConfig] = None


def get_ai_config() -> AIConfig:
    """获取全局AI配置实例
    
    Returns:
        AIConfig: AI配置实例
    """
    global _ai_config
    if _ai_config is None:
        _ai_config = AIConfig()
    return _ai_config


def load_ai_config(config_path: Optional[Path] = None) -> AIConfig:
    """加载AI配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        AIConfig: AI配置实例
    """
    global _ai_config
    
    if config_path is None:
        config_path = Path(__file__).parent / 'ai_settings.json'
    
    _ai_config = AIConfig.load_from_file(config_path)
    return _ai_config


def save_ai_config(config_path: Optional[Path] = None) -> None:
    """保存当前AI配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    config = get_ai_config()
    
    if config_path is None:
        config_path = Path(__file__).parent / 'ai_settings.json'
    
    config.save_to_file(config_path)