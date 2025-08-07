"""
数据模型单元测试
"""

import sys
import os
import unittest
from datetime import datetime

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.data.models.player import Player, PlayerType
from game.data.models.word import Word, WordDifficulty, WordCategory
from game.data.models.game_data import GameData, RoundData


class TestPlayerModel(unittest.TestCase):
    """测试玩家数据模型"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.player = Player(
            player_id="player1",
            name="Alice",
            player_type=PlayerType.HUMAN
        )
    
    def test_player_creation(self):
        """测试玩家创建"""
        self.assertEqual(self.player.player_id, "player1")
        self.assertEqual(self.player.name, "Alice")
        self.assertEqual(self.player.player_type, PlayerType.HUMAN)
        self.assertEqual(self.player.score, 0)
        self.assertFalse(self.player.is_drawing)
        self.assertFalse(self.player.has_guessed)
    
    def test_player_score_management(self):
        """测试玩家分数管理"""
        # 增加分数
        self.player.add_score(10)
        self.assertEqual(self.player.score, 10)
        
        # 增加更多分数
        self.player.add_score(20)
        self.assertEqual(self.player.score, 30)
        
        # 不能增加负分数
        self.player.add_score(-10)
        self.assertEqual(self.player.score, 30)  # 分数应该保持不变
    
    def test_player_state_management(self):
        """测试玩家状态管理"""
        # 设置绘画状态
        self.player.set_drawing_state(True)
        self.assertTrue(self.player.is_drawing)
        self.assertFalse(self.player.has_guessed)  # 应该自动重置猜题状态
        
        # 设置猜题状态
        self.player.set_guessed_state(True)
        self.assertTrue(self.player.has_guessed)
        
        # 重置回合状态
        self.player.reset_round_state()
        self.assertFalse(self.player.is_drawing)
        self.assertFalse(self.player.has_guessed)
        
        # 重置游戏状态
        self.player.add_score(50)
        self.player.set_drawing_state(True)
        self.player.reset_game_state()
        self.assertEqual(self.player.score, 0)
        self.assertFalse(self.player.is_drawing)
        self.assertFalse(self.player.has_guessed)


class TestWordModel(unittest.TestCase):
    """测试词汇数据模型"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.word = Word(
            text="苹果",
            category="food",
            difficulty="easy",
            hint="一种水果",
            examples=["红苹果", "青苹果"]
        )
    
    def test_word_creation(self):
        """测试词汇创建"""
        self.assertEqual(self.word.text, "苹果")
        self.assertEqual(self.word.category, "food")
        self.assertEqual(self.word.difficulty, "easy")
        self.assertEqual(self.word.hint, "一种水果")
        self.assertEqual(self.word.examples, ["红苹果", "青苹果"])
        self.assertIsNone(self.word.word_id)
    
    def test_word_validation(self):
        """测试词汇验证"""
        # 无效词汇 - 空文本
        with self.assertRaises(ValueError):
            Word(text="", category="food", difficulty="easy", hint="提示")
        
        # 无效词汇 - 空提示
        with self.assertRaises(ValueError):
            Word(text="苹果", category="food", difficulty="easy", hint="")
        
        # 文本自动清理
        word_with_spaces = Word(
            text=" 苹果 ", 
            category="food", 
            difficulty="easy", 
            hint=" 一种水果 "
        )
        self.assertEqual(word_with_spaces.text, "苹果")
        self.assertEqual(word_with_spaces.hint, "一种水果")
    
    def test_word_difficulty_and_category_check(self):
        """测试词汇难度和类别检查"""
        self.assertTrue(self.word.is_difficulty("easy"))
        self.assertTrue(self.word.is_difficulty("EASY"))
        self.assertFalse(self.word.is_difficulty("hard"))
        
        self.assertTrue(self.word.is_category("food"))
        self.assertTrue(self.word.is_category("FOOD"))
        self.assertFalse(self.word.is_category("animal"))
    
    def test_word_examples_management(self):
        """测试词汇示例管理"""
        # 添加示例
        self.word.add_example("黄苹果")
        self.assertIn("黄苹果", self.word.examples)
        
        # 重复添加应该无效
        original_length = len(self.word.examples)
        self.word.add_example("红苹果")  # 已存在的示例
        self.assertEqual(len(self.word.examples), original_length)
        
        # 删除示例
        self.assertTrue(self.word.remove_example("红苹果"))
        self.assertNotIn("红苹果", self.word.examples)
        
        # 删除不存在的示例
        self.assertFalse(self.word.remove_example("紫苹果"))
    
    def test_word_display_text(self):
        """测试词汇显示文本"""
        display_text = self.word.get_display_text()
        self.assertEqual(display_text, "**")  # "苹果"有两个字符


class TestGameDataModel(unittest.TestCase):
    """测试游戏数据模型"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建玩家
        self.player1 = Player("player1", "Alice", PlayerType.HUMAN)
        self.player2 = Player("player2", "Bob", PlayerType.AI)
        
        # 创建词汇
        self.word = Word("苹果", "food", "easy", "一种水果")
        
        # 创建游戏数据
        self.game_data = GameData("game1")
    
    def test_game_data_creation(self):
        """测试游戏数据创建"""
        self.assertEqual(self.game_data.game_id, "game1")
        self.assertEqual(self.game_data.players, [])
        self.assertEqual(self.game_data.rounds, [])
        self.assertEqual(self.game_data.current_round_index, 0)
        self.assertIsNone(self.game_data.start_time)
        self.assertIsNone(self.game_data.end_time)
        self.assertFalse(self.game_data.is_active)
        self.assertEqual(self.game_data.config, {})
    
    def test_player_management(self):
        """测试玩家管理"""
        # 添加玩家
        self.game_data.add_player(self.player1)
        self.assertIn(self.player1, self.game_data.players)
        
        self.game_data.add_player(self.player2)
        self.assertIn(self.player2, self.game_data.players)
        self.assertEqual(len(self.game_data.players), 2)
        
        # 移除玩家
        self.assertTrue(self.game_data.remove_player(self.player1))
        self.assertNotIn(self.player1, self.game_data.players)
        self.assertEqual(len(self.game_data.players), 1)
        
        # 移除不存在的玩家
        fake_player = Player("fake", "Fake", PlayerType.HUMAN)
        self.assertFalse(self.game_data.remove_player(fake_player))
    
    def test_game_lifecycle(self):
        """测试游戏生命周期"""
        # 开始游戏
        self.game_data.start_game()
        self.assertIsNotNone(self.game_data.start_time)
        self.assertTrue(self.game_data.is_active)
        
        # 结束游戏
        self.game_data.end_game()
        self.assertIsNotNone(self.game_data.end_time)
        self.assertFalse(self.game_data.is_active)
    
    def test_round_management(self):
        """测试回合管理"""
        # 创建回合数据
        round1 = RoundData(round_number=1)
        round2 = RoundData(round_number=2)
        
        # 添加回合
        self.game_data.add_round(round1)
        self.game_data.add_round(round2)
        self.assertEqual(len(self.game_data.rounds), 2)
        
        # 获取当前回合
        self.assertEqual(self.game_data.get_current_round(), round1)
        
        # 进入下一回合
        self.assertTrue(self.game_data.next_round())
        self.assertEqual(self.game_data.get_current_round(), round2)
        
        # 尝试超出回合数
        self.assertFalse(self.game_data.next_round())
    
    def test_round_lifecycle(self):
        """测试回合生命周期"""
        round_data = RoundData(round_number=1)
        
        # 开始回合
        round_data.start_round(self.word, self.player1)
        self.assertEqual(round_data.current_word, self.word)
        self.assertEqual(round_data.drawer, self.player1)
        self.assertIsNotNone(round_data.start_time)
        self.assertFalse(round_data.is_finished)
        
        # 添加正确猜测
        round_data.add_correct_guess(self.player2)
        self.assertIn(self.player2, round_data.correct_guesses)
        
        # 结束回合
        round_data.end_round()
        self.assertIsNotNone(round_data.end_time)
        self.assertTrue(round_data.is_finished)
    
    def test_player_rankings_and_winner(self):
        """测试玩家排名和获胜者"""
        # 添加玩家并设置分数
        self.game_data.add_player(self.player1)
        self.game_data.add_player(self.player2)
        
        self.player1.add_score(30)
        self.player2.add_score(50)
        
        # 获取排名
        rankings = self.game_data.get_player_rankings()
        self.assertEqual(rankings[0], self.player2)  # Bob分数高，排名第一
        self.assertEqual(rankings[1], self.player1)  # Alice分数低，排名第二
        
        # 获取获胜者
        winner = self.game_data.get_winner()
        self.assertEqual(winner, self.player2)  # Bob是获胜者


if __name__ == '__main__':
    unittest.main()