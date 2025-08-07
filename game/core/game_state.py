"""
游戏状态机模块

实现游戏状态管理器，用于跟踪和控制游戏状态转换。
"""

from enum import Enum
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
import logging

from .event_bus import EventBus, GameEvent, EventType, get_event_bus
from ..utils.constants import (
    GAME_STATE_WAITING, GAME_STATE_DRAWING, 
    GAME_STATE_GUESSING, GAME_STATE_SCORING, GAME_STATE_GAME_OVER
)


class GameState(Enum):
    """游戏状态枚举"""
    WAITING = GAME_STATE_WAITING      # 等待开始
    DRAWING = GAME_STATE_DRAWING      # 绘画阶段
    GUESSING = GAME_STATE_GUESSING    # 猜测阶段
    SCORING = GAME_STATE_SCORING      # 结算阶段
    GAME_OVER = GAME_STATE_GAME_OVER  # 游戏结束


# 定义有效的状态转换
VALID_STATE_TRANSITIONS: Dict[GameState, List[GameState]] = {
    GameState.WAITING: [GameState.DRAWING],
    GameState.DRAWING: [GameState.GUESSING],
    GameState.GUESSING: [GameState.SCORING],
    GameState.SCORING: [GameState.DRAWING, GameState.GAME_OVER],
    GameState.GAME_OVER: [GameState.WAITING]
}


@dataclass
class GameStateContext:
    """游戏状态上下文"""
    # 当前回合数
    current_round: int = 0
    
    # 总回合数
    total_rounds: int = 3
    
    # 当前绘画者
    current_drawer: Optional[str] = None
    
    # 当前词汇
    current_word: Optional[str] = None
    
    # 其他自定义上下文数据
    extra_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}


class GameStateManager:
    """游戏状态管理器"""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        初始化游戏状态管理器
        
        Args:
            event_bus: 事件总线实例，如果为None则使用全局事件总线
        """
        self._current_state: GameState = GameState.WAITING
        self._previous_state: Optional[GameState] = None
        self._state_context: GameStateContext = GameStateContext()
        self._event_bus: EventBus = event_bus or get_event_bus()
        self._state_change_callbacks: List[Callable[[GameState, GameState], None]] = []
        
        # 记录状态转换历史
        self._state_history: List[GameState] = [GameState.WAITING]
        
        # 订阅相关事件
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """订阅相关事件"""
        # 可以在这里订阅需要自动处理状态转换的事件
        pass
    
    @property
    def current_state(self) -> GameState:
        """获取当前游戏状态"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[GameState]:
        """获取前一个游戏状态"""
        return self._previous_state
    
    @property
    def state_context(self) -> GameStateContext:
        """获取状态上下文"""
        return self._state_context
    
    def can_transition_to(self, target_state: GameState) -> bool:
        """
        检查是否可以转换到目标状态
        
        Args:
            target_state: 目标状态
            
        Returns:
            是否可以转换
        """
        if self._current_state == target_state:
            return True
            
        valid_transitions = VALID_STATE_TRANSITIONS.get(self._current_state, [])
        return target_state in valid_transitions
    
    def transition_to(self, target_state: GameState, context: Optional[GameStateContext] = None) -> bool:
        """
        转换到目标状态
        
        Args:
            target_state: 目标状态
            context: 状态上下文（可选）
            
        Returns:
            是否成功转换
        """
        # 验证状态转换是否有效
        if not self.can_transition_to(target_state):
            logging.warning(f"无效的状态转换: {self._current_state.value} -> {target_state.value}")
            return False
        
        # 保存当前状态
        old_state = self._current_state
        
        # 更新状态
        self._previous_state = self._current_state
        self._current_state = target_state
        
        # 更新上下文
        if context:
            self._state_context = context
        
        # 记录状态历史
        self._state_history.append(target_state)
        if len(self._state_history) > 100:  # 限制历史记录长度
            self._state_history.pop(0)
        
        # 触发状态变更回调
        for callback in self._state_change_callbacks:
            try:
                callback(old_state, target_state)
            except Exception as e:
                logging.error(f"状态变更回调执行出错: {e}")
        
        # 发布状态变更事件
        event = GameEvent(
            event_type=EventType.GAME_STATE_CHANGED,
            data={
                "from_state": old_state.value,
                "to_state": target_state.value,
                "context": self._state_context
            }
        )
        self._event_bus.publish(event)
        
        logging.info(f"游戏状态变更: {old_state.value} -> {target_state.value}")
        return True
    
    def add_state_change_callback(self, callback: Callable[[GameState, GameState], None]) -> None:
        """
        添加状态变更回调函数
        
        Args:
            callback: 回调函数，接收(旧状态, 新状态)作为参数
        """
        self._state_change_callbacks.append(callback)
    
    def remove_state_change_callback(self, callback: Callable[[GameState, GameState], None]) -> bool:
        """
        移除状态变更回调函数
        
        Args:
            callback: 要移除的回调函数
            
        Returns:
            是否成功移除
        """
        if callback in self._state_change_callbacks:
            self._state_change_callbacks.remove(callback)
            return True
        return False
    
    def is_in_state(self, state: GameState) -> bool:
        """
        检查当前是否处于指定状态
        
        Args:
            state: 要检查的状态
            
        Returns:
            是否处于指定状态
        """
        return self._current_state == state
    
    def is_in_any_state(self, states: List[GameState]) -> bool:
        """
        检查当前是否处于指定状态列表中的任何状态
        
        Args:
            states: 状态列表
            
        Returns:
            是否处于指定状态列表中的任何状态
        """
        return self._current_state in states
    
    def get_state_history(self, count: Optional[int] = None) -> List[GameState]:
        """
        获取状态历史记录
        
        Args:
            count: 要获取的历史记录数量，如果为None则返回所有历史记录
            
        Returns:
            状态历史记录列表
        """
        if count is None:
            return self._state_history.copy()
        return self._state_history[-count:].copy()
    
    def reset(self) -> None:
        """重置游戏状态"""
        old_state = self._current_state
        self._current_state = GameState.WAITING
        self._previous_state = None
        self._state_context = GameStateContext()
        self._state_history = [GameState.WAITING]
        
        # 发布重置事件
        event = GameEvent(
            event_type=EventType.GAME_RESET,
            data={
                "from_state": old_state.value if old_state else None,
                "to_state": GameState.WAITING.value
            }
        )
        self._event_bus.publish(event)
        
        logging.info("游戏状态已重置")
    
    def is_game_active(self) -> bool:
        """
        检查游戏是否处于活跃状态（非等待和非结束状态）
        
        Returns:
            游戏是否处于活跃状态
        """
        return self._current_state in [GameState.DRAWING, GameState.GUESSING, GameState.SCORING]
    
    def is_game_over(self) -> bool:
        """
        检查游戏是否结束
        
        Returns:
            游戏是否结束
        """
        return self._current_state == GameState.GAME_OVER


# 全局游戏状态管理器实例
_game_state_manager_instance: Optional[GameStateManager] = None


def get_game_state_manager(event_bus: Optional[EventBus] = None) -> GameStateManager:
    """
    获取全局游戏状态管理器实例
    
    Args:
        event_bus: 事件总线实例，如果为None则使用全局事件总线
        
    Returns:
        GameStateManager: 全局游戏状态管理器实例
    """
    global _game_state_manager_instance
    if _game_state_manager_instance is None:
        _game_state_manager_instance = GameStateManager(event_bus)
    return _game_state_manager_instance


def transition_to_state(target_state: GameState, context: Optional[GameStateContext] = None) -> bool:
    """
    转换到目标状态（使用全局状态管理器）
    
    Args:
        target_state: 目标状态
        context: 状态上下文（可选）
        
    Returns:
        是否成功转换
    """
    return get_game_state_manager().transition_to(target_state, context)