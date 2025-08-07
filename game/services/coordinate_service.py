"""
坐标转换服务模块

提供pygame坐标系与OpenGL坐标系之间的转换功能。
处理两种坐标系的差异：
- Pygame: 原点在左上角，Y轴向下为正
- OpenGL: 原点在中心，Y轴向上为正
"""

from typing import Tuple


def pygame_to_opengl(x: float, y: float, screen_width: int, screen_height: int) -> Tuple[float, float]:
    """
    将Pygame坐标转换为OpenGL坐标
    
    Args:
        x: Pygame中的x坐标（从左到右增加）
        y: Pygame中的y坐标（从上到下增加）
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    
    Returns:
        Tuple[float, float]: 对应的OpenGL坐标(x, y)
    """
    # 将Pygame坐标转换为标准化设备坐标(NDC)
    # OpenGL的X轴范围: [-1, 1]，左到右
    opengl_x = (x / screen_width) * 2 - 1
    
    # OpenGL的Y轴范围: [-1, 1]，下到上（需要翻转）
    opengl_y = 1 - (y / screen_height) * 2
    
    return opengl_x, opengl_y


def opengl_to_pygame(x: float, y: float, screen_width: int, screen_height: int) -> Tuple[float, float]:
    """
    将OpenGL坐标转换为Pygame坐标
    
    Args:
        x: OpenGL中的x坐标（范围[-1, 1]）
        y: OpenGL中的y坐标（范围[-1, 1]）
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    
    Returns:
        Tuple[float, float]: 对应的Pygame坐标(x, y)
    """
    # 将OpenGL坐标转换为Pygame坐标
    pygame_x = ((x + 1) / 2) * screen_width
    pygame_y = ((1 - y) / 2) * screen_height
    
    return pygame_x, pygame_y


def texture_coordinates_to_vertices(
    x: float, 
    y: float, 
    width: int, 
    height: int, 
    screen_width: int, 
    screen_height: int
) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    """
    计算纹理在屏幕上的顶点坐标（用于OpenGL绘制）
    
    Args:
        x: 纹理在屏幕上的x坐标（Pygame坐标系）
        y: 纹理在屏幕上的y坐标（Pygame坐标系）
        width: 纹理宽度
        height: 纹理高度
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    
    Returns:
        四个顶点的坐标：左下、右下、右上、左上（OpenGL坐标系）
    """
    # 计算纹理在屏幕上的比例
    x_ratio = width / screen_width
    y_ratio = height / screen_height
    
    # 计算偏移量（转换为OpenGL坐标系）
    x_offset = (x / screen_width) * 2 - 1
    y_offset = 1 - (y / screen_height) * 2
    
    # 计算四个顶点坐标（逆时针顺序）
    # 左下角
    vertex1 = (x_offset, y_offset - y_ratio * 2)
    # 右下角
    vertex2 = (x_offset + x_ratio * 2, y_offset - y_ratio * 2)
    # 右上角
    vertex3 = (x_offset + x_ratio * 2, y_offset)
    # 左上角
    vertex4 = (x_offset, y_offset)
    
    return vertex1, vertex2, vertex3, vertex4