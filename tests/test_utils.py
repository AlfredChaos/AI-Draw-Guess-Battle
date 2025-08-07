"""
工具函数库单元测试
"""

import sys
import os
import unittest

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.utils.constants import *
from game.utils.helpers import *
from game.utils.validators import *


class TestConstants(unittest.TestCase):
    """测试常量定义"""
    
    def test_screen_constants(self):
        """测试屏幕常量"""
        self.assertEqual(SCREEN_WIDTH, 1280)
        self.assertEqual(SCREEN_HEIGHT, 720)
        self.assertEqual(FPS, 60)
    
    def test_color_constants(self):
        """测试颜色常量"""
        self.assertEqual(WHITE, (255, 255, 255))
        self.assertEqual(BLACK, (0, 0, 0))
        self.assertEqual(PLAYER_COLORS["human"], (0, 150, 255))
        self.assertEqual(PLAYER_COLORS["ai"], (255, 100, 0))
    
    def test_game_constants(self):
        """测试游戏常量"""
        self.assertEqual(MAX_ROUNDS, 3)
        self.assertEqual(DRAWING_TIME_LIMIT, 90)
        self.assertEqual(TOOL_PEN, "pen")
        self.assertEqual(TOOL_ERASER, "eraser")


class TestHelpers(unittest.TestCase):
    """测试辅助函数"""
    
    def test_clamp(self):
        """测试clamp函数"""
        self.assertEqual(clamp(5, 1, 10), 5)
        self.assertEqual(clamp(0, 1, 10), 1)
        self.assertEqual(clamp(15, 1, 10), 10)
        self.assertEqual(clamp(1.5, 1.0, 2.0), 1.5)
    
    def test_format_time(self):
        """测试时间格式化函数"""
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(60), "01:00")
        self.assertEqual(format_time(90), "01:30")
        self.assertEqual(format_time(3600), "60:00")
    
    def test_calculate_distance(self):
        """测试距离计算函数"""
        self.assertEqual(calculate_distance(0, 0, 3, 4), 5)
        self.assertEqual(calculate_distance(1, 1, 1, 1), 0)
        self.assertAlmostEqual(calculate_distance(0, 0, 1, 1), 1.414, places=3)
    
    def test_is_point_in_rect(self):
        """测试点在矩形内检查函数"""
        # 点在矩形内
        self.assertTrue(is_point_in_rect(5, 5, 0, 0, 10, 10))
        # 点在矩形边界上
        self.assertTrue(is_point_in_rect(0, 0, 0, 0, 10, 10))
        self.assertTrue(is_point_in_rect(10, 10, 0, 0, 10, 10))
        # 点在矩形外
        self.assertFalse(is_point_in_rect(-1, -1, 0, 0, 10, 10))
        self.assertFalse(is_point_in_rect(11, 11, 0, 0, 10, 10))
    
    def test_lerp(self):
        """测试线性插值函数"""
        self.assertEqual(lerp(0, 10, 0), 0)
        self.assertEqual(lerp(0, 10, 1), 10)
        self.assertEqual(lerp(0, 10, 0.5), 5)
        self.assertEqual(lerp(-5, 5, 0.5), 0)


class TestValidators(unittest.TestCase):
    """测试验证器函数"""
    
    def test_validate_player_name(self):
        """测试玩家名称验证"""
        # 有效名称
        self.assertTrue(validate_player_name("Alice"))
        self.assertTrue(validate_player_name("Bob123"))
        self.assertTrue(validate_player_name("玩家一"))
        self.assertTrue(validate_player_name("Test_User"))
        
        # 无效名称
        self.assertFalse(validate_player_name(""))  # 空字符串
        self.assertFalse(validate_player_name("A"))  # 太短
        self.assertFalse(validate_player_name("A" * 21))  # 太长
        self.assertFalse(validate_player_name("Invalid@Name"))  # 包含特殊字符
    
    def test_validate_word_entry(self):
        """测试词汇条目验证"""
        # 有效词汇条目
        valid_word = {
            "word": "苹果",
            "category": "水果",
            "difficulty": "easy",
            "hint": "一种水果"
        }
        self.assertTrue(validate_word_entry(valid_word))
        
        # 包含示例的词汇条目
        valid_word_with_examples = {
            "word": "苹果",
            "category": "水果",
            "difficulty": "easy",
            "hint": "一种水果",
            "examples": ["红苹果", "青苹果"]
        }
        self.assertTrue(validate_word_entry(valid_word_with_examples))
        
        # 无效词汇条目 - 缺少必需字段
        invalid_word = {
            "word": "苹果",
            "category": "水果"
            # 缺少 difficulty 和 hint
        }
        self.assertFalse(validate_word_entry(invalid_word))
        
        # 无效词汇条目 - 无效难度
        invalid_word2 = {
            "word": "苹果",
            "category": "水果",
            "difficulty": "invalid",
            "hint": "一种水果"
        }
        self.assertFalse(validate_word_entry(invalid_word2))
    
    def test_validate_positive_integer(self):
        """测试正整数验证"""
        self.assertTrue(validate_positive_integer(1))
        self.assertTrue(validate_positive_integer(100))
        self.assertFalse(validate_positive_integer(0))
        self.assertFalse(validate_positive_integer(-1))
        self.assertFalse(validate_positive_integer(1.5))
        self.assertFalse(validate_positive_integer("1"))
    
    def test_validate_color(self):
        """测试颜色验证"""
        self.assertTrue(validate_color((255, 0, 0)))
        self.assertTrue(validate_color([0, 255, 0]))
        self.assertFalse(validate_color((256, 0, 0)))  # 超出范围
        self.assertFalse(validate_color((-1, 0, 0)))  # 负数
        self.assertFalse(validate_color((255, 0)))  # 长度不正确
        self.assertFalse(validate_color("red"))  # 类型不正确
    
    def test_validate_game_state(self):
        """测试游戏状态验证"""
        self.assertTrue(validate_game_state(GAME_STATE_WAITING))
        self.assertTrue(validate_game_state(GAME_STATE_DRAWING))
        self.assertFalse(validate_game_state("invalid_state"))


if __name__ == '__main__':
    unittest.main()