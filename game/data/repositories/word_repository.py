"""
词库管理仓库模块

负责加载、管理和访问游戏词库数据。
从words.json文件中加载词汇，并提供按难度、类别等筛选功能。
"""

import json
import random
from typing import List, Dict, Optional
from pathlib import Path

from ...utils.helpers import load_json_file
from ..models.word import Word


class WordRepository:
    """词库管理仓库"""
    
    def __init__(self, words_file_path: Optional[str] = None):
        """
        初始化词库仓库
        
        Args:
            words_file_path: 词库文件路径，默认为项目根目录下的words.json
        """
        if words_file_path is None:
            # 默认使用项目根目录下的words.json文件
            self.words_file_path = Path(__file__).parent.parent.parent.parent / "words.json"
        else:
            self.words_file_path = Path(words_file_path)
        
        self.words: List[Word] = []
        self.words_by_category: Dict[str, List[Word]] = {}
        self.words_by_difficulty: Dict[str, List[Word]] = {}
        self._load_words()
    
    def _load_words(self) -> None:
        """从JSON文件加载词库数据"""
        data = load_json_file(str(self.words_file_path))
        
        if data is None:
            raise FileNotFoundError(f"无法加载词库文件: {self.words_file_path}")
        
        if not isinstance(data, dict) or "categories" not in data:
            raise ValueError("词库文件格式错误，应该包含categories字段")
        
        # 清空现有数据
        self.words = []
        self.words_by_category = {}
        self.words_by_difficulty = {}
        
        # 解析词汇数据
        for category_data in data["categories"]:
            category_name = category_data["name"]
            
            for word_item in category_data["words"]:
                try:
                    # 根据字符数确定难度
                    word_text = word_item["name"]
                    char_count = word_item["count"]
                    
                    # 确定难度级别
                    if char_count <= 2:
                        difficulty = "easy"
                    elif char_count <= 3:
                        difficulty = "medium"
                    else:
                        difficulty = "hard"
                    
                    # 创建词汇对象
                    word = Word(
                        text=word_text,
                        category=category_name,
                        difficulty=difficulty,
                        hint=f"一种{category_name}" if category_name in ["动物", "食物"] 
                             else f"一个{category_name}" if category_name in ["人物"] 
                             else f"一项{category_name}" if category_name in ["运动"] 
                             else category_name,
                        examples=[],  # words.json中没有提供示例
                        word_id=None
                    )
                    
                    self.words.append(word)
                    
                    # 按类别分类
                    category = word.category.lower()
                    if category not in self.words_by_category:
                        self.words_by_category[category] = []
                    self.words_by_category[category].append(word)
                    
                    # 按难度分类
                    difficulty = word.difficulty.lower()
                    if difficulty not in self.words_by_difficulty:
                        self.words_by_difficulty[difficulty] = []
                    self.words_by_difficulty[difficulty].append(word)
                
                except (KeyError, ValueError) as e:
                    # 跳过无效的词汇数据
                    print(f"警告: 词库中存在无效数据: {word_item}, 错误: {e}")
                    continue
    
    def get_all_words(self) -> List[Word]:
        """
        获取所有词汇
        
        Returns:
            所有词汇的列表
        """
        return self.words.copy()
    
    def get_words_by_category(self, category: str) -> List[Word]:
        """
        根据类别获取词汇
        
        Args:
            category: 词汇类别
            
        Returns:
            指定类别的词汇列表
        """
        return self.words_by_category.get(category.lower(), []).copy()
    
    def get_words_by_difficulty(self, difficulty: str) -> List[Word]:
        """
        根据难度获取词汇
        
        Args:
            difficulty: 词汇难度
            
        Returns:
            指定难度的词汇列表
        """
        return self.words_by_difficulty.get(difficulty.lower(), []).copy()
    
    def get_words_by_category_and_difficulty(self, category: str, difficulty: str) -> List[Word]:
        """
        根据类别和难度获取词汇
        
        Args:
            category: 词汇类别
            difficulty: 词汇难度
            
        Returns:
            指定类别和难度的词汇列表
        """
        category_words = self.get_words_by_category(category)
        return [word for word in category_words if word.is_difficulty(difficulty)]
    
    def get_random_word(self, exclude_word: Optional[Word] = None) -> Optional[Word]:
        """
        随机获取一个词汇
        
        Args:
            exclude_word: 要排除的词汇
            
        Returns:
            随机选择的词汇，如果没有可用词汇则返回None
        """
        if not self.words:
            return None
        
        available_words = self.words
        if exclude_word:
            available_words = [word for word in self.words if word.text != exclude_word.text]
        
        if not available_words:
            return None
            
        return random.choice(available_words)
    
    def get_random_word_by_difficulty(self, difficulty: str, exclude_word: Optional[Word] = None) -> Optional[Word]:
        """
        根据难度随机获取一个词汇
        
        Args:
            difficulty: 词汇难度
            exclude_word: 要排除的词汇
            
        Returns:
            指定难度下随机选择的词汇，如果没有可用词汇则返回None
        """
        words = self.get_words_by_difficulty(difficulty)
        
        if not words:
            return None
        
        if exclude_word:
            words = [word for word in words if word.text != exclude_word.text]
        
        if not words:
            return None
            
        return random.choice(words)
    
    def get_random_words(self, count: int, difficulty: Optional[str] = None) -> List[Word]:
        """
        随机获取多个词汇
        
        Args:
            count: 需要获取的词汇数量
            difficulty: 词汇难度（可选）
            
        Returns:
            随机选择的词汇列表
        """
        if difficulty:
            words = self.get_words_by_difficulty(difficulty)
        else:
            words = self.words.copy()
        
        if not words:
            return []
        
        # 如果请求数量大于可用数量，则返回所有词汇
        if count >= len(words):
            return words
        
        return random.sample(words, count)
    
    def get_categories(self) -> List[str]:
        """
        获取所有词汇类别
        
        Returns:
            所有词汇类别的列表
        """
        return list(self.words_by_category.keys())
    
    def get_difficulties(self) -> List[str]:
        """
        获取所有词汇难度
        
        Returns:
            所有词汇难度的列表
        """
        return list(self.words_by_difficulty.keys())
    
    def search_words(self, keyword: str) -> List[Word]:
        """
        根据关键词搜索词汇
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的词汇列表
        """
        keyword = keyword.lower()
        return [word for word in self.words if keyword in word.text.lower() or keyword in word.hint.lower()]
    
    def get_word_count(self) -> int:
        """
        获取词汇总数
        
        Returns:
            词汇总数
        """
        return len(self.words)
    
    def get_word_count_by_difficulty(self, difficulty: str) -> int:
        """
        获取指定难度的词汇数量
        
        Args:
            difficulty: 词汇难度
            
        Returns:
            指定难度的词汇数量
        """
        return len(self.words_by_difficulty.get(difficulty.lower(), []))
    
    def get_word_count_by_category(self, category: str) -> int:
        """
        获取指定类别的词汇数量
        
        Args:
            category: 词汇类别
            
        Returns:
            指定类别的词汇数量
        """
        return len(self.words_by_category.get(category.lower(), []))