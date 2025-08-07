"""
游戏状态机单元测试
"""

import sys
import os
import unittest
from unittest.mock import Mock
import logging

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.core.game_state import (
    GameState, GameStateManager, GameStateContext,
    get_game_state_manager, transition_to_state
)
from game.core.event_bus import EventBus, GameEvent, EventType


class TestGameState(unittest.TestCase):
    """测试游戏状态枚举"""
    
    def test_game_state_values(self):
        """测试游戏状态枚举值"""
        self.assertEqual(GameState.WAITING.value, "waiting")
        self.assertEqual(GameState.DRAWING.value, "drawing")
        self.assertEqual(GameState.GUESSING.value, "guessing")
        self.assertEqual(GameState.SCORING.value, "scoring")
        self.assertEqual(GameState.GAME_OVER.value, "game_over")


class TestGameStateManager(unittest.TestCase):
    """测试游戏状态管理器"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建独立的事件总线以避免测试间干扰
        self.event_bus = EventBus()
        self.state_manager = GameStateManager(self.event_bus)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.state_manager.current_state, GameState.WAITING)
        self.assertIsNone(self.state_manager.previous_state)
        self.assertIsInstance(self.state_manager.state_context, GameStateContext)
    
    def test_state_transition_valid(self):
        """测试有效的状态转换"""
        # WAITING -> DRAWING
        result = self.state_manager.transition_to(GameState.DRAWING)
        self.assertTrue(result)
        self.assertEqual(self.state_manager.current_state, GameState.DRAWING)
        self.assertEqual(self.state_manager.previous_state, GameState.WAITING)
        
        # DRAWING -> GUESSING
        result = self.state_manager.transition_to(GameState.GUESSING)
        self.assertTrue(result)
        self.assertEqual(self.state_manager.current_state, GameState.GUESSING)
        self.assertEqual(self.state_manager.previous_state, GameState.DRAWING)
    
    def test_state_transition_invalid(self):
        """测试无效的状态转换"""
        # WAITING -> GUESSING (无效转换)
        result = self.state_manager.transition_to(GameState.GUESSING)
        self.assertFalse(result)
        self.assertEqual(self.state_manager.current_state, GameState.WAITING)
    
    def test_state_transition_to_same_state(self):
        """测试转换到相同状态"""
        # WAITING -> WAITING (允许转换到相同状态)
        result = self.state_manager.transition_to(GameState.WAITING)
        self.assertTrue(result)
        self.assertEqual(self.state_manager.current_state, GameState.WAITING)
    
    def test_state_context_update(self):
        """测试状态上下文更新"""
        # 创建新的上下文
        context = GameStateContext(
            current_round=1,
            total_rounds=3,
            current_drawer="player1",
            current_word="苹果"
        )
        
        # 转换状态并更新上下文
        self.state_manager.transition_to(GameState.DRAWING, context)
        
        # 验证上下文更新
        self.assertEqual(self.state_manager.state_context.current_round, 1)
        self.assertEqual(self.state_manager.state_context.total_rounds, 3)
        self.assertEqual(self.state_manager.state_context.current_drawer, "player1")
        self.assertEqual(self.state_manager.state_context.current_word, "苹果")
    
    def test_state_change_callbacks(self):
        """测试状态变更回调"""
        callback = Mock()
        self.state_manager.add_state_change_callback(callback)
        
        # 触发状态变更
        self.state_manager.transition_to(GameState.DRAWING)
        
        # 验证回调被调用
        callback.assert_called_once_with(GameState.WAITING, GameState.DRAWING)
        
        # 移除回调
        self.state_manager.remove_state_change_callback(callback)
        
        # 再次触发状态变更
        self.state_manager.transition_to(GameState.GUESSING)
        
        # 验证回调没有被再次调用
        callback.assert_called_once_with(GameState.WAITING, GameState.DRAWING)
    
    def test_state_queries(self):
        """测试状态查询方法"""
        # 初始状态检查
        self.assertTrue(self.state_manager.is_in_state(GameState.WAITING))
        self.assertFalse(self.state_manager.is_in_state(GameState.DRAWING))
        
        self.assertTrue(self.state_manager.is_in_any_state([GameState.WAITING, GameState.DRAWING]))
        self.assertFalse(self.state_manager.is_in_any_state([GameState.DRAWING, GameState.GUESSING]))
        
        # 转换状态后检查
        self.state_manager.transition_to(GameState.DRAWING)
        self.assertTrue(self.state_manager.is_in_state(GameState.DRAWING))
        self.assertTrue(self.state_manager.is_in_any_state([GameState.WAITING, GameState.DRAWING]))
        self.assertFalse(self.state_manager.is_game_over())
        self.assertTrue(self.state_manager.is_game_active())
    
    def test_state_history(self):
        """测试状态历史记录"""
        # 初始历史记录
        history = self.state_manager.get_state_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], GameState.WAITING)
        
        # 转换几次状态
        self.state_manager.transition_to(GameState.DRAWING)
        self.state_manager.transition_to(GameState.GUESSING)
        self.state_manager.transition_to(GameState.SCORING)
        
        # 检查完整历史记录
        history = self.state_manager.get_state_history()
        self.assertEqual(len(history), 4)
        self.assertEqual(history, [GameState.WAITING, GameState.DRAWING, GameState.GUESSING, GameState.SCORING])
        
        # 检查有限历史记录
        recent_history = self.state_manager.get_state_history(2)
        self.assertEqual(len(recent_history), 2)
        self.assertEqual(recent_history, [GameState.GUESSING, GameState.SCORING])
    
    def test_reset(self):
        """测试状态重置"""
        # 转换几次状态
        self.state_manager.transition_to(GameState.DRAWING)
        self.state_manager.transition_to(GameState.GUESSING)
        
        # 重置状态
        self.state_manager.reset()
        
        # 验证重置结果
        self.assertEqual(self.state_manager.current_state, GameState.WAITING)
        self.assertIsNone(self.state_manager.previous_state)
        history = self.state_manager.get_state_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], GameState.WAITING)
    
    def test_can_transition_to(self):
        """测试状态转换验证"""
        # 有效的转换
        self.assertTrue(self.state_manager.can_transition_to(GameState.DRAWING))
        self.assertTrue(self.state_manager.can_transition_to(GameState.WAITING))  # 同状态转换
        
        # 无效的转换
        self.assertFalse(self.state_manager.can_transition_to(GameState.GUESSING))
        self.assertFalse(self.state_manager.can_transition_to(GameState.GAME_OVER))
    
    def test_global_state_manager(self):
        """测试全局状态管理器"""
        # 获取全局状态管理器
        global_manager1 = get_game_state_manager(self.event_bus)
        global_manager2 = get_game_state_manager(self.event_bus)
        
        # 验证是同一个实例
        self.assertIs(global_manager1, global_manager2)
        
        # 测试全局状态转换函数
        result = transition_to_state(GameState.DRAWING)
        self.assertTrue(result)
        self.assertEqual(global_manager1.current_state, GameState.DRAWING)


class TestGameStateContext(unittest.TestCase):
    """测试游戏状态上下文"""
    
    def test_context_creation(self):
        """测试上下文创建"""
        context = GameStateContext()
        self.assertEqual(context.current_round, 0)
        self.assertEqual(context.total_rounds, 3)
        self.assertIsNone(context.current_drawer)
        self.assertIsNone(context.current_word)
        self.assertEqual(context.extra_data, {})
    
    def test_context_with_parameters(self):
        """测试带参数的上下文创建"""
        extra_data = {"timer": 60, "difficulty": "medium"}
        context = GameStateContext(
            current_round=2,
            total_rounds=5,
            current_drawer="player2",
            current_word="香蕉",
            extra_data=extra_data
        )
        
        self.assertEqual(context.current_round, 2)
        self.assertEqual(context.total_rounds, 5)
        self.assertEqual(context.current_drawer, "player2")
        self.assertEqual(context.current_word, "香蕉")
        self.assertEqual(context.extra_data, extra_data)


if __name__ == '__main__':
    # 配置日志以避免测试输出混乱
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()