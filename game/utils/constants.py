"""
游戏常量定义模块

定义游戏中使用的所有常量值，包括屏幕尺寸、颜色、游戏规则等。
"""

# 屏幕和显示常量
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 颜色常量 (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

# 玩家相关常量
PLAYER_COLORS = {
    "human": (0, 150, 255),  # 人类玩家 - 蓝色
    "ai": (255, 100, 0)      # AI玩家 - 橙色
}

# 游戏状态常量
GAME_STATE_WAITING = "waiting"
GAME_STATE_DRAWING = "drawing"
GAME_STATE_GUESSING = "guessing"
GAME_STATE_SCORING = "scoring"
GAME_STATE_GAME_OVER = "game_over"

# 回合相关常量
MAX_ROUNDS = 3
DRAWING_TIME_LIMIT = 90  # 秒

# 绘画工具常量
TOOL_PEN = "pen"
TOOL_ERASER = "eraser"

# 默认绘画设置
DEFAULT_PEN_SIZE = 3
DEFAULT_ERASER_SIZE = 15

# AI难度等级
AI_DIFFICULTY_EASY = "easy"
AI_DIFFICULTY_MEDIUM = "medium"
AI_DIFFICULTY_HARD = "hard"

# 词汇难度等级
WORD_DIFFICULTY_EASY = "easy"
WORD_DIFFICULTY_MEDIUM = "medium"
WORD_DIFFICULTY_HARD = "hard"

# 积分系统常量
BASE_SCORE_FOR_DRAWER = 20
BASE_SCORE_FOR_GUESSER = 30
TIME_BONUS_FACTOR = 1  # 每剩余一秒加1分
SPEED_BONUS_THRESHOLD = 0.33  # 前1/3时间猜中获得额外奖励
SPEED_BONUS_POINTS = 10  # 速通奖励分数

# 文件路径常量
RESOURCES_DIR = "game/Resources"
WORDS_FILE = "words.json"
CONFIG_DIR = "game/config"