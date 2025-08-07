"""
数据验证器模块

提供游戏中各种数据的验证函数，确保数据的有效性和安全性。
"""

import re
from typing import Any, Optional, Union
from .constants import WORD_DIFFICULTY_EASY, WORD_DIFFICULTY_MEDIUM, WORD_DIFFICULTY_HARD


def validate_player_name(name: str) -> bool:
    """
    验证玩家名称的有效性
    
    Args:
        name: 玩家名称
    
    Returns:
        如果名称有效返回True，否则返回False
    """
    if not isinstance(name, str):
        return False
    
    # 去除首尾空格
    name = name.strip()
    
    # 检查长度（2-20个字符）
    if not (2 <= len(name) <= 20):
        return False
    
    # 检查是否只包含字母、数字、中文字符、下划线和空格
    if not re.match(r'^[\w\u4e00-\u9fff ]+$', name):
        return False
    
    return True


def validate_word_entry(word_data: dict) -> bool:
    """
    验证词汇条目的有效性
    
    Args:
        word_data: 词汇数据字典
    
    Returns:
        如果词汇条目有效返回True，否则返回False
    """
    if not isinstance(word_data, dict):
        return False
    
    # 检查必需字段
    required_fields = ['word', 'category', 'difficulty', 'hint']
    for field in required_fields:
        if field not in word_data:
            return False
    
    # 验证词汇
    if not isinstance(word_data['word'], str) or not word_data['word'].strip():
        return False
    
    # 验证类别
    if not isinstance(word_data['category'], str) or not word_data['category'].strip():
        return False
    
    # 验证难度
    valid_difficulties = [WORD_DIFFICULTY_EASY, WORD_DIFFICULTY_MEDIUM, WORD_DIFFICULTY_HARD]
    if word_data['difficulty'] not in valid_difficulties:
        return False
    
    # 验证提示
    if not isinstance(word_data['hint'], str) or not word_data['hint'].strip():
        return False
    
    # 验证示例（如果存在）
    if 'examples' in word_data:
        if not isinstance(word_data['examples'], list):
            return False
        for example in word_data['examples']:
            if not isinstance(example, str) or not example.strip():
                return False
    
    return True


def validate_positive_integer(value: Any) -> bool:
    """
    验证值是否为正整数
    
    Args:
        value: 要验证的值
    
    Returns:
        如果是正整数返回True，否则返回False
    """
    if not isinstance(value, int):
        return False
    return value > 0


def validate_non_negative_integer(value: Any) -> bool:
    """
    验证值是否为非负整数
    
    Args:
        value: 要验证的值
    
    Returns:
        如果是非负整数返回True，否则返回False
    """
    if not isinstance(value, int):
        return False
    return value >= 0


def validate_float_range(value: Any, min_val: float, max_val: float) -> bool:
    """
    验证浮点数是否在指定范围内
    
    Args:
        value: 要验证的值
        min_val: 最小值（包含）
        max_val: 最大值（包含）
    
    Returns:
        如果在范围内返回True，否则返回False
    """
    if not isinstance(value, (int, float)):
        return False
    return min_val <= value <= max_val


def validate_color(color: Any) -> bool:
    """
    验证颜色值是否有效 (R, G, B) 格式
    
    Args:
        color: 颜色值
    
    Returns:
        如果颜色值有效返回True，否则返回False
    """
    if not isinstance(color, (tuple, list)):
        return False
    
    if len(color) != 3:
        return False
    
    for component in color:
        if not isinstance(component, int) or not (0 <= component <= 255):
            return False
    
    return True


def validate_game_state(state: str) -> bool:
    """
    验证游戏状态值是否有效
    
    Args:
        state: 游戏状态字符串
    
    Returns:
        如果状态值有效返回True，否则返回False
    """
    from .constants import (
        GAME_STATE_WAITING, GAME_STATE_DRAWING, 
        GAME_STATE_GUESSING, GAME_STATE_SCORING, GAME_STATE_GAME_OVER
    )
    
    valid_states = [
        GAME_STATE_WAITING, GAME_STATE_DRAWING, 
        GAME_STATE_GUESSING, GAME_STATE_SCORING, GAME_STATE_GAME_OVER
    ]
    
    return state in valid_states


def validate_drawing_coordinates(x: Any, y: Any, width: int, height: int) -> bool:
    """
    验证绘图坐标是否有效
    
    Args:
        x, y: 坐标值
        width, height: 绘图区域的宽高
    
    Returns:
        如果坐标有效返回True，否则返回False
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return False
    
    if not isinstance(width, int) or not isinstance(height, int):
        return False
    
    if width <= 0 or height <= 0:
        return False
    
    return 0 <= x <= width and 0 <= y <= height