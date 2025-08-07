"""
回合管理器单元测试
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import time

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.core.round_manager import RoundManager, RoundInfo
from game.core.event_bus import EventBus
from game.core.game_state import GameStateManager
from game.data.models.player import Player, PlayerType
from game.data.models.word import Word
from game.data.repositories.word_repository import WordRepository


class TestRoundManager(unittest.TestCase):
    """测试回合管理器"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试依赖
        self.event_bus = EventBus()
        self.game_state_manager = GameStateManager(self.event_bus)
        self.word_repository = WordRepository()
        
        # 创建回合管理器
        self.round_manager = RoundManager(
            event_bus=self.event_bus,
            game_state_manager=self.game_state_manager,
            word_repository=self.word_repository
        )
        
        # 创建测试玩家
        self.player1 = Player("player1", "Alice", PlayerType.HUMAN)
        self.player2 = Player("player2", "Bob", PlayerType.AI)
        self.player3 = Player("player3", "Charlie", PlayerType.HUMAN)
        
        # 添加玩家到回合管理器
        self.round_manager.add_player(self.player1)
        self.round_manager.add_player(self.player2)
        self.round_manager.add_player(self.player3)
    
    def test_player_management(self):
        """测试玩家管理"""
        # 检查初始玩家列表
        players = self.round_manager.players
        self.assertEqual(len(players), 3)
        self.assertIn(self.player1, players)
        self.assertIn(self.player2, players)
        self.assertIn(self.player3, players)
        
        # 移除玩家
        result = self.round_manager.remove_player(self.player2)
        self.assertTrue(result)
        
        # 检查玩家列表
        players = self.round_manager.players
        self.assertEqual(len(players), 2)
        self.assertIn(self.player1, players)
        self.assertIn(self.player3, players)
        self.assertNotIn(self.player2, players)
        
        # 尝试移除不存在的玩家
        fake_player = Player("fake", "Fake", PlayerType.HUMAN)
        result = self.round_manager.remove_player(fake_player)
        self.assertFalse(result)
    
    def test_start_new_round(self):
        """测试开始新回合"""
        # 开始第一回合
        result = self.round_manager.start_new_round(1)
        self.assertTrue(result)
        
        # 检查回合状态
        current_round = self.round_manager.current_round
        self.assertIsNotNone(current_round)
        self.assertEqual(current_round.round_number, 1)
        self.assertTrue(current_round.is_active)
        self.assertIsNotNone(current_round.current_word)
        self.assertIsNotNone(current_round.current_drawer)
        self.assertIsNotNone(current_round.start_time)
        
        # 检查玩家状态
        drawer = current_round.current_drawer
        self.assertTrue(drawer.is_drawing)
        self.assertFalse(drawer.has_guessed)
        
        for player in self.round_manager.players:
            if player != drawer:
                self.assertFalse(player.is_drawing)
                self.assertFalse(player.has_guessed)
    
    def test_start_round_insufficient_players(self):
        """测试玩家不足时开始回合"""
        # 创建只有1个玩家的回合管理器
        rm = RoundManager(self.event_bus, self.game_state_manager, self.word_repository)
        rm.add_player(self.player1)
        
        # 尝试开始回合应该失败
        result = rm.start_new_round(1)
        self.assertFalse(result)
    
    def test_end_current_round(self):
        """测试结束当前回合"""
        # 开始回合
        self.round_manager.start_new_round(1)
        current_round = self.round_manager.current_round
        self.assertIsNotNone(current_round)
        self.assertTrue(current_round.is_active)
        
        # 结束回合
        result = self.round_manager.end_current_round()
        self.assertTrue(result)
        
        # 检查回合状态
        self.assertIsNone(self.round_manager.current_round)
        
        # 检查历史记录
        history = self.round_manager.round_history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], current_round)
        self.assertFalse(history[0].is_active)
    
    def test_submit_guess(self):
        """测试提交猜测"""
        # 开始回合
        self.round_manager.start_new_round(1)
        current_round = self.round_manager.current_round
        drawer = current_round.current_drawer
        word = current_round.current_word
        
        # 获取一个非绘画者玩家
        guesser = None
        for player in self.round_manager.players:
            if player != drawer:
                guesser = player
                break
        
        # 提交正确猜测
        result = self.round_manager.submit_guess(guesser, word.text)
        self.assertTrue(result)
        self.assertIn(guesser, current_round.correct_guesses)
        self.assertTrue(guesser.has_guessed)
        
        # 尝试再次提交猜测（应该返回True但不重复计分）
        result = self.round_manager.submit_guess(guesser, word.text)
        self.assertTrue(result)
        
        # 提交错误猜测
        other_guesser = self.player3 if guesser != self.player3 else self.player2
        result = self.round_manager.submit_guess(other_guesser, "错误答案")
        self.assertFalse(result)
        self.assertNotIn(other_guesser, current_round.correct_guesses)
        self.assertFalse(other_guesser.has_guessed)
    
    def test_submit_guess_by_drawer(self):
        """测试绘画者提交猜测"""
        # 开始回合
        self.round_manager.start_new_round(1)
        current_round = self.round_manager.current_round
        drawer = current_round.current_drawer
        
        # 绘画者提交猜测应该失败
        result = self.round_manager.submit_guess(drawer, "任何答案")
        self.assertFalse(result)
    
    def test_round_timer_update(self):
        """测试回合计时器更新"""
        # 开始回合
        self.round_manager.start_new_round(1)
        
        # 手动设置开始时间以控制测试
        self.round_manager._round_start_time = time.time() - 10  # 模拟已经过了10秒
        
        # 更新计时器
        self.round_manager.update_round_timer()
        self.assertEqual(self.round_manager.remaining_time, 80)  # 90-10=80
    
    def test_timer_callbacks(self):
        """测试计时器回调"""
        callback = Mock()
        self.round_manager.add_timer_callback(callback)
        
        # 开始回合
        self.round_manager.start_new_round(1)
        
        # 手动设置开始时间以控制测试
        self.round_manager._round_start_time = time.time() - 10  # 模拟已经过了10秒
        
        # 更新计时器应该触发回调
        self.round_manager.update_round_timer()
        callback.assert_called_with(80)  # 90-10=80秒剩余
    
    def test_get_round_score(self):
        """测试获取回合得分"""
        # 开始回合
        self.round_manager.start_new_round(1)
        current_round = self.round_manager.current_round
        drawer = current_round.current_drawer
        word = current_round.current_word
        
        # 获取绘画者初始得分（应该为0，因为还没人猜中）
        score = self.round_manager.get_round_score(drawer)
        self.assertEqual(score, 0)
        
        # 获取猜测者初始得分（应该为0）
        guesser = None
        for player in self.round_manager.players:
            if player != drawer:
                guesser = player
                break
        
        score = self.round_manager.get_round_score(guesser)
        self.assertEqual(score, 0)
        
        # 提交正确猜测
        # 手动设置开始时间以控制测试
        current_round.start_time = time.time() - 30  # 模拟已经过了30秒
        
        self.round_manager.submit_guess(guesser, word.text)
        
        # 绘画者得分（有人猜中了）
        score = self.round_manager.get_round_score(drawer)
        self.assertEqual(score, 20)  # 基础分
        
        # 猜测者得分
        score = self.round_manager.get_round_score(guesser)
        # 注意：实际得分可能因为时间精度而略有不同，这里只做基本验证
        self.assertGreaterEqual(score, 30)  # 至少有基础分30
    
    def test_round_progress(self):
        """测试回合进度信息"""
        # 开始回合
        self.round_manager.start_new_round(1)
        current_round = self.round_manager.current_round
        
        # 获取进度信息
        progress = self.round_manager.get_round_progress()
        self.assertEqual(progress["current_round"], 1)
        self.assertEqual(progress["total_rounds"], 3)  # 默认最大回合数
        self.assertEqual(progress["time_limit"], 90)  # 默认时间限制
        self.assertIsNotNone(progress["drawer"])
        self.assertIsNotNone(progress["word_hint"])
        self.assertEqual(progress["correct_guesses"], [])
    
    def test_reset(self):
        """测试重置回合管理器"""
        # 开始回合
        self.round_manager.start_new_round(1)
        self.assertIsNotNone(self.round_manager.current_round)
        
        # 添加历史记录
        self.round_manager.end_current_round()
        self.assertEqual(len(self.round_manager.round_history), 1)
        
        # 重置
        self.round_manager.reset()
        
        # 检查重置结果
        self.assertIsNone(self.round_manager.current_round)
        self.assertEqual(len(self.round_manager.round_history), 0)
        self.assertEqual(len(self.round_manager.players), 3)  # 玩家列表不应被重置


if __name__ == '__main__':
    unittest.main()