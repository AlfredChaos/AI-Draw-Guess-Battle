"""
积分计算系统模块

实现游戏积分算法和排行榜功能。
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

from .event_bus import EventBus, GameEvent, EventType, get_event_bus
from ..data.models.player import Player
from ..data.models.game_data import GameData
from ..utils.constants import (
    BASE_SCORE_FOR_DRAWER, BASE_SCORE_FOR_GUESSER, 
    TIME_BONUS_FACTOR, SPEED_BONUS_THRESHOLD, SPEED_BONUS_POINTS
)


@dataclass
class ScoreRecord:
    """积分记录"""
    # 玩家ID
    player_id: str
    
    # 玩家名称
    player_name: str
    
    # 回合数
    round_number: int
    
    # 得分
    score: int
    
    # 得分类型（绘画者/猜测者）
    score_type: str
    
    # 得分时间
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 额外信息
    extra_info: Dict = field(default_factory=dict)


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    # 玩家ID
    player_id: str
    
    # 玩家名称
    player_name: str
    
    # 总分
    total_score: int
    
    # 排名
    rank: int = 0
    
    # 猜测正确次数
    correct_guesses: int = 0
    
    # 担任绘画者次数
    times_as_drawer: int = 0


class ScoringSystem:
    """积分计算系统"""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        初始化积分计算系统
        
        Args:
            event_bus: 事件总线实例，如果为None则使用全局事件总线
        """
        self._event_bus: EventBus = event_bus or get_event_bus()
        
        # 积分记录
        self._score_records: List[ScoreRecord] = []
        
        # 玩家积分跟踪
        self._player_scores: Dict[str, int] = {}
        
        # 玩家统计信息
        self._player_stats: Dict[str, Dict[str, int]] = {}
        
        # 订阅相关事件
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """订阅相关事件"""
        # 订阅猜中事件以自动计算积分
        self._event_bus.subscribe(EventType.GUESS_CORRECT, self._on_guess_correct)
        self._event_bus.subscribe(EventType.ROUND_END, self._on_round_end)
    
    def _on_guess_correct(self, event: GameEvent) -> None:
        """处理猜中事件"""
        # 这里只记录事件，实际积分计算由专门的方法处理
        logging.debug(f"玩家 {event.data['player']} 猜中了词汇")
    
    def _on_round_end(self, event: GameEvent) -> None:
        """处理回合结束事件"""
        # 回合结束时更新排行榜
        self._update_leaderboard()
    
    def calculate_drawer_score(self, has_correct_guesses: bool) -> int:
        """
        计算绘画者得分
        
        Args:
            has_correct_guesses: 是否有人猜中了词汇
            
        Returns:
            绘画者得分
        """
        if has_correct_guesses:
            return BASE_SCORE_FOR_DRAWER
        return 0
    
    def calculate_guesser_score(self, guess_time: float, time_limit: int) -> int:
        """
        计算猜测者得分
        
        Args:
            guess_time: 猜中所用时间（秒）
            time_limit: 回合时间限制（秒）
            
        Returns:
            猜测者得分
        """
        # 基础分
        score = BASE_SCORE_FOR_GUESSER
        
        # 时间奖励
        time_bonus = max(0, int((time_limit - guess_time) * TIME_BONUS_FACTOR))
        score += time_bonus
        
        # 速度奖励（如果在前1/3时间内猜中）
        if guess_time <= time_limit * SPEED_BONUS_THRESHOLD:
            score += SPEED_BONUS_POINTS
        
        return score
    
    def add_score(self, player: Player, score: int, round_number: int, score_type: str, 
                  extra_info: Optional[Dict] = None) -> None:
        """
        添加玩家得分
        
        Args:
            player: 玩家对象
            score: 得分数
            round_number: 回合数
            score_type: 得分类型
            extra_info: 额外信息
        """
        if extra_info is None:
            extra_info = {}
        
        # 创建积分记录
        record = ScoreRecord(
            player_id=player.player_id,
            player_name=player.name,
            round_number=round_number,
            score=score,
            score_type=score_type,
            extra_info=extra_info
        )
        
        # 添加到记录列表
        self._score_records.append(record)
        
        # 更新玩家总分
        if player.player_id not in self._player_scores:
            self._player_scores[player.player_id] = 0
        
        self._player_scores[player.player_id] += score
        
        # 更新玩家统计信息
        if player.player_id not in self._player_stats:
            self._player_stats[player.player_id] = {
                "correct_guesses": 0,
                "times_as_drawer": 0
            }
        
        if score_type == "guesser":
            self._player_stats[player.player_id]["correct_guesses"] += 1
        elif score_type == "drawer":
            self._player_stats[player.player_id]["times_as_drawer"] += 1
        
        # 发布积分更新事件
        event = GameEvent(
            event_type=EventType.SCORE_UPDATE,
            data={
                "player_id": player.player_id,
                "player_name": player.name,
                "score": score,
                "total_score": self._player_scores[player.player_id],
                "round_number": round_number,
                "score_type": score_type
            }
        )
        self._event_bus.publish(event)
        
        logging.info(f"玩家 {player.name} 在第 {round_number} 回合获得 {score} 分，总分: {self._player_scores[player.player_id]}")
    
    def get_player_score(self, player_id: str) -> int:
        """
        获取玩家总分
        
        Args:
            player_id: 玩家ID
            
        Returns:
            玩家总分
        """
        return self._player_scores.get(player_id, 0)
    
    def get_player_scores(self) -> Dict[str, int]:
        """
        获取所有玩家的总分
        
        Returns:
            玩家总分字典
        """
        return self._player_scores.copy()
    
    def get_score_records(self, player_id: Optional[str] = None, 
                         round_number: Optional[int] = None) -> List[ScoreRecord]:
        """
        获取积分记录
        
        Args:
            player_id: 玩家ID（可选）
            round_number: 回合数（可选）
            
        Returns:
            积分记录列表
        """
        records = self._score_records
        
        if player_id:
            records = [r for r in records if r.player_id == player_id]
        
        if round_number:
            records = [r for r in records if r.round_number == round_number]
        
        return records
    
    def _update_leaderboard(self) -> None:
        """更新排行榜"""
        # 实际应用中，这里可能触发排行榜更新事件
        logging.debug("排行榜已更新")
    
    def get_leaderboard(self, game_data: Optional[GameData] = None) -> List[LeaderboardEntry]:
        """
        获取排行榜
        
        Args:
            game_data: 游戏数据（可选，用于获取玩家详细信息）
            
        Returns:
            排行榜条目列表
        """
        # 创建排行榜条目
        entries: List[LeaderboardEntry] = []
        
        # 获取所有玩家ID
        player_ids = set(self._player_scores.keys())
        
        # 如果提供了游戏数据，添加其中的玩家
        if game_data:
            for player in game_data.players:
                player_ids.add(player.player_id)
        
        # 为每个玩家创建排行榜条目
        for player_id in player_ids:
            # 获取玩家名称
            player_name = f"玩家{player_id}"
            if game_data:
                for player in game_data.players:
                    if player.player_id == player_id:
                        player_name = player.name
                        break
            
            # 获取总分
            total_score = self._player_scores.get(player_id, 0)
            
            # 获取统计信息
            stats = self._player_stats.get(player_id, {})
            correct_guesses = stats.get("correct_guesses", 0)
            times_as_drawer = stats.get("times_as_drawer", 0)
            
            # 创建条目
            entry = LeaderboardEntry(
                player_id=player_id,
                player_name=player_name,
                total_score=total_score,
                correct_guesses=correct_guesses,
                times_as_drawer=times_as_drawer
            )
            entries.append(entry)
        
        # 按总分排序
        entries.sort(key=lambda x: x.total_score, reverse=True)
        
        # 设置排名
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        return entries
    
    def reset(self) -> None:
        """重置积分系统"""
        self._score_records.clear()
        self._player_scores.clear()
        self._player_stats.clear()
        
        logging.info("积分系统已重置")
    
    def get_game_summary(self) -> Dict[str, Any]:
        """
        获取游戏总结信息
        
        Returns:
            游戏总结信息字典
        """
        total_scores = sum(self._player_scores.values())
        return {
            "total_scores": total_scores,
            "total_players": len(self._player_scores),
            "total_records": len(self._score_records)
        }


# 全局积分计算系统实例
_scoring_system_instance: Optional[ScoringSystem] = None


def get_scoring_system(event_bus: Optional[EventBus] = None) -> ScoringSystem:
    """
    获取全局积分计算系统实例
    
    Args:
        event_bus: 事件总线实例
        
    Returns:
        ScoringSystem: 全局积分计算系统实例
    """
    global _scoring_system_instance
    if _scoring_system_instance is None:
        _scoring_system_instance = ScoringSystem(event_bus)
    return _scoring_system_instance