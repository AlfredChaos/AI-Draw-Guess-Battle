"""
词汇服务测试模块

测试WordService类的核心功能。
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.services.word_service import WordService, get_word_service, reset_word_service
from game.data.models.word import Word
from game.data.repositories.word_repository import WordRepository


class TestWordService(unittest.TestCase):
    """测试WordService类"""
    
    def setUp(self):
        """测试前准备"""
        reset_word_service()  # 重置词汇服务实例
        
        # 创建模拟的词汇仓库
        self.mock_repository = Mock(spec=WordRepository)
        
        # 创建测试词汇数据
        self.test_words = [
            Word(text="苹果", category="食物", difficulty="easy", hint="一种水果"),
            Word(text="香蕉", category="食物", difficulty="easy", hint="黄色的水果"),
            Word(text="篮球", category="运动", difficulty="medium", hint="一种球类运动"),
            Word(text="画蛇添足", category="成语", difficulty="hard", hint="一个成语"),
        ]
        
        # 设置模拟仓库的返回值
        self.mock_repository.get_words_by_filters.return_value = self.test_words
        self.mock_repository.get_words_by_difficulty.return_value = [self.test_words[0], self.test_words[1]]
        self.mock_repository.get_words_by_category.return_value = [self.test_words[2]]
        self.mock_repository.search_words.return_value = [self.test_words[0]]
        
        # 创建词汇服务实例
        self.word_service = WordService(self.mock_repository)
    
    def tearDown(self):
        """测试后清理"""
        reset_word_service()
    
    def test_get_random_word(self):
        """测试获取随机词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_filters.return_value = [self.test_words[0]]
        
        # 测试获取随机词汇
        word = self.word_service.get_random_word()
        self.assertIsNotNone(word)
        self.assertEqual(word.text, "苹果")
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_filters.assert_called_with(None, None)
    
    def test_get_random_word_with_filters(self):
        """测试带筛选条件获取随机词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_filters.return_value = [self.test_words[1]]
        
        # 测试带筛选条件获取随机词汇
        word = self.word_service.get_random_word(difficulty="easy", category="食物")
        self.assertIsNotNone(word)
        self.assertEqual(word.text, "香蕉")
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_filters.assert_called_with("easy", "食物")
    
    def test_get_random_word_no_matches(self):
        """测试没有匹配词汇时的情况"""
        # 设置模拟返回值为空列表
        self.mock_repository.get_words_by_filters.return_value = []
        
        # 测试没有匹配词汇时返回None
        word = self.word_service.get_random_word(difficulty="nonexistent")
        self.assertIsNone(word)
    
    def test_get_random_words(self):
        """测试获取多个随机词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_filters.return_value = self.test_words
        
        # 测试获取多个随机词汇
        words = self.word_service.get_random_words(count=3)
        self.assertEqual(len(words), 3)
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_filters.assert_called_with(None, None)
    
    def test_get_random_words_with_filters(self):
        """测试带筛选条件获取多个随机词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_filters.return_value = [self.test_words[0], self.test_words[1]]
        
        # 测试带筛选条件获取多个随机词汇
        words = self.word_service.get_random_words(count=2, difficulty="easy")
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0].difficulty, "easy")
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_filters.assert_called_with("easy", None)
    
    def test_get_random_words_no_matches(self):
        """测试没有匹配词汇时获取多个随机词汇"""
        # 设置模拟返回值为空列表
        self.mock_repository.get_words_by_filters.return_value = []
        
        # 测试没有匹配词汇时返回空列表
        words = self.word_service.get_random_words(count=3, difficulty="nonexistent")
        self.assertEqual(len(words), 0)
    
    def test_get_word_hint(self):
        """测试获取词汇提示"""
        # 测试获取词汇提示
        hint = self.word_service.get_word_hint(self.test_words[0])
        self.assertEqual(hint, "一种水果")
    
    def test_get_words_by_difficulty(self):
        """测试根据难度获取词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_difficulty.return_value = [self.test_words[0], self.test_words[1]]
        
        # 测试根据难度获取词汇
        words = self.word_service.get_words_by_difficulty("easy")
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0].difficulty, "easy")
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_difficulty.assert_called_with("easy")
    
    def test_get_words_by_category(self):
        """测试根据类别获取词汇"""
        # 设置模拟返回值
        self.mock_repository.get_words_by_category.return_value = [self.test_words[2]]
        
        # 测试根据类别获取词汇
        words = self.word_service.get_words_by_category("运动")
        self.assertEqual(len(words), 1)
        self.assertEqual(words[0].category, "运动")
        
        # 验证仓库方法被正确调用
        self.mock_repository.get_words_by_category.assert_called_with("运动")
    
    def test_search_words(self):
        """测试搜索词汇"""
        # 设置模拟返回值
        self.mock_repository.search_words.return_value = [self.test_words[0]]
        
        # 测试搜索词汇
        words = self.word_service.search_words("苹果")
        self.assertEqual(len(words), 1)
        self.assertEqual(words[0].text, "苹果")
        
        # 验证仓库方法被正确调用
        self.mock_repository.search_words.assert_called_with("苹果")
    
    def test_get_word_service_singleton(self):
        """测试词汇服务单例模式"""
        # 重置服务
        reset_word_service()
        
        # 获取服务实例
        service1 = get_word_service()
        service2 = get_word_service()
        
        # 验证是同一个实例
        self.assertIs(service1, service2)


if __name__ == '__main__':
    unittest.main()