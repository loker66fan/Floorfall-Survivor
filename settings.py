from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
TITLE = "是男人就下100层"
FPS = 60

DIFFICULTY_EASY = "easy"
DIFFICULTY_HARD = "hard"
DEFAULT_DIFFICULTY = DIFFICULTY_EASY

STATE_START = "start"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

BACKGROUND_TOP = (12, 19, 34)
BACKGROUND_BOTTOM = (44, 77, 111)
BACKGROUND_ACCENT = (255, 214, 102)
WHITE = (245, 247, 250)
BLACK = (14, 18, 27)
SHADOW = (12, 14, 22)

PLAYER_WIDTH = 34
PLAYER_HEIGHT = 46
PLAYER_START_X = (SCREEN_WIDTH - PLAYER_WIDTH) / 2
PLAYER_START_Y = 170
PLAYER_MOVE_SPEED = 280.0
PLAYER_GRAVITY = 1650.0
PLAYER_MAX_FALL_SPEED = 920.0
PLAYER_BOUNCE_SPEED = 980.0
PLAYER_COLOR = (255, 174, 66)
PLAYER_ACCENT = (255, 242, 204)

WORLD_SCROLL_BASE = 140.0
WORLD_SCROLL_ACCEL = 4.5
WORLD_SCROLL_MAX = 320.0
DEATH_BUFFER = 80
TOP_BOUNDARY_Y = 0

SCORE_TIME_FACTOR = 20
SCORE_DISTANCE_FACTOR = 0.15
LANDING_TOLERANCE = 10

PLATFORM_HEIGHT = 18
PLATFORM_TARGET_COUNT = 14
PLATFORM_MIN_WIDTH = 82
PLATFORM_MAX_WIDTH = 138
PLATFORM_EDGE_PADDING = 20
PLATFORM_GAP_MIN = 76
PLATFORM_GAP_MAX = 122
PLATFORM_SPAWN_BUFFER = 220

MOVING_PLATFORM_SPEED_MIN = 72.0
MOVING_PLATFORM_SPEED_MAX = 120.0
FRAGILE_BREAK_DELAY = 0.18

PLATFORM_NORMAL = "normal"
PLATFORM_MOVING = "moving"
PLATFORM_FRAGILE = "fragile"
PLATFORM_SPIKE = "spike"
PLATFORM_BOUNCE = "bounce"

DIFFICULTY_LABELS = {
    DIFFICULTY_EASY: "简单",
    DIFFICULTY_HARD: "困难",
}

DIFFICULTY_PRESETS = {
    DIFFICULTY_EASY: {
        "scroll_speed_multiplier": 0.9,
        "gap_min_offset": -10,
        "gap_max_offset": -14,
        "spawn_buffer_offset": 30,
        "reach_bonus": 26,
        "safe_choice_bias": 3,
        "platform_count_bonus": 2,
        "hazard_weight_scale": 0.72,
        "moving_weight_bonus": -0.02,
        "fragile_weight_bonus": -0.015,
        "bounce_weight_bonus": 0.02,
        "width_bonus": 12,
    },
    DIFFICULTY_HARD: {
        "scroll_speed_multiplier": 1.16,
        "gap_min_offset": 14,
        "gap_max_offset": 24,
        "spawn_buffer_offset": -20,
        "reach_bonus": -22,
        "safe_choice_bias": 0,
        "platform_count_bonus": -1,
        "hazard_weight_scale": 1.38,
        "moving_weight_bonus": 0.05,
        "fragile_weight_bonus": 0.03,
        "bounce_weight_bonus": -0.01,
        "width_bonus": -8,
    },
}

SAVE_FILE = BASE_DIR / "best_score.txt"

FONT_CANDIDATES = [
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
    "DejaVu Sans",
]
