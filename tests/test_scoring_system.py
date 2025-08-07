"""
积分计算系统单元测试
"""

import sys
import os
import unittest
from unittest.mock import Mock
from datetime import datetime

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.core.scoring_system import ScoringSystem, ScoreRecord, LeaderboardEntry
from game.core.event_bus import EventBus, GameEvent, EventType
from game.data.models.player import Player, PlayerType
from game.data.models.game_data import GameData


class TestScoringSystem(unittest.TestCase):
    """测试积分计算系统"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试依赖
        self.event_bus = EventBus()
        
        # 创建积分计算系统
        self.scoring_system = ScoringSystem(self.event_bus)
        
        # 创建测试玩家
        self.player1 = Player("player1", "Alice", PlayerType.HUMAN)
        self.player2 = Player("player2", "Bob", PlayerType.AI)
        self.player3 = Player("player3", "Charlie", PlayerType.HUMAN)
    
    def test_calculate_drawer_score(self):
        """测试计算绘画者得分"""
        # 有人猜中时绘画者得分
        score = self.scoring_system.calculate_drawer_score(True)
        self.assertEqual(score, 20)  # BASE_SCORE_FOR_DRAWER
        
        # 没人猜中时绘画者得分
        score = self.scoring_system.calculate_drawer_score(False)
        self.assertEqual(score, 0)
    
    def test_calculate_guesser_score(self):
        """测试计算猜测者得分"""
        time_limit = 90
        
        # 快速猜中（获得所有奖励）
        score = self.scoring_system.calculate_guesser_score(10, time_limit)
        # 基础分30 + 时间奖励(90-10)*1 + 速度奖励10 = 30 + 80 + 10 = 120
        self.assertEqual(score, 120)
        
        # 中等时间猜中（获得基础奖励）
        score = self.scoring_system.calculate_guesser_score(45, time_limit)
        # 基础分30 + 时间奖励(90-45)*1 = 30 + 45 = 75
        self.assertEqual(score, 75)
        
        # 慢速猜中（只获得基础分）
        score = self.scoring_system.calculate_guesser_score(85, time_limit)
        # 基础分30 + 时间奖励(90-85)*1 = 30 + 5 = 35
        self.assertEqual(score, 35)
    
    def test_add_score(self):
        """测试添加玩家得分"""
        # 添加得分
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        
        # 检查玩家总分
        score = self.scoring_system.get_player_score("player1")
        self.assertEqual(score, 50)
        
        # 再次添加得分
        self.scoring_system.add_score(self.player1, 30, 1, "guesser")
        
        # 检查累计得分
        score = self.scoring_system.get_player_score("player1")
        self.assertEqual(score, 80)
        
        # 检查积分记录
        records = self.scoring_system.get_score_records("player1")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].score, 50)
        self.assertEqual(records[1].score, 30)
    
    def test_get_player_scores(self):
        """测试获取所有玩家得分"""
        # 添加多个玩家得分
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        self.scoring_system.add_score(self.player3, 40, 1, "guesser")
        
        # 获取所有玩家得分
        scores = self.scoring_system.get_player_scores()
        self.assertEqual(len(scores), 3)
        self.assertEqual(scores["player1"], 50)
        self.assertEqual(scores["player2"], 30)
        self.assertEqual(scores["player3"], 40)
    
    def test_get_score_records(self):
        """测试获取积分记录"""
        # 添加记录
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        self.scoring_system.add_score(self.player1, 30, 1, "guesser")
        self.scoring_system.add_score(self.player2, 40, 1, "guesser")
        self.scoring_system.add_score(self.player1, 20, 2, "drawer")
        
        # 获取特定玩家记录
        player1_records = self.scoring_system.get_score_records("player1")
        self.assertEqual(len(player1_records), 3)
        
        # 获取特定回合记录
        round1_records = self.scoring_system.get_score_records(round_number=1)
        self.assertEqual(len(round1_records), 3)
        
        # 获取特定玩家和回合记录
        records = self.scoring_system.get_score_records("player1", 1)
        self.assertEqual(len(records), 2)
    
    def test_get_leaderboard(self):
        """测试获取排行榜"""
        # 创建游戏数据
        game_data = GameData("test_game")
        game_data.add_player(self.player1)
        game_data.add_player(self.player2)
        game_data.add_player(self.player3)
        
        # 添加得分
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        self.scoring_system.add_score(self.player3, 40, 1, "guesser")
        self.scoring_system.add_score(self.player1, 20, 2, "drawer")
        
        # 获取排行榜
        leaderboard = self.scoring_system.get_leaderboard(game_data)
        self.assertEqual(len(leaderboard), 3)
        
        # 检查排名顺序
        self.assertEqual(leaderboard[0].player_name, "Alice")
        self.assertEqual(leaderboard[0].total_score, 70)
        self.assertEqual(leaderboard[0].rank, 1)
        
        self.assertEqual(leaderboard[1].player_name, "Charlie")
        self.assertEqual(leaderboard[1].total_score, 40)
        self.assertEqual(leaderboard[1].rank, 2)
        
        self.assertEqual(leaderboard[2].player_name, "Bob")
        self.assertEqual(leaderboard[2].total_score, 30)
        self.assertEqual(leaderboard[2].rank, 3)
    
    def test_leaderboard_with_stats(self):
        """测试排行榜统计信息"""
        # 添加得分并检查统计信息
        self.scoring_system.add_score(self.player1, 20, 1, "drawer")
        self.scoring_system.add_score(self.player1, 30, 1, "guesser")
        self.scoring_system.add_score(self.player2, 20, 1, "drawer")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        
        # 获取排行榜
        leaderboard = self.scoring_system.get_leaderboard()
        
        # 查找玩家条目
        player1_entry = None
        player2_entry = None
        for entry in leaderboard:
            if entry.player_id == "player1":
                player1_entry = entry
            elif entry.player_id == "player2":
                player2_entry = entry
        
        # 检查统计信息
        self.assertIsNotNone(player1_entry)
        self.assertIsNotNone(player2_entry)
        
        self.assertEqual(player1_entry.correct_guesses, 1)
        self.assertEqual(player1_entry.times_as_drawer, 1)
        
        self.assertEqual(player2_entry.correct_guesses, 2)
        self.assertEqual(player2_entry.times_as_drawer, 1)
    
    def test_reset(self):
        """测试重置积分系统"""
        # 添加数据
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        
        # 检查数据存在
        self.assertEqual(len(self.scoring_system.get_player_scores()), 2)
        self.assertEqual(len(self.scoring_system.get_score_records()), 2)
        
        # 重置系统
        self.scoring_system.reset()
        
        # 检查数据已清除
        self.assertEqual(len(self.scoring_system.get_player_scores()), 0)
        self.assertEqual(len(self.scoring_system.get_score_records()), 0)
    
    def test_get_game_summary(self):
        """测试获取游戏总结"""
        # 添加数据
        self.scoring_system.add_score(self.player1, 50, 1, "drawer")
        self.scoring_system.add_score(self.player2, 30, 1, "guesser")
        self.scoring_system.add_score(self.player3, 40, 1, "guesser")
        
        # 获取总结
        summary = self.scoring_system.get_game_summary()
        self.assertEqual(summary["total_scores"], 120)  # 50 + 30 + 40
        self.assertEqual(summary["total_players"], 3)
        self.assertEqual(summary["total_records"], 3)
    
    def test_event_subscription(self):
        """测试事件订阅"""
        # 检查事件订阅
        self.assertTrue(self.event_bus.has_listeners(EventType.GUESS_CORRECT))
        self.assertTrue(self.event_bus.has_listeners(EventType.ROUND_END))


if __name__ == '__main__':
    unittest.main()