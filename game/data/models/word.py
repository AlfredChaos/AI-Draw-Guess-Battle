"""
词汇数据模型模块

定义词汇相关的数据结构和操作方法。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class WordDifficulty(Enum):
    """词汇难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class WordCategory(Enum):
    """词汇类别枚举"""
    ANIMAL = "animal"
    FOOD = "food"
    ACTION = "action"
    PROFESSION = "profession"
    IDIOM = "idiom"
    CONCEPT = "concept"
    MOVIE = "movie"
    OTHER = "other"


@dataclass
class Word:
    """词汇数据模型"""
    
    # 词汇文本
    text: str
    
    # 词汇类别
    category: str  # 使用字符串以便支持扩展类别
    
    # 词汇难度
    difficulty: str  # 使用字符串以便支持扩展难度
    
    # 词汇提示
    hint: str
    
    # 词汇示例列表（可选）
    examples: List[str] = field(default_factory=list)
    
    # 词汇ID（可选）
    word_id: Optional[str] = None
    
    def __post_init__(self):
        """数据初始化后验证"""
        # 确保文本和提示不为空
        if not self.text or not self.text.strip():
            raise ValueError("词汇文本不能为空")
        
        if not self.hint or not self.hint.strip():
            raise ValueError("词汇提示不能为空")
        
        # 清理文本
        self.text = self.text.strip()
        self.hint = self.hint.strip()
        
        # 清理示例列表
        self.examples = [example.strip() for example in self.examples if example.strip()]
    
    def is_difficulty(self, difficulty: str) -> bool:
        """检查词汇是否为指定难度"""
        return self.difficulty.lower() == difficulty.lower()
    
    def is_category(self, category: str) -> bool:
        """检查词汇是否为指定类别"""
        return self.category.lower() == category.lower()
    
    def add_example(self, example: str) -> None:
        """添加词汇示例"""
        example = example.strip()
        if example and example not in self.examples:
            self.examples.append(example)
    
    def remove_example(self, example: str) -> bool:
        """删除词汇示例"""
        example = example.strip()
        if example in self.examples:
            self.examples.remove(example)
            return True
        return False
    
    def get_display_text(self) -> str:
        """获取显示文本（带星号隐藏）"""
        return "*" * len(self.text)