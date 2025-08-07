"""
事件总线模块

实现游戏中的事件发布/订阅机制，用于模块间解耦通信。
"""

from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class EventType(Enum):
    """游戏事件类型枚举"""
    
    # 游戏状态事件
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_PAUSE = "game_pause"
    GAME_RESUME = "game_resume"
    GAME_STATE_CHANGED = "game_state_changed"
    GAME_RESET = "game_reset"
    
    # 回合事件
    ROUND_START = "round_start"
    ROUND_END = "round_end"
    
    # 绘画事件
    DRAWING_START = "drawing_start"
    DRAWING_UPDATE = "drawing_update"
    DRAWING_END = "drawing_end"
    
    # 猜测事件
    GUESS_SUBMITTED = "guess_submitted"
    GUESS_CORRECT = "guess_correct"
    GUESS_INCORRECT = "guess_incorrect"
    
    # 玩家事件
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_READY = "player_ready"
    
    # 分数事件
    SCORE_UPDATE = "score_update"
    
    # AI事件
    AI_THINKING_START = "ai_thinking_start"
    AI_THINKING_END = "ai_thinking_end"
    AI_RESPONSE = "ai_response"
    
    # UI事件
    UI_BUTTON_CLICKED = "ui_button_clicked"
    UI_MODE_CHANGED = "ui_mode_changed"
    
    # 系统事件
    SYSTEM_ERROR = "system_error"
    CONFIG_CHANGED = "config_changed"


@dataclass
class GameEvent:
    """游戏事件数据结构"""
    
    # 事件类型
    event_type: EventType
    
    # 事件数据
    data: Dict[str, Any] = field(default_factory=dict)
    
    # 事件时间戳
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 事件ID
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 事件发送者（可选）
    sender: Optional[str] = None
    
    # 事件优先级（数值越大优先级越高）
    priority: int = 0
    
    def __post_init__(self):
        """数据初始化后验证"""
        if not isinstance(self.event_type, EventType):
            raise ValueError("event_type必须是EventType枚举类型")


class EventBus:
    """事件总线系统"""
    
    def __init__(self):
        """初始化事件总线"""
        # 存储事件监听器 {事件类型: [监听器列表]}
        self._listeners: Dict[EventType, List[Callable[[GameEvent], None]]] = {}
        
        # 存储一次性监听器 {事件类型: [监听器列表]}
        self._one_time_listeners: Dict[EventType, List[Callable[[GameEvent], None]]] = {}
    
    def subscribe(self, event_type: EventType, listener: Callable[[GameEvent], None]) -> str:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            listener: 事件监听器回调函数
            
        Returns:
            订阅ID，可用于取消订阅
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(listener)
        return f"subscription_{event_type.value}_{len(self._listeners[event_type])}"
    
    def subscribe_once(self, event_type: EventType, listener: Callable[[GameEvent], None]) -> str:
        """
        订阅事件（仅一次）
        
        Args:
            event_type: 事件类型
            listener: 事件监听器回调函数
            
        Returns:
            订阅ID，可用于取消订阅
        """
        if event_type not in self._one_time_listeners:
            self._one_time_listeners[event_type] = []
        
        self._one_time_listeners[event_type].append(listener)
        return f"one_time_subscription_{event_type.value}_{len(self._one_time_listeners[event_type])}"
    
    def unsubscribe(self, event_type: EventType, listener: Callable[[GameEvent], None]) -> bool:
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            listener: 事件监听器回调函数
            
        Returns:
            是否成功取消订阅
        """
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
            return True
        
        # 检查一次性监听器
        if event_type in self._one_time_listeners and listener in self._one_time_listeners[event_type]:
            self._one_time_listeners[event_type].remove(listener)
            return True
        
        return False
    
    def publish(self, event: GameEvent) -> None:
        """
        发布事件
        
        Args:
            event: 游戏事件对象
        """
        # 通知常规监听器
        if event.event_type in self._listeners:
            # 按优先级排序监听器
            listeners = sorted(self._listeners[event.event_type], 
                             key=lambda listener: getattr(listener, '_priority', 0), 
                             reverse=True)
            
            for listener in listeners:
                try:
                    listener(event)
                except Exception as e:
                    print(f"警告: 事件监听器执行出错: {e}")
        
        # 通知一次性监听器
        if event.event_type in self._one_time_listeners:
            # 复制列表以避免在迭代时修改列表
            one_time_listeners = self._one_time_listeners[event.event_type].copy()
            
            for listener in one_time_listeners:
                try:
                    listener(event)
                except Exception as e:
                    print(f"警告: 一次性事件监听器执行出错: {e}")
            
            # 清除已触发的一次性监听器
            self._one_time_listeners[event.event_type].clear()
    
    def publish_sync(self, event: GameEvent) -> None:
        """
        同步发布事件（别名方法）
        
        Args:
            event: 游戏事件对象
        """
        self.publish(event)
    
    def has_listeners(self, event_type: EventType) -> bool:
        """
        检查是否有监听器订阅了指定事件类型
        
        Args:
            event_type: 事件类型
            
        Returns:
            是否有监听器
        """
        regular_listeners = len(self._listeners.get(event_type, []))
        one_time_listeners = len(self._one_time_listeners.get(event_type, []))
        return regular_listeners > 0 or one_time_listeners > 0
    
    def get_listener_count(self, event_type: EventType) -> int:
        """
        获取指定事件类型的监听器数量
        
        Args:
            event_type: 事件类型
            
        Returns:
            监听器数量
        """
        regular_listeners = len(self._listeners.get(event_type, []))
        one_time_listeners = len(self._one_time_listeners.get(event_type, []))
        return regular_listeners + one_time_listeners
    
    def clear_listeners(self, event_type: Optional[EventType] = None) -> None:
        """
        清除监听器
        
        Args:
            event_type: 事件类型，如果为None则清除所有监听器
        """
        if event_type is None:
            self._listeners.clear()
            self._one_time_listeners.clear()
        else:
            if event_type in self._listeners:
                self._listeners[event_type].clear()
            if event_type in self._one_time_listeners:
                self._one_time_listeners[event_type].clear()


# 全局事件总线实例
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    获取全局事件总线实例
    
    Returns:
        EventBus: 全局事件总线实例
    """
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


def publish_event(event: GameEvent) -> None:
    """
    发布事件到全局事件总线
    
    Args:
        event: 游戏事件对象
    """
    get_event_bus().publish(event)


def subscribe_event(event_type: EventType, listener: Callable[[GameEvent], None]) -> str:
    """
    订阅全局事件总线中的事件
    
    Args:
        event_type: 事件类型
        listener: 事件监听器回调函数
        
    Returns:
        订阅ID
    """
    return get_event_bus().subscribe(event_type, listener)