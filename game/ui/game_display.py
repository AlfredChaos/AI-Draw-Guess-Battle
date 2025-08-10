"""
简单的游戏界面显示模块

用于验证事件系统和游戏流程的临时界面
"""

import pygame
import sys
from typing import List, Dict, Any
import logging
import os
import platform
from pathlib import Path

from ..core.event_bus import GameEvent, EventType
from ..data.models.player import Player

logger = logging.getLogger(__name__)


class GameDisplay:
    """游戏显示界面"""

    def __init__(self, event_bus):
        """初始化游戏显示界面"""
        self.event_bus = event_bus
        self.screen = None
        self.font = None
        self.running = False
        self.players: List[Player] = []
        self.current_word = ""
        self.game_state = "等待开始"
        self.game_data = {}

        # 注册事件监听器
        self._register_event_listeners()

    def _register_event_listeners(self) -> None:
        """注册事件监听器"""
        self.event_bus.subscribe(EventType.GAME_START, self._on_game_start)
        self.event_bus.subscribe(EventType.PLAYER_JOIN, self._on_player_join)
        self.event_bus.subscribe(EventType.PLAYER_LEAVE, self._on_player_leave)
        self.event_bus.subscribe(
            EventType.GAME_STATE_CHANGED, self._on_game_state_changed)
        self.event_bus.subscribe(
            EventType.ROUND_START, self._on_round_start)
        logger.debug("GameDisplay event listeners registered")

    def _on_game_start(self, event: GameEvent) -> None:
        """处理游戏开始事件"""
        logger.info("GameDisplay received GAME_START event")
        self.game_data = event.data
        if self.screen:  # 如果界面已打开，更新显示
            # 这里可以触发重绘，但实际在主循环中处理
            pass
        else:
            # 初始化显示界面
            self._initialize_display(event.data)

    def _on_player_join(self, event: GameEvent) -> None:
        """处理玩家加入事件"""
        logger.info(f"GameDisplay received PLAYER_JOIN event: {event.data}")
        player_data = {
            "player_id": event.data.get("player_id"),
            "player_name": event.data.get("player_name", "Unknown"),
            "player_type": event.data.get("player_type", "HUMAN")
        }
        
        # 添加玩家到列表
        self.players.append(player_data)
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_player_leave(self, event: GameEvent) -> None:
        """处理玩家离开事件"""
        logger.info(f"GameDisplay received PLAYER_LEAVE event: {event.data}")
        player_id = event.data.get("player_id")
        
        # 从玩家列表中移除玩家
        self.players = [p for p in self.players if p.get("player_id") != player_id]
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_game_state_changed(self, event: GameEvent) -> None:
        """处理游戏状态变更事件"""
        logger.info(
            f"GameDisplay received GAME_STATE_CHANGED event: {event.data}")
        to_state = event.data.get("to_state", "unknown")
        self.game_state = to_state
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_round_start(self, event: GameEvent) -> None:
        """处理回合开始事件"""
        logger.info(f"GameDisplay received ROUND_START event: {event.data}")
        round_number = event.data.get("round_number", 1)
        current_word = event.data.get("current_word", "")
        
        # 更新回合信息
        self.current_round = round_number
        self.current_word = current_word
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _initialize_display(self, game_data: Dict[str, Any]) -> None:
        """初始化显示界面"""
        logger.info("Initializing game display")

        try:
            # 初始化pygame
            pygame.init()

            # 创建窗口
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("AI Sketch Duel - 测试界面")

            # 设置支持中文的字体
            self.font = self._get_chinese_font(32)

            # 启动显示循环
            self.running = True
            self._display_loop()

        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")

    def _get_chinese_font(self, size: int):
        """获取支持中文显示的字体"""
        # 获取项目字体文件夹路径
        font_dir = Path(__file__).parent.parent / "Resources" / "font"
        
        # 检查字体文件夹是否存在
        if font_dir.exists() and font_dir.is_dir():
            # 获取所有字体文件
            font_files = list(font_dir.glob("*.ttf")) + list(font_dir.glob("*.otf")) + list(font_dir.glob("*.ttc"))
            
            # 尝试加载每个字体文件，直到找到一个可用的
            for font_file in font_files:
                try:
                    font = pygame.font.Font(str(font_file), size)
                    logger.info(f"成功加载项目字体: {font_file}")
                    return font
                except Exception as e:
                    logger.warning(f"加载项目字体失败 {font_file}: {e}")
                    continue
        
        # 如果项目字体文件夹不存在或没有可用字体，记录警告
        logger.warning("项目字体文件夹不存在或没有可用字体")
        
        # 使用pygame默认字体
        logger.warning("使用pygame默认字体")
        return pygame.font.Font(None, size)

    def _display_loop(self) -> None:
        """显示循环"""
        logger.info("Starting display loop")

        clock = pygame.time.Clock()

        while self.running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # 绘制界面
            self._draw_interface()

            # 更新显示
            pygame.display.flip()
            clock.tick(60)

        # 退出pygame
        pygame.quit()
        logger.info("Display loop ended")

    def _draw_interface(self) -> None:
        """绘制界面"""
        # 填充背景
        self.screen.fill((30, 30, 30))

        # 显示标题
        title_text = self.font.render(
            "AI Sketch Duel - 测试界面", True, (255, 255, 255))
        self.screen.blit(title_text, (50, 50))

        # 显示游戏状态
        state_text = self.font.render(
            f"游戏状态: {self.game_state}", True, (255, 255, 255))
        self.screen.blit(state_text, (50, 100))

        # 显示玩家列表标题
        players_title = self.font.render("玩家列表:", True, (255, 255, 255))
        self.screen.blit(players_title, (50, 150))

        # 显示玩家列表
        if self.players:
            for i, player in enumerate(self.players):
                player_text = self.font.render(
                    f"- {player['player_name']} ({'AI' if player['player_type'] == 'AI' else '人类'})", 
                    True, (200, 200, 200))
                self.screen.blit(player_text, (70, 190 + i * 40))
        else:
            no_player_text = self.font.render("暂无玩家", True, (150, 150, 150))
            self.screen.blit(no_player_text, (70, 190))

        # 显示选词系统标题
        word_system_title = self.font.render("选词系统:", True, (255, 255, 255))
        self.screen.blit(word_system_title, (50, 300))

        # 显示选词信息
        if self.current_word:
            word_text = self.font.render(f"- 当前词汇: {self.current_word}", True, (200, 200, 200))
        else:
            word_text = self.font.render("- 当前词汇: 待选择", True, (200, 200, 200))
        self.screen.blit(word_text, (70, 340))

        # 显示提示信息
        hint_text = self.font.render("按 ESC 键退出", True, (150, 150, 150))
        self.screen.blit(hint_text, (50, 550))