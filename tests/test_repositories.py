"""
数据仓库单元测试
"""

import sys
import os
import unittest
from pathlib import Path

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.data.repositories.word_repository import WordRepository
from game.data.repositories.config_repository import ConfigRepository
from game.data.models.word import Word


class TestWordRepository(unittest.TestCase):
    """测试词库管理仓库"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用测试词库文件
        self.words_file_path = os.path.join(os.path.dirname(__file__), '..', 'words.json')
        self.word_repo = WordRepository(self.words_file_path)
    
    def test_word_repository_creation(self):
        """测试词库仓库创建"""
        # 检查仓库是否成功创建
        self.assertIsNotNone(self.word_repo)
        self.assertTrue(len(self.word_repo.get_all_words()) > 0)
    
    def test_load_words(self):
        """测试加载词库"""
        # 检查词汇是否正确加载
        words = self.word_repo.get_all_words()
        self.assertTrue(len(words) > 0)
        
        # 检查第一个词汇是否正确加载
        first_word = words[0]
        self.assertIsInstance(first_word, Word)
        self.assertIsNotNone(first_word.text)
        self.assertIsNotNone(first_word.category)
        self.assertIsNotNone(first_word.difficulty)
        self.assertIsNotNone(first_word.hint)
    
    def test_get_words_by_category(self):
        """测试按类别获取词汇"""
        # 获取所有类别
        categories = self.word_repo.get_categories()
        self.assertTrue(len(categories) > 0)
        
        # 测试获取特定类别的词汇
        first_category = categories[0]
        category_words = self.word_repo.get_words_by_category(first_category)
        self.assertTrue(len(category_words) > 0)
        
        # 验证所有词汇都属于指定类别
        for word in category_words:
            self.assertTrue(word.is_category(first_category))
    
    def test_get_words_by_difficulty(self):
        """测试按难度获取词汇"""
        # 获取所有难度
        difficulties = self.word_repo.get_difficulties()
        self.assertTrue(len(difficulties) > 0)
        
        # 测试获取特定难度的词汇
        first_difficulty = difficulties[0]
        difficulty_words = self.word_repo.get_words_by_difficulty(first_difficulty)
        self.assertTrue(len(difficulty_words) > 0)
        
        # 验证所有词汇都属于指定难度
        for word in difficulty_words:
            self.assertTrue(word.is_difficulty(first_difficulty))
    
    def test_get_random_word(self):
        """测试随机获取词汇"""
        # 获取随机词汇
        random_word = self.word_repo.get_random_word()
        self.assertIsNotNone(random_word)
        self.assertIsInstance(random_word, Word)
        
        # 获取指定难度的随机词汇
        difficulties = self.word_repo.get_difficulties()
        if difficulties:
            first_difficulty = difficulties[0]
            random_word_by_difficulty = self.word_repo.get_random_word_by_difficulty(first_difficulty)
            self.assertIsNotNone(random_word_by_difficulty)
            self.assertTrue(random_word_by_difficulty.is_difficulty(first_difficulty))
    
    def test_search_words(self):
        """测试搜索词汇"""
        # 获取一个已知词汇进行搜索测试
        all_words = self.word_repo.get_all_words()
        if all_words:
            first_word = all_words[0]
            search_results = self.word_repo.search_words(first_word.text)
            self.assertTrue(len(search_results) > 0)
            
            # 验证搜索结果中包含目标词汇
            found = False
            for word in search_results:
                if word.text == first_word.text:
                    found = True
                    break
            self.assertTrue(found)
    
    def test_word_counts(self):
        """测试词汇计数功能"""
        # 测试总词汇数
        total_count = self.word_repo.get_word_count()
        self.assertTrue(total_count > 0)
        self.assertEqual(total_count, len(self.word_repo.get_all_words()))
        
        # 测试按类别计数
        categories = self.word_repo.get_categories()
        if categories:
            first_category = categories[0]
            category_count = self.word_repo.get_word_count_by_category(first_category)
            category_words = self.word_repo.get_words_by_category(first_category)
            self.assertEqual(category_count, len(category_words))
        
        # 测试按难度计数
        difficulties = self.word_repo.get_difficulties()
        if difficulties:
            first_difficulty = difficulties[0]
            difficulty_count = self.word_repo.get_word_count_by_difficulty(first_difficulty)
            difficulty_words = self.word_repo.get_words_by_difficulty(first_difficulty)
            self.assertEqual(difficulty_count, len(difficulty_words))


class TestConfigRepository(unittest.TestCase):
    """测试配置管理仓库"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用测试配置目录
        self.config_dir_path = os.path.join(os.path.dirname(__file__), '..', 'game', 'config')
        self.config_repo = ConfigRepository(self.config_dir_path)
    
    def test_config_repository_creation(self):
        """测试配置仓库创建"""
        # 检查仓库是否成功创建
        self.assertIsNotNone(self.config_repo)
    
    def test_load_configs(self):
        """测试加载配置"""
        # 检查配置是否正确加载
        game_config = self.config_repo.get_game_config()
        ui_config = self.config_repo.get_ui_config()
        ai_config = self.config_repo.get_ai_config()
        
        # 验证至少有一个配置非空
        self.assertTrue(
            len(game_config) > 0 or len(ui_config) > 0 or len(ai_config) > 0,
            "至少应加载一个配置文件"
        )
    
    def test_get_config(self):
        """测试获取配置"""
        # 测试获取游戏配置
        game_config = self.config_repo.get_config('game')
        self.assertIsInstance(game_config, dict)
        
        # 测试获取UI配置
        ui_config = self.config_repo.get_config('ui')
        self.assertIsInstance(ui_config, dict)
        
        # 测试获取AI配置
        ai_config = self.config_repo.get_config('ai')
        self.assertIsInstance(ai_config, dict)
        
        # 测试无效配置类型
        with self.assertRaises(ValueError):
            self.config_repo.get_config('invalid')
    
    def test_config_updates(self):
        """测试配置更新"""
        # 更新游戏配置
        self.config_repo.update_game_config('test_key', 'test_value')
        self.assertEqual(self.config_repo.get_game_config('test_key'), 'test_value')
        
        # 更新UI配置
        self.config_repo.update_ui_config('test_key', 'ui_test_value')
        self.assertEqual(self.config_repo.get_ui_config('test_key'), 'ui_test_value')
        
        # 更新AI配置
        self.config_repo.update_ai_config('test_key', 'ai_test_value')
        self.assertEqual(self.config_repo.get_ai_config('test_key'), 'ai_test_value')


if __name__ == '__main__':
    unittest.main()