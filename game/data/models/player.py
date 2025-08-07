"""
玩家数据模型模块

定义玩家相关的数据结构和操作方法。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PlayerType(Enum):
    """玩家类型枚举"""
    HUMAN = "human"
    AI = "ai"


@dataclass
class Player:
    """玩家数据模型"""
    
    # 玩家ID
    player_id: str
    
    # 玩家名称
    name: str
    
    # 玩家类型（人类或AI）
    player_type: PlayerType
    
    # 玩家分数
    score: int = 0
    
    # 玩家是否为当前绘画者
    is_drawing: bool = False
    
    # 玩家是否已猜中答案
    has_guessed: bool = False
    
    def reset_round_state(self) -> None:
        """重置回合状态"""
        self.is_drawing = False
        self.has_guessed = False
    
    def reset_game_state(self) -> None:
        """重置游戏状态"""
        self.score = 0
        self.reset_round_state()
    
    def add_score(self, points: int) -> None:
        """增加分数"""
        if points > 0:
            self.score += points
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """设置绘画状态"""
        self.is_drawing = is_drawing
        # 如果是绘画者，则重置猜题状态
        if is_drawing:
            self.has_guessed = False
    
    def set_guessed_state(self, has_guessed: bool) -> None:
        """设置猜题状态"""
        self.has_guessed = has_guessed