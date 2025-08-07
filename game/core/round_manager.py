"""
回合管理器模块

实现游戏回合控制逻辑，包括回合切换、时间管理和回合数据持久化。
"""

import time
import logging
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .event_bus import EventBus, GameEvent, EventType, get_event_bus
from .game_state import GameState, GameStateManager, GameStateContext, get_game_state_manager
from ..data.models.player import Player
from ..data.models.word import Word
from ..data.models.game_data import RoundData
from ..data.repositories.word_repository import WordRepository
from ..utils.constants import MAX_ROUNDS, DRAWING_TIME_LIMIT


@dataclass
class RoundInfo:
    """回合信息数据类"""
    # 回合编号
    round_number: int
    
    # 当前词汇
    current_word: Optional[Word] = None
    
    # 当前绘画者
    current_drawer: Optional[Player] = None
    
    # 回合开始时间
    start_time: Optional[float] = None
    
    # 回合结束时间
    end_time: Optional[float] = None
    
    # 回合限时（秒）
    time_limit: int = DRAWING_TIME_LIMIT
    
    # 已猜中的玩家列表
    correct_guesses: List[Player] = field(default_factory=list)
    
    # 回合是否活跃
    is_active: bool = False


class RoundManager:
    """回合管理器"""
    
    def __init__(
        self, 
        event_bus: Optional[EventBus] = None,
        game_state_manager: Optional[GameStateManager] = None,
        word_repository: Optional[WordRepository] = None
    ):
        """
        初始化回合管理器
        
        Args:
            event_bus: 事件总线实例，如果为None则使用全局事件总线
            game_state_manager: 游戏状态管理器，如果为None则使用全局状态管理器
            word_repository: 词库仓库，如果为None则创建新实例
        """
        self._event_bus: EventBus = event_bus or get_event_bus()
        self._game_state_manager: GameStateManager = game_state_manager or get_game_state_manager(self._event_bus)
        self._word_repository: WordRepository = word_repository or WordRepository()
        
        # 回合信息
        self._current_round: Optional[RoundInfo] = None
        self._round_history: List[RoundInfo] = []
        
        # 玩家列表
        self._players: List[Player] = []
        
        # 当前回合索引（用于确定绘画者）
        self._current_round_index: int = 0
        
        # 回合时间管理
        self._round_start_time: Optional[float] = None
        self._round_end_time: Optional[float] = None
        self._remaining_time: int = 0
        self._timer_callbacks: List[Callable[[int], None]] = []
        
        # 订阅相关事件
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """订阅相关事件"""
        # 可以在这里订阅需要自动处理回合管理的事件
        pass
    
    @property
    def current_round(self) -> Optional[RoundInfo]:
        """获取当前回合信息"""
        return self._current_round
    
    @property
    def round_history(self) -> List[RoundInfo]:
        """获取回合历史"""
        return self._round_history.copy()
    
    @property
    def players(self) -> List[Player]:
        """获取玩家列表"""
        return self._players.copy()
    
    @property
    def current_drawer(self) -> Optional[Player]:
        """获取当前绘画者"""
        if self._current_round and self._current_round.current_drawer:
            return self._current_round.current_drawer
        return None
    
    @property
    def current_word(self) -> Optional[Word]:
        """获取当前词汇"""
        if self._current_round and self._current_round.current_word:
            return self._current_round.current_word
        return None
    
    @property
    def remaining_time(self) -> int:
        """获取剩余时间（秒）"""
        return self._remaining_time
    
    def add_player(self, player: Player) -> None:
        """
        添加玩家
        
        Args:
            player: 玩家对象
        """
        if player not in self._players:
            self._players.append(player)
            logging.info(f"玩家 {player.name} 已添加到游戏中")
    
    def remove_player(self, player: Player) -> bool:
        """
        移除玩家
        
        Args:
            player: 玩家对象
            
        Returns:
            是否成功移除
        """
        if player in self._players:
            self._players.remove(player)
            logging.info(f"玩家 {player.name} 已从游戏中移除")
            return True
        return False
    
    def start_new_round(self, round_number: Optional[int] = None) -> bool:
        """
        开始新回合
        
        Args:
            round_number: 回合编号，如果为None则自动递增
            
        Returns:
            是否成功开始新回合
        """
        # 检查是否有足够的玩家
        if len(self._players) < 2:
            logging.warning("玩家数量不足，至少需要2名玩家")
            return False
        
        # 确定回合编号
        if round_number is None:
            round_number = len(self._round_history) + 1
        
        # 检查回合数限制
        if round_number > MAX_ROUNDS:
            logging.warning(f"已达到最大回合数限制 ({MAX_ROUNDS})")
            return False
        
        # 选择绘画者（轮换）
        drawer_index = (self._current_round_index + round_number - 1) % len(self._players)
        drawer = self._players[drawer_index]
        
        # 选择词汇（避免重复）
        last_word = self._current_round.current_word if self._current_round else None
        word = self._word_repository.get_random_word(exclude_word=last_word)
        if not word:
            logging.error("无法获取词汇")
            return False
        
        # 创建回合信息
        self._current_round = RoundInfo(
            round_number=round_number,
            current_word=word,
            current_drawer=drawer,
            start_time=time.time(),
            is_active=True,
            correct_guesses=[]
        )
        
        # 更新玩家状态
        for player in self._players:
            player.set_drawing_state(player == drawer)
            if player != drawer:
                player.set_guessed_state(False)
        
        # 更新游戏状态
        context = GameStateContext(
            current_round=round_number,
            total_rounds=MAX_ROUNDS,
            current_drawer=drawer.player_id,
            current_word=word.get_display_text()
        )
        
        # 发布回合开始事件
        event = GameEvent(
            event_type=EventType.ROUND_START,
            data={
                "round_number": round_number,
                "drawer": drawer.player_id,
                "word": word.text,
                "word_hint": word.hint,
                "time_limit": DRAWING_TIME_LIMIT
            }
        )
        self._event_bus.publish(event)
        
        # 更新游戏状态为绘画阶段
        self._game_state_manager.transition_to(GameState.DRAWING, context)
        
        # 初始化回合时间
        self._round_start_time = time.time()
        self._remaining_time = DRAWING_TIME_LIMIT
        
        logging.info(f"第 {round_number} 回合开始，绘画者: {drawer.name}，词汇: {word.text}")
        return True
    
    def end_current_round(self) -> bool:
        """
        结束当前回合
        
        Returns:
            是否成功结束回合
        """
        if not self._current_round or not self._current_round.is_active:
            logging.warning("没有活跃的回合可以结束")
            return False
        
        # 更新回合信息
        self._current_round.is_active = False
        self._current_round.end_time = time.time()
        
        # 记录回合历史
        self._round_history.append(self._current_round)
        
        # 发布回合结束事件
        event = GameEvent(
            event_type=EventType.ROUND_END,
            data={
                "round_number": self._current_round.round_number,
                "drawer": self._current_round.current_drawer.player_id if self._current_round.current_drawer else None,
                "word": self._current_round.current_word.text if self._current_round.current_word else None,
                "correct_guesses": [player.player_id for player in self._current_round.correct_guesses],
                "duration": self._current_round.end_time - self._current_round.start_time if self._current_round.start_time else None
            }
        )
        self._event_bus.publish(event)
        
        # 重置当前回合
        self._current_round = None
        self._round_start_time = None
        self._round_end_time = None
        self._remaining_time = 0
        
        logging.info("当前回合已结束")
        return True
    
    def submit_guess(self, player: Player, guess: str) -> bool:
        """
        提交猜测
        
        Args:
            player: 猜测的玩家
            guess: 猜测内容
            
        Returns:
            猜测是否正确
        """
        if not self._current_round or not self._current_round.is_active:
            logging.warning("当前没有活跃的回合")
            return False
        
        if not self._current_round.current_word:
            logging.error("当前回合没有词汇")
            return False
        
        # 检查玩家是否是绘画者
        if player == self._current_round.current_drawer:
            logging.warning("绘画者不能提交猜测")
            return False
        
        # 检查玩家是否已经猜中
        if player in self._current_round.correct_guesses:
            logging.warning(f"玩家 {player.name} 已经猜中了")
            return True  # 已经猜中，返回True但不重复计分
        
        # 检查猜测是否正确
        is_correct = guess.strip().lower() == self._current_round.current_word.text.lower()
        
        # 发布猜测事件
        event = GameEvent(
            event_type=EventType.GUESS_SUBMITTED,
            data={
                "player": player.player_id,
                "guess": guess,
                "is_correct": is_correct
            }
        )
        self._event_bus.publish(event)
        
        if is_correct:
            # 添加到猜中列表
            self._current_round.correct_guesses.append(player)
            player.set_guessed_state(True)
            
            # 发布猜中事件
            correct_event = GameEvent(
                event_type=EventType.GUESS_CORRECT,
                data={
                    "player": player.player_id,
                    "word": self._current_round.current_word.text,
                    "guess_time": time.time() - self._current_round.start_time if self._current_round.start_time else None
                }
            )
            self._event_bus.publish(correct_event)
            
            logging.info(f"玩家 {player.name} 猜中了词汇: {self._current_round.current_word.text}")
        else:
            # 发布猜错事件
            incorrect_event = GameEvent(
                event_type=EventType.GUESS_INCORRECT,
                data={
                    "player": player.player_id,
                    "guess": guess
                }
            )
            self._event_bus.publish(incorrect_event)
            
            logging.info(f"玩家 {player.name} 猜测错误: {guess}")
        
        return is_correct
    
    def update_round_timer(self) -> None:
        """更新回合计时器"""
        if not self._current_round or not self._current_round.is_active:
            return
        
        if not self._round_start_time:
            return
        
        # 计算剩余时间
        elapsed_time = time.time() - self._round_start_time
        self._remaining_time = max(0, DRAWING_TIME_LIMIT - int(elapsed_time))
        
        # 调用计时器回调
        for callback in self._timer_callbacks:
            try:
                callback(self._remaining_time)
            except Exception as e:
                logging.error(f"计时器回调执行出错: {e}")
        
        # 检查回合是否超时
        if self._remaining_time <= 0:
            self.end_current_round()
    
    def add_timer_callback(self, callback: Callable[[int], None]) -> None:
        """
        添加计时器回调函数
        
        Args:
            callback: 回调函数，接收剩余时间（秒）作为参数
        """
        self._timer_callbacks.append(callback)
    
    def remove_timer_callback(self, callback: Callable[[int], None]) -> bool:
        """
        移除计时器回调函数
        
        Args:
            callback: 要移除的回调函数
            
        Returns:
            是否成功移除
        """
        if callback in self._timer_callbacks:
            self._timer_callbacks.remove(callback)
            return True
        return False
    
    def get_round_score(self, player: Player) -> int:
        """
        获取玩家在当前回合的得分
        
        Args:
            player: 玩家对象
            
        Returns:
            玩家得分
        """
        if not self._current_round:
            return 0
        
        # 绘画者得分
        if player == self._current_round.current_drawer:
            # 如果有人猜中，绘画者获得基础分
            if self._current_round.correct_guesses:
                return 20  # 绘画者基础分
            return 0
        
        # 猜测者得分
        if player in self._current_round.correct_guesses:
            # 根据猜中时间计算得分
            if self._current_round.start_time:
                guess_time = time.time() - self._current_round.start_time
                time_bonus = max(0, DRAWING_TIME_LIMIT - int(guess_time))
                return 30 + time_bonus  # 基础分 + 时间奖励
            else:
                return 30  # 无法计算时间奖励时只给基础分
        
        return 0
    
    def is_round_active(self) -> bool:
        """
        检查当前是否有活跃回合
        
        Returns:
            是否有活跃回合
        """
        return self._current_round is not None and self._current_round.is_active
    
    def get_round_progress(self) -> Dict[str, Any]:
        """
        获取回合进度信息
        
        Returns:
            回合进度信息字典
        """
        return {
            "current_round": self._current_round.round_number if self._current_round else None,
            "total_rounds": MAX_ROUNDS,
            "remaining_time": self._remaining_time,
            "time_limit": DRAWING_TIME_LIMIT,
            "drawer": self._current_round.current_drawer.player_id if self._current_round and self._current_round.current_drawer else None,
            "word_hint": self._current_round.current_word.hint if self._current_round and self._current_round.current_word else None,
            "correct_guesses": [player.player_id for player in self._current_round.correct_guesses] if self._current_round else []
        }
    
    def reset(self) -> None:
        """重置回合管理器"""
        # 结束当前回合（如果有）
        if self.is_round_active():
            self.end_current_round()
        
        # 重置状态
        self._current_round = None
        self._round_history = []
        self._current_round_index = 0
        self._round_start_time = None
        self._round_end_time = None
        self._remaining_time = 0
        self._timer_callbacks = []
        
        logging.info("回合管理器已重置")


# 全局回合管理器实例
_round_manager_instance: Optional[RoundManager] = None


def get_round_manager(
    event_bus: Optional[EventBus] = None,
    game_state_manager: Optional[GameStateManager] = None,
    word_repository: Optional[WordRepository] = None
) -> RoundManager:
    """
    获取全局回合管理器实例
    
    Args:
        event_bus: 事件总线实例
        game_state_manager: 游戏状态管理器
        word_repository: 词库仓库
        
    Returns:
        RoundManager: 全局回合管理器实例
    """
    global _round_manager_instance
    if _round_manager_instance is None:
        _round_manager_instance = RoundManager(event_bus, game_state_manager, word_repository)
    return _round_manager_instance