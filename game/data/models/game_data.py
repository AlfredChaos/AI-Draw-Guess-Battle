"""
游戏数据模型模块

定义游戏整体数据结构和操作方法。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from .player import Player
from .word import Word


@dataclass
class RoundData:
    """回合数据模型"""
    
    # 回合编号
    round_number: int
    
    # 当前词汇
    current_word: Optional[Word] = None
    
    # 绘画者
    drawer: Optional[Player] = None
    
    # 已猜中的玩家列表
    correct_guesses: List[Player] = field(default_factory=list)
    
    # 回合开始时间
    start_time: Optional[datetime] = None
    
    # 回合结束时间
    end_time: Optional[datetime] = None
    
    # 回合是否结束
    is_finished: bool = False
    
    def start_round(self, word: Word, drawer: Player) -> None:
        """开始回合"""
        self.current_word = word
        self.drawer = drawer
        self.correct_guesses = []
        self.start_time = datetime.now()
        self.is_finished = False
    
    def end_round(self) -> None:
        """结束回合"""
        self.end_time = datetime.now()
        self.is_finished = True
    
    def add_correct_guess(self, player: Player) -> None:
        """添加正确猜测的玩家"""
        if player not in self.correct_guesses:
            self.correct_guesses.append(player)
    
    def get_duration(self) -> Optional[float]:
        """获取回合持续时间（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class GameData:
    """游戏数据模型"""
    
    # 游戏ID
    game_id: str
    
    # 玩家列表
    players: List[Player] = field(default_factory=list)
    
    # 回合数据列表
    rounds: List[RoundData] = field(default_factory=list)
    
    # 当前回合索引
    current_round_index: int = 0
    
    # 游戏开始时间
    start_time: Optional[datetime] = None
    
    # 游戏结束时间
    end_time: Optional[datetime] = None
    
    # 游戏是否正在进行
    is_active: bool = False
    
    # 游戏配置（额外配置数据）
    config: Dict[str, Any] = field(default_factory=dict)
    
    def start_game(self) -> None:
        """开始游戏"""
        self.start_time = datetime.now()
        self.is_active = True
        self.current_round_index = 0
    
    def end_game(self) -> None:
        """结束游戏"""
        self.end_time = datetime.now()
        self.is_active = False
    
    def add_player(self, player: Player) -> None:
        """添加玩家"""
        if player not in self.players:
            self.players.append(player)
    
    def remove_player(self, player: Player) -> bool:
        """移除玩家"""
        if player in self.players:
            self.players.remove(player)
            return True
        return False
    
    def add_round(self, round_data: RoundData) -> None:
        """添加回合数据"""
        self.rounds.append(round_data)
    
    def get_current_round(self) -> Optional[RoundData]:
        """获取当前回合"""
        if 0 <= self.current_round_index < len(self.rounds):
            return self.rounds[self.current_round_index]
        return None
    
    def next_round(self) -> bool:
        """进入下一回合"""
        if self.current_round_index < len(self.rounds) - 1:
            self.current_round_index += 1
            return True
        return False
    
    def get_game_duration(self) -> Optional[float]:
        """获取游戏总持续时间（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_winner(self) -> Optional[Player]:
        """获取获胜玩家"""
        if not self.players:
            return None
        
        return max(self.players, key=lambda player: player.score)
    
    def get_player_rankings(self) -> List[Player]:
        """获取玩家排名（按分数降序）"""
        return sorted(self.players, key=lambda player: player.score, reverse=True)