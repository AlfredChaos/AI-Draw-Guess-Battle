"""
坐标转换服务单元测试
"""

import unittest
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.services.coordinate_service import (
    pygame_to_opengl, 
    opengl_to_pygame, 
    texture_coordinates_to_vertices
)


class TestCoordinateService(unittest.TestCase):
    
    def setUp(self):
        """测试前的准备工作"""
        self.screen_width = 1280
        self.screen_height = 720
    
    def test_pygame_to_opengl_conversion(self):
        """测试Pygame到OpenGL坐标转换"""
        # 测试左上角 (0, 0) -> (-1, 1)
        opengl_x, opengl_y = pygame_to_opengl(0, 0, self.screen_width, self.screen_height)
        self.assertAlmostEqual(opengl_x, -1.0, places=5)
        self.assertAlmostEqual(opengl_y, 1.0, places=5)
        
        # 测试右下角 (1280, 720) -> (1, -1)
        opengl_x, opengl_y = pygame_to_opengl(
            self.screen_width, 
            self.screen_height, 
            self.screen_width, 
            self.screen_height
        )
        self.assertAlmostEqual(opengl_x, 1.0, places=5)
        self.assertAlmostEqual(opengl_y, -1.0, places=5)
        
        # 测试中心点 (640, 360) -> (0, 0)
        opengl_x, opengl_y = pygame_to_opengl(
            self.screen_width/2, 
            self.screen_height/2, 
            self.screen_width, 
            self.screen_height
        )
        self.assertAlmostEqual(opengl_x, 0.0, places=5)
        self.assertAlmostEqual(opengl_y, 0.0, places=5)
    
    def test_opengl_to_pygame_conversion(self):
        """测试OpenGL到Pygame坐标转换"""
        # 测试左上角 (-1, 1) -> (0, 0)
        pygame_x, pygame_y = opengl_to_pygame(-1.0, 1.0, self.screen_width, self.screen_height)
        self.assertAlmostEqual(pygame_x, 0.0, places=5)
        self.assertAlmostEqual(pygame_y, 0.0, places=5)
        
        # 测试右下角 (1, -1) -> (1280, 720)
        pygame_x, pygame_y = opengl_to_pygame(1.0, -1.0, self.screen_width, self.screen_height)
        self.assertAlmostEqual(pygame_x, self.screen_width, places=5)
        self.assertAlmostEqual(pygame_y, self.screen_height, places=5)
        
        # 测试中心点 (0, 0) -> (640, 360)
        pygame_x, pygame_y = opengl_to_pygame(0.0, 0.0, self.screen_width, self.screen_height)
        self.assertAlmostEqual(pygame_x, self.screen_width/2, places=5)
        self.assertAlmostEqual(pygame_y, self.screen_height/2, places=5)
    
    def test_bidirectional_conversion(self):
        """测试双向转换一致性"""
        # 测试一些随机点的双向转换
        test_points = [
            (0, 0),
            (100, 200),
            (640, 360),
            (1280, 720),
            (500, 400)
        ]
        
        for x, y in test_points:
            # Pygame -> OpenGL -> Pygame
            opengl_x, opengl_y = pygame_to_opengl(x, y, self.screen_width, self.screen_height)
            back_x, back_y = opengl_to_pygame(opengl_x, opengl_y, self.screen_width, self.screen_height)
            
            self.assertAlmostEqual(x, back_x, places=5)
            self.assertAlmostEqual(y, back_y, places=5)
    
    def test_texture_coordinates_to_vertices(self):
        """测试纹理坐标到顶点坐标的转换"""
        # 纹理参数
        x, y = 100, 150  # 纹理在屏幕上的位置
        width, height = 200, 100  # 纹理尺寸
        
        vertices = texture_coordinates_to_vertices(
            x, y, width, height, self.screen_width, self.screen_height
        )
        
        # 应该返回4个顶点
        self.assertEqual(len(vertices), 4)
        
        # 检查顶点顺序（逆时针）
        vertex1, vertex2, vertex3, vertex4 = vertices
        
        # 左下角应该有最小的Y值
        self.assertLess(vertex1[1], vertex4[1])
        # 右下角X值应该最大，Y值应该与左下角相同
        self.assertGreater(vertex2[0], vertex1[0])
        self.assertEqual(vertex2[1], vertex1[1])
        # 右上角Y值应该最大
        self.assertGreater(vertex3[1], vertex2[1])
        # 左上角X值应该与左下角相同，Y值应该与右上角相同
        self.assertEqual(vertex4[0], vertex1[0])
        self.assertEqual(vertex4[1], vertex3[1])


if __name__ == '__main__':
    unittest.main()