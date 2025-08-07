"""
主游戏引擎测试模块

测试GameEngine类的核心功能。
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.core.game_engine import GameEngine, get_game_engine, reset_game_engine
from game.core.game_state import GameState, get_game_state_manager
from game.data.models.player import Player, PlayerType


class TestGameEngine(unittest.TestCase):
    """测试GameEngine类"""
    
    def setUp(self):
        """测试前准备"""
        reset_game_engine()  # 重置游戏引擎实例
        self.game_engine = get_game_engine()
        
        # 创建测试玩家
        self.player1 = Player(player_id="1", name="Player 1", player_type=PlayerType.HUMAN)
        self.player2 = Player(player_id="2", name="Player 2", player_type=PlayerType.HUMAN)
    
    def tearDown(self):
        """测试后清理"""
        reset_game_engine()
    
    def test_initialization(self):
        """测试初始化"""
        # 检查核心组件是否正确初始化
        self.assertIsNotNone(self.game_engine.event_bus)
        self.assertIsNotNone(self.game_engine.state_manager)
        self.assertIsNotNone(self.game_engine.round_manager)
        self.assertIsNotNone(self.game_engine.scoring_system)
        self.assertIsNotNone(self.game_engine.word_repository)
        
        # 检查初始状态
        self.assertFalse(self.game_engine.is_running)
        self.assertIsNotNone(self.game_engine.game_data)
    
    def test_add_player(self):
        """测试添加玩家"""
        # 添加第一个玩家
        self.game_engine.add_player(self.player1)
        self.assertEqual(len(self.game_engine.game_data.players), 1)
        self.assertEqual(self.game_engine.game_data.players[0].name, "Player 1")
        
        # 添加第二个玩家
        self.game_engine.add_player(self.player2)
        self.assertEqual(len(self.game_engine.game_data.players), 2)
        self.assertEqual(self.game_engine.game_data.players[1].name, "Player 2")
    
    def test_remove_player(self):
        """测试移除玩家"""
        # 先添加玩家
        self.game_engine.add_player(self.player1)
        self.game_engine.add_player(self.player2)
        
        # 移除第一个玩家
        result = self.game_engine.remove_player("1")
        self.assertTrue(result)
        self.assertEqual(len(self.game_engine.game_data.players), 1)
        self.assertEqual(self.game_engine.game_data.players[0].player_id, "2")
        
        # 尝试移除不存在的玩家
        result = self.game_engine.remove_player("999")
        self.assertFalse(result)
    
    def test_start_game_success(self):
        """测试成功启动游戏"""
        # 添加玩家
        self.game_engine.add_player(self.player1)
        self.game_engine.add_player(self.player2)
        
        # 启动游戏
        result = self.game_engine.start_game()
        self.assertTrue(result)
        self.assertTrue(self.game_engine.is_running)
        
        # 检查游戏状态
        current_state = get_game_state_manager().current_state
        self.assertEqual(current_state, GameState.WAITING)
    
    def test_start_game_failure_no_players(self):
        """测试没有玩家时启动游戏失败"""
        result = self.game_engine.start_game()
        self.assertFalse(result)
        self.assertFalse(self.game_engine.is_running)
    
    def test_end_game(self):
        """测试结束游戏"""
        # 先启动游戏
        self.game_engine.add_player(self.player1)
        self.game_engine.start_game()
        self.assertTrue(self.game_engine.is_running)
        
        # 结束游戏
        self.game_engine.end_game()
        self.assertFalse(self.game_engine.is_running)
    
    def test_get_game_data(self):
        """测试获取游戏数据"""
        # 添加玩家
        self.game_engine.add_player(self.player1)
        
        # 获取游戏数据
        game_data = self.game_engine.get_game_data()
        self.assertEqual(len(game_data.players), 1)
        self.assertEqual(game_data.players[0].name, "Player 1")
    
    def test_is_game_running(self):
        """测试检查游戏运行状态"""
        # 初始状态
        self.assertFalse(self.game_engine.is_game_running())
        
        # 启动游戏后
        self.game_engine.add_player(self.player1)
        self.game_engine.start_game()
        self.assertTrue(self.game_engine.is_game_running())
        
        # 结束游戏后
        self.game_engine.end_game()
        self.assertFalse(self.game_engine.is_game_running())


if __name__ == '__main__':
    unittest.main()