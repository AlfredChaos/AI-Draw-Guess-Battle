"""
游戏主引擎模块

实现游戏主控制器，集成所有核心系统并管理游戏生命周期。
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
import time

from .event_bus import EventBus, GameEvent, EventType, get_event_bus
from .game_state import GameState, GameStateManager, GameStateContext, get_game_state_manager
from .round_manager import RoundManager, RoundInfo
from .scoring_system import ScoringSystem
from ..data.models.player import Player, PlayerType
from ..data.models.game_data import GameData
from ..data.models.word import Word
from ..data.repositories.word_repository import WordRepository
from ..utils.constants import MAX_ROUNDS
from ..config.config_manager import ConfigManager
from ..ui.game_display import GameDisplay


class GameEngine:
    """游戏主引擎"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """初始化游戏引擎
        
        Args:
            config_manager: 配置管理器，如果为None则使用默认配置
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # 初始化核心组件
        self.event_bus: EventBus = get_event_bus()
        self.state_manager: GameStateManager = get_game_state_manager()
        self.round_manager: RoundManager = RoundManager()
        self.scoring_system: ScoringSystem = ScoringSystem()
        self.word_repository: WordRepository = WordRepository()
        
        # 初始化游戏显示界面
        self.game_display: GameDisplay = GameDisplay(self.event_bus)
        
        # 初始化游戏数据
        game_id = str(uuid.uuid4())
        self.game_data: GameData = GameData(game_id=game_id)
        
        # 游戏运行状态
        self.is_running: bool = False
        
        # 注册事件监听器
        self._register_event_listeners()
        
        self.logger.info("Game engine initialized")
    
    def _register_event_listeners(self) -> None:
        """注册事件监听器"""
        # 监听游戏状态变更事件
        self.event_bus.subscribe(EventType.GAME_STATE_CHANGED, self._on_game_state_changed)
        
        # 监听回合开始事件
        self.event_bus.subscribe(EventType.ROUND_START, self._on_round_start)
        
        # 监听回合结束事件
        self.event_bus.subscribe(EventType.ROUND_END, self._on_round_end)
        
        # 监听游戏结束事件
        self.event_bus.subscribe(EventType.GAME_END, self._on_game_end)
        
        self.logger.debug("Event listeners registered")
    
    def _on_game_state_changed(self, event: GameEvent) -> None:
        """处理游戏状态变更事件"""
        self.logger.debug(f"Game state changed to: {event.data}")
    
    def _on_round_start(self, event: GameEvent) -> None:
        """处理回合开始事件"""
        self.logger.info(f"Round {event.data.get('round_number', 'unknown')} started")
    
    def _on_round_end(self, event: GameEvent) -> None:
        """处理回合结束事件"""
        self.logger.info(f"Round {event.data.get('round_number', 'unknown')} ended")
    
    def _on_game_end(self, event: GameEvent) -> None:
        """处理游戏结束事件"""
        self.logger.info("Game ended")
        self.is_running = False
    
    def add_player(self, player: Player) -> None:
        """添加玩家到游戏中"""
        self.game_data.players.append(player)
        self.logger.info(f"Player {player.name} added to game")
        
        # 发布玩家加入事件
        event = GameEvent(
            event_type=EventType.PLAYER_JOIN,
            data={"player_id": player.player_id, "player_name": player.name}
        )
        self.event_bus.publish(event)
    
    def remove_player(self, player_id: str) -> bool:
        """从游戏中移除玩家"""
        for i, player in enumerate(self.game_data.players):
            if player.player_id == player_id:
                removed_player = self.game_data.players.pop(i)
                self.logger.info(f"Player {removed_player.name} removed from game")
                
                # 发布玩家离开事件
                event = GameEvent(
                    event_type=EventType.PLAYER_LEAVE,
                    data={"player_id": player_id, "player_name": removed_player.name}
                )
                self.event_bus.publish(event)
                return True
        return False
    
    def start_game(self) -> bool:
        """启动游戏"""
        try:
            self.logger.info("Starting game")
            
            # 检查玩家数量
            if len(self.game_data.players) < 1:
                self.logger.error("Cannot start game: Not enough players")
                return False
            
            # 设置游戏运行状态
            self.is_running = True
            
            # 初始化游戏数据
            self.game_data.start_game()
            
            # 获取最大回合数，优先使用配置中的值
            max_rounds = MAX_ROUNDS
            if self.config_manager is not None:
                max_rounds = self.config_manager.game_config.max_rounds
            
            # 初始化游戏状态上下文
            context = GameStateContext(
                total_rounds=max_rounds,
                current_round=0
            )
            
            # 切换到等待状态并传递上下文
            success = self.state_manager.transition_to(GameState.WAITING, context)
            if not success:
                self.logger.error("Failed to transition to WAITING state")
                return False
            
            # 发布游戏开始事件
            event = GameEvent(
                event_type=EventType.GAME_START,
                data={"player_count": len(self.game_data.players), "game_id": self.game_data.game_id}
            )
            self.event_bus.publish(event)
            
            self.logger.info("Game started successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to start game: {e}")
            return False
    
    def end_game(self) -> None:
        """结束游戏"""
        self.logger.info("Ending game")
        
        # 更新游戏数据
        self.game_data.end_game()
        
        # 设置游戏运行状态为False
        self.is_running = False
        
        # 发布游戏结束事件
        event = GameEvent(
            event_type=EventType.GAME_END,
            data={"final_scores": self.scoring_system.get_leaderboard(self.game_data), 
                  "game_id": self.game_data.game_id}
        )
        self.event_bus.publish(event)
        
        self.logger.info("Game ended")
    
    def update(self, delta_time: float) -> None:
        """更新游戏逻辑"""
        # 游戏主循环更新逻辑
        if not self.is_running:
            return
        
        # 根据当前状态执行不同的更新逻辑
        current_state = self.state_manager.get_state()
        
        if current_state == GameState.WAITING:
            self._update_waiting_state()
        elif current_state == GameState.DRAWING:
            self._update_drawing_state(delta_time)
        elif current_state == GameState.GUESSING:
            self._update_guessing_state(delta_time)
        elif current_state == GameState.SCORING:
            self._update_scoring_state()
        elif current_state == GameState.GAME_OVER:
            self._update_game_over_state()
    
    def _update_waiting_state(self) -> None:
        """更新等待状态"""
        # 在等待状态下，可以处理玩家准备等逻辑
        pass
    
    def _update_drawing_state(self, delta_time: float) -> None:
        """更新绘画状态"""
        # 处理绘画逻辑
        pass
    
    def _update_guessing_state(self, delta_time: float) -> None:
        """更新猜测状态"""
        # 处理猜测逻辑
        pass
    
    def _update_scoring_state(self) -> None:
        """更新结算状态"""
        # 处理积分结算逻辑
        pass
    
    def _update_game_over_state(self) -> None:
        """更新游戏结束状态"""
        # 处理游戏结束逻辑
        pass
    
    def get_game_data(self) -> GameData:
        """获取游戏数据"""
        return self.game_data
    
    def is_game_running(self) -> bool:
        """检查游戏是否正在运行"""
        return self.is_running


# 全局游戏引擎实例
_game_engine: Optional[GameEngine] = None


def get_game_engine() -> GameEngine:
    """获取全局游戏引擎实例"""
    global _game_engine
    if _game_engine is None:
        _game_engine = GameEngine()
    return _game_engine


def reset_game_engine() -> None:
    """重置全局游戏引擎实例"""
    global _game_engine
    _game_engine = None