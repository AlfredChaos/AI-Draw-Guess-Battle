"""
游戏服务模块包
"""

from .coordinate_service import (
    pygame_to_opengl,
    opengl_to_pygame,
    texture_coordinates_to_vertices
)

from .word_service import (
    WordService,
    get_word_service,
    reset_word_service
)

__all__ = [
    'pygame_to_opengl',
    'opengl_to_pygame',
    'texture_coordinates_to_vertices',
    'WordService',
    'get_word_service',
    'reset_word_service'
]