"""
事件总线系统单元测试
"""

import sys
import os
import unittest
from unittest.mock import Mock
import time

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.core.event_bus import (
    EventBus, GameEvent, EventType, 
    get_event_bus, publish_event, subscribe_event
)


class TestEventBus(unittest.TestCase):
    """测试事件总线系统"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.event_bus = EventBus()
    
    def test_event_creation(self):
        """测试事件创建"""
        # 创建基本事件
        event_data = {"test": "data"}
        event = GameEvent(
            event_type=EventType.GAME_START,
            data=event_data
        )
        
        self.assertEqual(event.event_type, EventType.GAME_START)
        self.assertEqual(event.data, event_data)
        self.assertIsNotNone(event.timestamp)
        self.assertIsNotNone(event.event_id)
    
    def test_event_bus_subscribe_and_publish(self):
        """测试事件订阅和发布"""
        # 创建监听器
        listener = Mock()
        
        # 订阅事件
        subscription_id = self.event_bus.subscribe(EventType.GAME_START, listener)
        self.assertIsNotNone(subscription_id)
        
        # 发布事件
        event = GameEvent(event_type=EventType.GAME_START)
        self.event_bus.publish(event)
        
        # 验证监听器被调用
        listener.assert_called_once_with(event)
    
    def test_event_bus_subscribe_once(self):
        """测试一次性事件订阅"""
        # 创建监听器
        listener = Mock()
        
        # 订阅一次性事件
        subscription_id = self.event_bus.subscribe_once(EventType.GAME_START, listener)
        self.assertIsNotNone(subscription_id)
        
        # 发布事件
        event1 = GameEvent(event_type=EventType.GAME_START)
        self.event_bus.publish(event1)
        
        # 再次发布事件
        event2 = GameEvent(event_type=EventType.GAME_START)
        self.event_bus.publish(event2)
        
        # 验证监听器只被调用一次
        listener.assert_called_once_with(event1)
    
    def test_event_bus_unsubscribe(self):
        """测试取消事件订阅"""
        # 创建监听器
        listener = Mock()
        
        # 订阅事件
        self.event_bus.subscribe(EventType.GAME_START, listener)
        
        # 取消订阅
        result = self.event_bus.unsubscribe(EventType.GAME_START, listener)
        self.assertTrue(result)
        
        # 发布事件
        event = GameEvent(event_type=EventType.GAME_START)
        self.event_bus.publish(event)
        
        # 验证监听器未被调用
        listener.assert_not_called()
    
    def test_event_bus_has_listeners(self):
        """测试检查监听器存在性"""
        # 初始状态应该没有监听器
        self.assertFalse(self.event_bus.has_listeners(EventType.GAME_START))
        
        # 添加监听器
        listener = Mock()
        self.event_bus.subscribe(EventType.GAME_START, listener)
        
        # 现在应该有监听器
        self.assertTrue(self.event_bus.has_listeners(EventType.GAME_START))
    
    def test_event_bus_get_listener_count(self):
        """测试获取监听器数量"""
        # 初始状态应该没有监听器
        self.assertEqual(self.event_bus.get_listener_count(EventType.GAME_START), 0)
        
        # 添加监听器
        listener1 = Mock()
        listener2 = Mock()
        self.event_bus.subscribe(EventType.GAME_START, listener1)
        self.event_bus.subscribe(EventType.GAME_START, listener2)
        
        # 现在应该有两个监听器
        self.assertEqual(self.event_bus.get_listener_count(EventType.GAME_START), 2)
    
    def test_event_bus_clear_listeners(self):
        """测试清除监听器"""
        # 添加监听器
        listener1 = Mock()
        listener2 = Mock()
        self.event_bus.subscribe(EventType.GAME_START, listener1)
        self.event_bus.subscribe(EventType.GAME_END, listener2)
        
        # 清除特定事件类型的监听器
        self.event_bus.clear_listeners(EventType.GAME_START)
        
        # 检查监听器是否被清除
        self.assertEqual(self.event_bus.get_listener_count(EventType.GAME_START), 0)
        self.assertEqual(self.event_bus.get_listener_count(EventType.GAME_END), 1)
        
        # 清除所有监听器
        self.event_bus.clear_listeners()
        
        # 检查所有监听器是否被清除
        self.assertEqual(self.event_bus.get_listener_count(EventType.GAME_END), 0)
    
    def test_event_data_integrity(self):
        """测试事件数据完整性"""
        # 创建带有复杂数据的事件
        complex_data = {
            "player_id": "player1",
            "score": 100,
            "position": (10, 20),
            "metadata": {
                "timestamp": time.time(),
                "version": "1.0"
            }
        }
        
        event = GameEvent(
            event_type=EventType.SCORE_UPDATE,
            data=complex_data
        )
        
        # 验证数据完整性
        self.assertEqual(event.data, complex_data)
        self.assertEqual(event.data["player_id"], "player1")
        self.assertEqual(event.data["score"], 100)
        self.assertEqual(event.data["position"], (10, 20))
    
    def test_global_event_bus(self):
        """测试全局事件总线"""
        # 获取全局事件总线
        global_bus1 = get_event_bus()
        global_bus2 = get_event_bus()
        
        # 验证是同一个实例
        self.assertIs(global_bus1, global_bus2)
        
        # 测试全局事件发布和订阅
        listener = Mock()
        subscribe_event(EventType.GAME_START, listener)
        
        event = GameEvent(event_type=EventType.GAME_START)
        publish_event(event)
        
        # 验证监听器被调用
        listener.assert_called_once_with(event)


if __name__ == '__main__':
    unittest.main()