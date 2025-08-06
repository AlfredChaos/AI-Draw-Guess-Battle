#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Sketch Duel - 游戏入口文件

这是游戏的主入口点，负责初始化游戏引擎并启动游戏。
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.core.game_engine import GameEngine
from game.config.game_config import GameConfig


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
        
        # 加载配置
        config = GameConfig.load_default()
        
        # 创建并启动游戏引擎
        game_engine = GameEngine(config)
        game_engine.run()
        
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
    except Exception as e:
        logger.exception(f"Game crashed with error: {e}")
        sys.exit(1)
    finally:
        logger.info("Game shutdown complete")


if __name__ == "__main__":
    main()