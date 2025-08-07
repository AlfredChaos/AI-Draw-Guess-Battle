"""
词汇服务模块

实现词汇选择逻辑，支持难度分级和随机选择，以及词汇提示功能。
"""

import random
import logging
from typing import List, Optional, Dict, Any

from ..data.models.word import Word, WordDifficulty, WordCategory
from ..data.repositories.word_repository import WordRepository


class WordService:
    """词汇服务"""
    
    def __init__(self, word_repository: Optional[WordRepository] = None):
        """
        初始化词汇服务
        
        Args:
            word_repository: 词汇仓库实例，如果为None则创建默认实例
        """
        self.logger = logging.getLogger(__name__)
        self.word_repository = word_repository or WordRepository()
    
    def get_random_word(self, 
                       difficulty: Optional[str] = None, 
                       category: Optional[str] = None) -> Optional[Word]:
        """
        获取随机词汇
        
        Args:
            difficulty: 词汇难度（可选）
            category: 词汇类别（可选）
            
        Returns:
            Word: 随机选择的词汇，如果没有符合条件的词汇则返回None
        """
        # 获取符合条件的词汇列表
        words = self.word_repository.get_words_by_filters(difficulty, category)
        
        if not words:
            self.logger.warning(f"No words found with difficulty={difficulty}, category={category}")
            return None
        
        # 随机选择一个词汇
        selected_word = random.choice(words)
        self.logger.info(f"Selected random word: {selected_word.text}")
        return selected_word
    
    def get_random_words(self, 
                        count: int = 3, 
                        difficulty: Optional[str] = None, 
                        category: Optional[str] = None) -> List[Word]:
        """
        获取多个随机词汇
        
        Args:
            count: 需要获取的词汇数量
            difficulty: 词汇难度（可选）
            category: 词汇类别（可选）
            
        Returns:
            List[Word]: 随机选择的词汇列表
        """
        # 获取符合条件的词汇列表
        words = self.word_repository.get_words_by_filters(difficulty, category)
        
        if not words:
            self.logger.warning(f"No words found with difficulty={difficulty}, category={category}")
            return []
        
        # 如果请求数量大于可用数量，则调整为可用数量
        actual_count = min(count, len(words))
        
        # 随机选择指定数量的词汇
        selected_words = random.sample(words, actual_count)
        self.logger.info(f"Selected {actual_count} random words: {[w.text for w in selected_words]}")
        return selected_words
    
    def get_word_hint(self, word: Word) -> str:
        """
        获取词汇提示
        
        Args:
            word: 词汇对象
            
        Returns:
            str: 词汇提示信息
        """
        return word.hint
    
    def get_words_by_difficulty(self, difficulty: str) -> List[Word]:
        """
        根据难度获取词汇列表
        
        Args:
            difficulty: 词汇难度
            
        Returns:
            List[Word]: 指定难度的词汇列表
        """
        return self.word_repository.get_words_by_difficulty(difficulty)
    
    def get_words_by_category(self, category: str) -> List[Word]:
        """
        根据类别获取词汇列表
        
        Args:
            category: 词汇类别
            
        Returns:
            List[Word]: 指定类别的词汇列表
        """
        return self.word_repository.get_words_by_category(category)
    
    def search_words(self, keyword: str) -> List[Word]:
        """
        搜索包含关键词的词汇
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[Word]: 包含关键词的词汇列表
        """
        return self.word_repository.search_words(keyword)


# 全局词汇服务实例
_word_service: Optional[WordService] = None


def get_word_service(word_repository: Optional[WordRepository] = None) -> WordService:
    """
    获取全局词汇服务实例
    
    Args:
        word_repository: 词汇仓库实例，如果为None则创建默认实例
        
    Returns:
        WordService: 全局词汇服务实例
    """
    global _word_service
    if _word_service is None:
        _word_service = WordService(word_repository)
    return _word_service


def reset_word_service() -> None:
    """重置全局词汇服务实例"""
    global _word_service
    _word_service = None