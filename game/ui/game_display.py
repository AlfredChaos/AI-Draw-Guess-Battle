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
import uuid
import random
import re
import time

from ..core.event_bus import GameEvent, EventType
from ..data.models.player import Player, PlayerType
from ..data.repositories.word_repository import WordRepository
from ..core.game_state import GameState
from ..core.scoring_system import get_scoring_system

logger = logging.getLogger(__name__)


class GameDisplay:
    """游戏显示界面"""

    def __init__(self, event_bus):
        """初始化游戏显示界面"""
        self.event_bus = event_bus
        self.screen = None
        self.font = None
        self.small_font = None
        self.medium_font = None
        self.running = False
        self.players: List[Dict] = []
        self.current_word = ""
        self.game_state = GameState.WAITING
        self.game_data = {}
        self.word_repository = WordRepository()
        
        # 回合和阶段信息
        self.current_round = 1
        self.total_rounds = 3
        self.current_phase = "等待开始"
        self.remaining_time = 0
        self.time_limit = 0
        
        # 按钮状态
        self.game_started = False
        self.round_started = False
        
        # 按钮区域定义
        self.buttons = {}
        
        # 当前绘制者
        self.current_drawer = None
        
        # 输入框相关
        self.input_text = ""
        self.input_active = False
        self.input_box = pygame.Rect(300, 500, 300, 40)
        self.composition_text = ""  # 输入法组合文本
        self.composition_pos = (0, 0)  # 输入法组合文本位置
        
        # 消息历史
        self.message_history = []
        
        # 当前玩家（默认为第一个人类玩家）
        self.current_player = None
        
        # 玩家顺序索引
        self.player_order_index = 0
        
        # AI预设回答
        self.ai_responses = [
            "这是一个动物",
            "它有长长的耳朵",
            "它是灰色的",
            "它喜欢胡萝卜",
            "它会跳跃",
            "它在森林里生活",
            "它很可爱",
            "它是哺乳动物"
        ]
        
        # AI猜测答案
        self.ai_guesses = [
            "兔子", "大象", "狮子", "老虎", "熊猫", "猴子", "长颈鹿", "斑马"
        ]
        
        # 积分系统
        self.scoring_system = get_scoring_system(event_bus)

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
        self.event_bus.subscribe(
            EventType.ROUND_END, self._on_round_end)
        self.event_bus.subscribe(
            EventType.SCORE_UPDATE, self._on_score_update)
        self.event_bus.subscribe(
            EventType.GUESS_CORRECT, self._on_guess_correct)
        self.event_bus.subscribe(
            EventType.GUESS_SUBMITTED, self._on_guess_submitted)
        logger.debug("GameDisplay event listeners registered")

    def _on_game_start(self, event: GameEvent) -> None:
        """处理游戏开始事件"""
        logger.info("GameDisplay received GAME_START event")
        self.game_data = event.data
        self.game_started = True
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
            "player_type": event.data.get("player_type", "HUMAN"),
            "score": 0  # 初始化分数
        }
        
        # 添加玩家到列表
        self.players.append(player_data)
        
        # 设置当前玩家为第一个人类玩家
        if not self.current_player and player_data["player_type"] == "HUMAN":
            self.current_player = player_data
        
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
        
        # 如果当前玩家离开，设置下一个玩家为当前玩家
        if self.current_player and self.current_player["player_id"] == player_id:
            human_players = [p for p in self.players if p["player_type"] == "HUMAN"]
            self.current_player = human_players[0] if human_players else None
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_game_state_changed(self, event: GameEvent) -> None:
        """处理游戏状态变更事件"""
        logger.info(
            f"GameDisplay received GAME_STATE_CHANGED event: {event.data}")
        to_state = event.data.get("to_state", "waiting")
        
        # 更新游戏状态显示
        state_names = {
            "waiting": "等待开始",
            "drawing": "绘画阶段",
            "guessing": "猜测阶段",
            "scoring": "结算阶段",
            "game_over": "游戏结束"
        }
        self.current_phase = state_names.get(to_state, to_state)
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_round_start(self, event: GameEvent) -> None:
        """处理回合开始事件"""
        logger.info(f"GameDisplay received ROUND_START event: {event.data}")
        round_number = event.data.get("round_number", 1)
        current_word = event.data.get("current_word", "")
        drawer_id = event.data.get("drawer_id", "")
        
        # 更新回合信息
        self.current_round = round_number
        self.current_word = current_word
        self.current_drawer = drawer_id
        self.round_started = True
        self.time_limit = event.data.get("time_limit", 60)
        self.remaining_time = self.time_limit
        self.current_phase = "绘画阶段"  # 更新阶段为绘画阶段
        
        # 添加回合开始消息
        drawer_name = next((p["player_name"] for p in self.players if p["player_id"] == drawer_id), "未知玩家")
        self._add_message(f"第 {round_number} 回合开始！{drawer_name} 是绘制者，正在绘制词汇...", "系统")
        
        # 如果是人类玩家作为绘制者，显示词汇
        if drawer_id == (self.current_player["player_id"] if self.current_player else None):
            self._add_message(f"你要绘制的词汇是: {current_word}", "系统")
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_round_end(self, event: GameEvent) -> None:
        """处理回合结束事件"""
        logger.info(f"GameDisplay received ROUND_END event: {event.data}")
        self.round_started = False
        self.current_word = ""
        self.current_drawer = None
        self.current_phase = "等待开始"
        
        # 添加回合结束消息
        self._add_message(f"第 {event.data.get('round_number', '未知')} 回合结束！正确答案是：{event.data.get('word', '未知')}", "系统")
        
        # 如果是第3回合结束，显示最终结果
        if event.data.get('round_number', 0) >= self.total_rounds:
            self._add_message("游戏结束！正在计算最终结果...", "系统")
        
        # 如果界面已打开，触发重绘
        if self.screen:
            # 在实际应用中，这里可以触发界面重绘
            pass

    def _on_score_update(self, event: GameEvent) -> None:
        """处理积分更新事件"""
        logger.info(f"GameDisplay received SCORE_UPDATE event: {event.data}")
        player_id = event.data.get("player_id")
        score = event.data.get("score", 0)
        total_score = event.data.get("total_score", 0)
        
        # 更新玩家分数
        for player in self.players:
            if player["player_id"] == player_id:
                player["score"] = total_score
                break
        
        # 添加积分更新消息
        player_name = event.data.get("player_name", "未知玩家")
        self._add_message(f"{player_name} 获得 {score} 分，总分: {total_score}", "积分系统")

    def _on_guess_correct(self, event: GameEvent) -> None:
        """处理猜中事件"""
        logger.info(f"GameDisplay received GUESS_CORRECT event: {event.data}")
        player_id = event.data.get("player")
        word = event.data.get("word")
        
        # 查找玩家名称
        player_name = "未知玩家"
        for player in self.players:
            if player["player_id"] == player_id:
                player_name = player["player_name"]
                break
        
        # 添加猜中消息
        self._add_message(f"{player_name} 猜中了词汇 '{word}'！", "系统")

    def _on_guess_submitted(self, event: GameEvent) -> None:
        """处理猜测提交事件"""
        logger.info(f"GameDisplay received GUESS_SUBMITTED event: {event.data}")
        player_id = event.data.get("player")
        guess = event.data.get("guess")
        is_correct = event.data.get("is_correct", False)
        
        # 查找玩家名称
        player_name = "未知玩家"
        for player in self.players:
            if player["player_id"] == player_id:
                player_name = player["player_name"]
                break
        
        # 添加猜测消息
        if is_correct:
            self._add_message(f"{player_name} 猜测 '{guess}' - 正确！", "系统")
        else:
            self._add_message(f"{player_name} 猜测 '{guess}' - 错误", "系统")

    def _initialize_display(self, game_data: Dict[str, Any]) -> None:
        """初始化显示界面"""
        logger.info("Initializing game display")

        try:
            # 初始化pygame
            pygame.init()

            # 创建窗口
            self.screen = pygame.display.set_mode((1000, 600))
            pygame.display.set_caption("AI Sketch Duel - 你画我猜")

            # 设置支持中文的字体
            self.font = self._get_chinese_font(32)
            self.medium_font = self._get_chinese_font(28)
            self.small_font = self._get_chinese_font(24)

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
        last_time = time.time()

        while self.running:
            # 计算时间差
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # 更新倒计时
            if self.round_started and self.remaining_time > 0:
                self.remaining_time = max(0, self.remaining_time - delta_time)
                
                # 如果是猜测阶段且时间快到了，AI自动猜测
                if self.current_phase == "猜测阶段" and self.remaining_time <= 5 and self.remaining_time > 4:
                    self._ai_make_guess()
                
                # 如果倒计时结束，进入下一阶段
                if self.remaining_time <= 0:
                    self._handle_time_up()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif self.input_active:
                        if event.key == pygame.K_RETURN:
                            self._send_message()
                        elif event.key == pygame.K_BACKSPACE:
                            if not self.composition_text:  # 只有在没有组合文本时才删除
                                self.input_text = self.input_text[:-1]
                        elif event.key == pygame.K_DELETE:
                            if not self.composition_text:  # 只有在没有组合文本时才删除
                                self.input_text = ""
                        # 注意：不再处理其他按键，避免与TEXTINPUT事件重复
                elif event.type == pygame.TEXTINPUT:
                    # 处理文本输入事件（包括中文输入法确认的文本）
                    if self.input_active and len(self.input_text) < 50:
                        self.input_text += event.text
                        self.composition_text = ""  # 清除组合文本
                elif event.type == pygame.TEXTEDITING:
                    # 处理输入法组合文本
                    self.composition_text = event.text
                    self.composition_pos = (event.start, event.length)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        self._handle_mouse_click(event.pos)

            # 绘制界面
            self._draw_interface()

            # 更新显示
            pygame.display.flip()
            clock.tick(60)

        # 退出pygame
        pygame.quit()
        logger.info("Display loop ended")

    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        x, y = pos
        
        # 检查是否点击了输入框
        if self.input_box.collidepoint(x, y):
            self.input_active = True
        else:
            self.input_active = False
            
        # 检查是否点击了开始回合按钮
        if "start_round" in self.buttons:
            button_rect = self.buttons["start_round"]
            if button_rect.collidepoint(x, y) and self.game_started and not self.round_started:
                self._start_round()
                return

    def _start_round(self):
        """开始回合"""
        # 按顺序选择一个玩家作为绘制者
        if self.players:
            drawer = self.players[self.player_order_index % len(self.players)]
            self.player_order_index += 1
            self.current_drawer = drawer["player_id"]
            
            # 从词库中随机选择一个词
            word_entry = self.word_repository.get_random_word()
            if word_entry:
                self.current_word = word_entry.text
                
                # 发布回合开始事件
                event = GameEvent(
                    event_type=EventType.ROUND_START,
                    data={
                        "round_number": self.current_round,
                        "drawer_id": self.current_drawer,
                        "current_word": self.current_word,
                        "time_limit": 60  # 设置时间限制为60秒
                    }
                )
                self.event_bus.publish(event)
                
                self.round_started = True
                self.remaining_time = 60
                self.time_limit = 60
                self.current_phase = "绘画阶段"
                
                # 如果是AI绘制者，让它描述词汇
                if drawer["player_type"] == "AI":
                    # 延迟1秒后让AI描述词汇
                    pygame.time.set_timer(pygame.USEREVENT, 1000)

    def _send_message(self):
        """发送消息"""
        if self.input_text.strip() and self.current_player:
            # 检查消息是否包含当前词汇，如果包含则进行屏蔽
            message = self.input_text.strip()
            sender = self.current_player["player_name"]
            
            # 如果消息包含当前词汇，则进行屏蔽
            if self.current_word and self.current_word in message:
                # 使用星号屏蔽词汇
                masked_message = re.sub(re.escape(self.current_word), '*' * len(self.current_word), message)
                self._add_message(masked_message, sender, True)  # 标记为已屏蔽
                
                # 如果是猜中词汇，发布猜中事件
                event = GameEvent(
                    event_type=EventType.GUESS_SUBMITTED,
                    data={
                        "player": self.current_player["player_id"],
                        "guess": message,
                        "is_correct": True
                    }
                )
                self.event_bus.publish(event)
                
                # 发布猜中事件
                correct_event = GameEvent(
                    event_type=EventType.GUESS_CORRECT,
                    data={
                        "player": self.current_player["player_id"],
                        "word": self.current_word,
                        "guess_time": self.time_limit - self.remaining_time
                    }
                )
                self.event_bus.publish(correct_event)
                
                # 为猜中的玩家增加积分
                player_obj = None
                for p in self.players:
                    if p["player_id"] == self.current_player["player_id"]:
                        player_obj = Player(
                            player_id=p["player_id"],
                            name=p["player_name"],
                            player_type=PlayerType.HUMAN if p["player_type"] == "HUMAN" else PlayerType.AI
                        )
                        break
                
                if player_obj:
                    # 计算得分（基于剩余时间）
                    time_bonus = int(self.remaining_time)
                    score = 30 + time_bonus  # 基础分30 + 时间奖励
                    self.scoring_system.add_score(player_obj, score, self.current_round, "guesser")
            else:
                self._add_message(message, sender)
            
            # 清空输入框
            self.input_text = ""
            
            # 取消输入框激活状态
            self.input_active = False

    def _add_message(self, message, sender, masked=False):
        """添加消息到历史记录"""
        self.message_history.append({
            "sender": sender,
            "message": message,
            "masked": masked,
            "timestamp": pygame.time.get_ticks()
        })
        
        # 限制消息历史数量
        if len(self.message_history) > 50:
            self.message_history.pop(0)

    def _ai_describe_word(self):
        """AI描述词汇"""
        # 随机选择几个描述
        descriptions = random.sample(self.ai_responses, min(3, len(self.ai_responses)))
        for desc in descriptions:
            self._add_message(desc, "AI玩家1")
            pygame.time.wait(1000)  # 等待1秒再发送下一条消息

    def _ai_make_guess(self):
        """AI进行猜测"""
        # AI随机猜测一个词
        guess = random.choice(self.ai_guesses)
        
        # 检查是否猜中
        is_correct = guess == self.current_word
        
        # 发布猜测事件
        event = GameEvent(
            event_type=EventType.GUESS_SUBMITTED,
            data={
                "player": next((p["player_id"] for p in self.players if p["player_type"] == "AI"), ""),
                "guess": guess,
                "is_correct": is_correct
            }
        )
        self.event_bus.publish(event)
        
        # 如果猜中，发布猜中事件
        if is_correct:
            correct_event = GameEvent(
                event_type=EventType.GUESS_CORRECT,
                data={
                    "player": next((p["player_id"] for p in self.players if p["player_type"] == "AI"), ""),
                    "word": self.current_word,
                    "guess_time": self.time_limit - self.remaining_time
                }
            )
            self.event_bus.publish(correct_event)
            
            # 为猜中的AI玩家增加积分
            ai_player = None
            for p in self.players:
                if p["player_type"] == "AI":
                    ai_player = Player(
                        player_id=p["player_id"],
                        name=p["player_name"],
                        player_type=PlayerType.AI
                    )
                    break
            
            if ai_player:
                # 计算得分（基于剩余时间）
                time_bonus = int(self.remaining_time)
                score = 30 + time_bonus  # 基础分30 + 时间奖励
                self.scoring_system.add_score(ai_player, score, self.current_round, "guesser")

    def _handle_time_up(self):
        """处理时间到事件"""
        # 如果当前是绘画阶段，进入猜测阶段
        if self.current_phase == "绘画阶段":
            self.current_phase = "猜测阶段"
            self.remaining_time = self.time_limit  # 重新开始倒计时
            self._add_message("绘画阶段结束，进入猜测阶段！", "系统")
        # 如果当前是猜测阶段，回合结束
        elif self.current_phase == "猜测阶段":
            self.current_phase = "等待开始"
            self.round_started = False
            self._add_message("猜测阶段结束，回合结束！", "系统")
            
            # 发布回合结束事件
            event = GameEvent(
                event_type=EventType.ROUND_END,
                data={
                    "round_number": self.current_round,
                    "word": self.current_word
                }
            )
            self.event_bus.publish(event)
            
            # 增加回合数，准备下一回合
            self.current_round += 1

    def _draw_button(self, text, x, y, width, height, enabled=True):
        """绘制按钮"""
        button_rect = pygame.Rect(x, y, width, height)
        color = (70, 130, 180) if enabled else (100, 100, 100)  # 蓝色或灰色
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), button_rect, 2)  # 边框
        
        # 绘制按钮文字
        text_surface = self.small_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return button_rect

    def _draw_input_box(self):
        """绘制输入框"""
        # 绘制输入框
        color = (255, 255, 255) if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (50, 50, 50), self.input_box)
        pygame.draw.rect(self.screen, color, self.input_box, 2)
        
        # 准备显示文本（包括普通文本和组合文本）
        display_text = self.input_text
        if self.composition_text:
            # 如果有组合文本，将其添加到显示文本中
            display_text += self.composition_text
            
        # 绘制输入文本
        txt_surface = self.small_font.render(display_text, True, (255, 255, 255))
        # 确保文本不会超出输入框
        if txt_surface.get_width() > self.input_box.width - 10:
            # 如果文本太长，截取末尾部分
            # 计算需要截取的起始位置
            start_pos = len(display_text) - (self.input_box.width - 10) // 10
            if start_pos < 0:
                start_pos = 0
            txt_surface = self.small_font.render(display_text[start_pos:], True, (255, 255, 255))
        
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 10))
        
        # 绘制输入框标签
        label = self.small_font.render("输入消息:", True, (255, 255, 255))
        self.screen.blit(label, (self.input_box.x, self.input_box.y - 30))

    def _draw_message_history(self):
        """绘制消息历史"""
        # 绘制消息历史区域背景
        history_rect = pygame.Rect(300, 120, 650, 350)
        pygame.draw.rect(self.screen, (40, 40, 40), history_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), history_rect, 2)
        
        # 绘制消息历史标题
        title = self.small_font.render("消息历史:", True, (255, 255, 255))
        self.screen.blit(title, (history_rect.x + 10, history_rect.y + 10))
        
        # 绘制消息
        if self.message_history:
            y_offset = 50
            for msg in self.message_history[-10:]:  # 只显示最近10条消息
                # 绘制发送者
                sender_text = self.small_font.render(f"{msg['sender']}:", True, (200, 200, 200))
                self.screen.blit(sender_text, (history_rect.x + 10, history_rect.y + y_offset))
                
                # 绘制消息内容
                message_color = (255, 100, 100) if msg['masked'] else (255, 255, 255)  # 屏蔽消息用红色显示
                message_text = self.small_font.render(msg['message'], True, message_color)
                self.screen.blit(message_text, (history_rect.x + 100, history_rect.y + y_offset))
                
                y_offset += 30
        else:
            # 没有消息时显示提示
            no_msg_text = self.small_font.render("暂无消息", True, (150, 150, 150))
            self.screen.blit(no_msg_text, (history_rect.x + 10, history_rect.y + 50))

    def _draw_game_info(self):
        """绘制游戏信息（回合、阶段、倒计时）"""
        # 绘制回合信息
        round_text = self.small_font.render(f"回合: {self.current_round}/{self.total_rounds}", True, (255, 255, 255))
        self.screen.blit(round_text, (500, 20))
        
        # 绘制阶段信息
        phase_text = self.small_font.render(f"阶段: {self.current_phase}", True, (255, 255, 255))
        self.screen.blit(phase_text, (500, 50))
        
        # 绘制倒计时
        if self.round_started and self.remaining_time > 0:
            time_text = self.small_font.render(f"倒计时: {int(self.remaining_time)}s", True, (255, 50, 50))
        else:
            time_text = self.small_font.render("倒计时: --", True, (200, 200, 200))
        self.screen.blit(time_text, (500, 80))

    def _draw_player_list(self):
        """绘制玩家列表和积分"""
        # 绘制玩家列表标题
        players_title = self.small_font.render("玩家列表:", True, (255, 255, 255))
        self.screen.blit(players_title, (50, 140))
        
        # 绘制玩家列表
        if self.players:
            for i, player in enumerate(self.players):
                # 高亮显示当前绘制者
                color = (200, 200, 200)
                if player["player_id"] == self.current_drawer:
                    color = (255, 215, 0)  # 金色表示绘制者
                
                player_text = self.small_font.render(
                    f"- {player['player_name']} ({'AI' if player['player_type'] == 'AI' else '人类'}) - {player['score']}分", 
                    True, color)
                self.screen.blit(player_text, (70, 170 + i * 30))
        else:
            no_player_text = self.small_font.render("暂无玩家", True, (150, 150, 150))
            self.screen.blit(no_player_text, (70, 170))

    def _draw_interface(self) -> None:
        """绘制界面"""
        # 填充背景
        self.screen.fill((30, 30, 30))

        # 显示标题
        title_text = self.font.render(
            "AI Sketch Duel - 你画我猜", True, (255, 255, 255))
        self.screen.blit(title_text, (50, 20))

        # 显示游戏信息（回合、阶段、倒计时）
        self._draw_game_info()

        # 显示当前玩家
        if self.current_player:
            current_player_text = self.small_font.render(
                f"当前玩家: {self.current_player['player_name']}", True, (255, 255, 255))
            self.screen.blit(current_player_text, (50, 100))

        # 显示玩家列表和积分
        self._draw_player_list()

        # 显示选词系统标题
        word_system_title = self.small_font.render("选词系统:", True, (255, 255, 255))
        self.screen.blit(word_system_title, (50, 250))

        # 显示选词信息
        if self.current_word and self.current_drawer == (self.current_player["player_id"] if self.current_player else None):
            # 如果是绘制者，显示真实词汇
            word_text = self.small_font.render(f"- 当前词汇: {self.current_word}", True, (255, 215, 0))  # 金色显示词汇
        elif self.current_word:
            # 如果不是绘制者，显示提示信息
            word_text = self.small_font.render("- 当前词汇: (仅绘制者可见)", True, (200, 200, 200))
        else:
            word_text = self.small_font.render("- 当前词汇: 待选择", True, (200, 200, 200))
        self.screen.blit(word_text, (70, 280))

        # 绘制按钮
        y_pos = 320
        button_width = 150
        button_height = 30
        button_spacing = 20

        # 开始回合按钮（只有在游戏开始后才启用）
        self.buttons["start_round"] = self._draw_button(
            "开始回合", 50, y_pos, button_width, button_height, 
            self.game_started and not self.round_started)
        y_pos += button_height + button_spacing

        # 绘制消息历史区域
        self._draw_message_history()
        
        # 绘制输入框
        self._draw_input_box()
        
        # 显示提示信息
        hint_text = self.small_font.render("按 ESC 键退出", True, (150, 150, 150))
        self.screen.blit(hint_text, (50, 570))