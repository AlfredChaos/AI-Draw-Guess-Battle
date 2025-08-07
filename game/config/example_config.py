#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置系统使用示例

展示如何使用游戏配置系统的各种功能。
"""

import logging
from pathlib import Path

from game.config import (
    initialize_configs,
    get_config_manager,
    get_game_config,
    get_ui_config,
    get_ai_config
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """配置系统使用示例"""
    try:
        # 1. 初始化配置系统
        logger.info("初始化配置系统...")
        config_dir = Path("config")
        initialize_configs(config_dir)
        
        # 2. 获取配置管理器
        config_manager = get_config_manager()
        logger.info(f"配置管理器初始化完成，配置目录: {config_manager.config_dir}")
        
        # 3. 获取各种配置
        game_config = get_game_config()
        ui_config = get_ui_config()
        ai_config = get_ai_config()
        
        # 4. 显示当前配置
        logger.info("=== 游戏配置 ===")
        logger.info(f"游戏名称: {game_config.game_name}")
        logger.info(f"版本: {game_config.version}")
        logger.info(f"回合时间限制: {game_config.round_time_limit}秒")
        logger.info(f"最大回合数: {game_config.max_rounds}")
        
        logger.info("=== UI配置 ===")
        logger.info(f"窗口大小: {ui_config.window.width}x{ui_config.window.height}")
        logger.info(f"主题色: {ui_config.colors.primary}")
        logger.info(f"默认字体: {ui_config.fonts.default_font}")
        
        logger.info("=== AI配置 ===")
        logger.info(f"LLM模型: {ai_config.llm.model_name}")
        logger.info(f"文生图模型: {ai_config.text_to_image.model_name}")
        logger.info(f"缓存启用: {ai_config.cache.enabled}")
        
        # 5. 修改配置示例
        logger.info("\n=== 修改配置示例 ===")
        
        # 修改游戏配置
        game_config.round_time_limit = 90
        game_config.max_rounds = 5
        logger.info(f"修改回合时间限制为: {game_config.round_time_limit}秒")
        logger.info(f"修改最大回合数为: {game_config.max_rounds}")
        
        # 修改UI配置
        ui_config.window.width = 1920
        ui_config.window.height = 1080
        logger.info(f"修改窗口大小为: {ui_config.window.width}x{ui_config.window.height}")
        
        # 修改AI配置
        ai_config.llm.temperature = 0.8
        ai_config.text_to_image.steps = 30
        logger.info(f"修改LLM温度为: {ai_config.llm.temperature}")
        logger.info(f"修改文生图步数为: {ai_config.text_to_image.steps}")
        
        # 6. 保存配置
        logger.info("\n=== 保存配置 ===")
        config_manager.save_all_configs()
        logger.info("所有配置已保存")
        
        # 7. 重新加载配置
        logger.info("\n=== 重新加载配置 ===")
        config_manager.reload_all_configs()
        logger.info("所有配置已重新加载")
        
        # 8. 验证配置
        logger.info("\n=== 验证配置 ===")
        is_valid = config_manager.validate_all_configs()
        logger.info(f"配置验证结果: {'通过' if is_valid else '失败'}")
        
        # 9. 导出配置
        logger.info("\n=== 导出配置 ===")
        export_path = Path("exported_config.json")
        config_manager.export_config(export_path)
        logger.info(f"配置已导出到: {export_path}")
        
        # 10. 重置为默认配置
        logger.info("\n=== 重置为默认配置 ===")
        config_manager.reset_to_defaults()
        logger.info("配置已重置为默认值")
        
        # 11. 导入配置
        if export_path.exists():
            logger.info("\n=== 导入配置 ===")
            config_manager.import_config(export_path)
            logger.info(f"配置已从 {export_path} 导入")
            
            # 清理导出文件
            export_path.unlink()
            logger.info("清理导出文件")
        
        logger.info("\n配置系统示例运行完成！")
        
    except Exception as e:
        logger.error(f"配置系统示例运行失败: {e}")
        raise


if __name__ == "__main__":
    main()