"""
通用辅助函数模块

提供游戏中常用的辅助函数，如随机选择、字符串处理、数学计算等。
"""

import random
from typing import List, Any, Optional, Dict, Union
from pathlib import Path
import json


def clamp(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """
    将值限制在指定范围内
    
    Args:
        value: 要限制的值
        min_value: 最小值
        max_value: 最大值
    
    Returns:
        限制在范围内的值
    """
    return max(min_value, min(value, max_value))


def random_choice_excluding(choices: List[Any], excluding: Any) -> Any:
    """
    从选项列表中随机选择一个元素，排除指定的元素
    
    Args:
        choices: 可选择的选项列表
        excluding: 要排除的元素
    
    Returns:
        随机选择的元素（不包括被排除的元素）
    """
    available_choices = [choice for choice in choices if choice != excluding]
    if not available_choices:
        return excluding  # 如果没有其他选择，则返回被排除的元素
    return random.choice(available_choices)


def weighted_random_choice(choices: List[Any], weights: List[float]) -> Any:
    """
    根据权重进行随机选择
    
    Args:
        choices: 选项列表
        weights: 对应的权重列表
    
    Returns:
        根据权重随机选择的元素
    """
    return random.choices(choices, weights=weights, k=1)[0]


def format_time(seconds: int) -> str:
    """
    格式化时间为 MM:SS 格式
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化后的时间字符串
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    计算两点之间的欧几里得距离
    
    Args:
        x1, y1: 第一个点的坐标
        x2, y2: 第二个点的坐标
    
    Returns:
        两点之间的距离
    """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def load_json_file(file_path: str) -> Optional[Dict]:
    """
    安全地加载JSON文件
    
    Args:
        file_path: JSON文件路径
    
    Returns:
        解析后的JSON数据，如果出错则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None


def is_point_in_rect(x: float, y: float, rect_x: float, rect_y: float, rect_width: float, rect_height: float) -> bool:
    """
    检查点是否在矩形区域内
    
    Args:
        x, y: 点的坐标
        rect_x, rect_y: 矩形左上角坐标
        rect_width, rect_height: 矩形的宽高
    
    Returns:
        如果点在矩形内返回True，否则返回False
    """
    return rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径
    
    Returns:
        资源文件的绝对路径
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    return str(root_dir / relative_path)


def lerp(start: float, end: float, t: float) -> float:
    """
    线性插值函数
    
    Args:
        start: 起始值
        end: 结束值
        t: 插值因子 (0.0 到 1.0)
    
    Returns:
        插值结果
    """
    return start + (end - start) * t