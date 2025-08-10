#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Sketch Duel - 游戏入口文件

这是游戏的主入口点，负责初始化游戏引擎并启动游戏。
"""

import sys
import logging
from pathlib import Path
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.core.game_engine import GameEngine
from game.data.models.player import Player, PlayerType
from game.config.config_manager import ConfigManager


def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('game.log'),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    """主函数"""
    try:
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting AI Sketch Duel...")
        
        # 加载所有配置
        config_manager = ConfigManager(Path(__file__).parent.parent / "config")
        config_manager.load_all_configs()
        
        # 创建并启动游戏引擎
        game_engine = GameEngine(config_manager)
        
        # 添加人类玩家和AI玩家
        human_player = Player(
            player_id=str(uuid.uuid4()),
            name="人类玩家1",
            player_type=PlayerType.HUMAN
        )
        game_engine.add_player(human_player)
        logger.info(f"Added human player: {human_player.name}")

        ai_player = Player(
            player_id=str(uuid.uuid4()),
            name="AI玩家1",
            player_type=PlayerType.AI
        )
        game_engine.add_player(ai_player)
        logger.info(f"Added AI player: {ai_player.name}")
        
        # 启动游戏
        success = game_engine.start_game()
        if not success:
            logger.error("Failed to start game")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
    except Exception as e:
        logger.exception(f"Game crashed with error: {e}")
        sys.exit(1)
    finally:
        logger.info("Game shutdown complete")


if __name__ == "__main__":
    main()