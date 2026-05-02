export const WORLD_WIDTH = 480;
export const WORLD_HEIGHT = 800;
export const FPS = 60;

export const DIFFICULTY_EASY = "easy";
export const DIFFICULTY_HARD = "hard";
export const DEFAULT_DIFFICULTY = DIFFICULTY_EASY;

export const DIFFICULTY_LABELS = {
  [DIFFICULTY_EASY]: "简单",
  [DIFFICULTY_HARD]: "困难",
};

export const STATE_START = "start";
export const STATE_PLAYING = "playing";
export const STATE_PAUSED = "paused";
export const STATE_GAME_OVER = "game_over";

export const PLAYER_WIDTH = 34;
export const PLAYER_HEIGHT = 46;
export const PLAYER_START_X = (WORLD_WIDTH - PLAYER_WIDTH) / 2;
export const PLAYER_START_Y = 170;
export const PLAYER_MOVE_SPEED = 280;
export const PLAYER_GRAVITY = 1650;
export const PLAYER_MAX_FALL_SPEED = 920;
export const PLAYER_BOUNCE_SPEED = 980;

export const WORLD_SCROLL_BASE = 140;
export const WORLD_SCROLL_ACCEL = 4.5;
export const WORLD_SCROLL_MAX = 320;
export const DEATH_BUFFER = 80;
export const TOP_BOUNDARY_Y = 0;

export const SCORE_TIME_FACTOR = 20;
export const SCORE_DISTANCE_FACTOR = 0.15;
export const LANDING_TOLERANCE = 10;

export const PLATFORM_HEIGHT = 18;
export const PLATFORM_TARGET_COUNT = 14;
export const PLATFORM_MIN_WIDTH = 82;
export const PLATFORM_MAX_WIDTH = 138;
export const PLATFORM_EDGE_PADDING = 20;
export const PLATFORM_GAP_MIN = 76;
export const PLATFORM_GAP_MAX = 122;
export const PLATFORM_SPAWN_BUFFER = 220;

export const MOVING_PLATFORM_SPEED_MIN = 72;
export const MOVING_PLATFORM_SPEED_MAX = 120;
export const FRAGILE_BREAK_DELAY = 0.18;

export const PLATFORM_NORMAL = "normal";
export const PLATFORM_MOVING = "moving";
export const PLATFORM_FRAGILE = "fragile";
export const PLATFORM_SPIKE = "spike";
export const PLATFORM_BOUNCE = "bounce";

export const DIFFICULTY_PRESETS = {
  [DIFFICULTY_EASY]: {
    scrollSpeedMultiplier: 0.9,
    gapMinOffset: -10,
    gapMaxOffset: -14,
    spawnBufferOffset: 30,
    reachBonus: 26,
    safeChoiceBias: 3,
    platformCountBonus: 2,
    hazardWeightScale: 0.72,
    movingWeightBonus: -0.02,
    fragileWeightBonus: -0.015,
    bounceWeightBonus: 0.02,
    widthBonus: 12,
  },
  [DIFFICULTY_HARD]: {
    scrollSpeedMultiplier: 1.16,
    gapMinOffset: 14,
    gapMaxOffset: 24,
    spawnBufferOffset: -20,
    reachBonus: -22,
    safeChoiceBias: 0,
    platformCountBonus: -1,
    hazardWeightScale: 1.38,
    movingWeightBonus: 0.05,
    fragileWeightBonus: 0.03,
    bounceWeightBonus: -0.01,
    widthBonus: -8,
  },
};

export const COLORS = {
  backgroundTop: "#0c1322",
  backgroundBottom: "#2c4d6f",
  backgroundAccent: "#ffd666",
  white: "#f5f7fa",
  black: "#0e121b",
  shadow: "#0c0e16",
  player: "#ffae42",
  playerAccent: "#fff2cc",
  platform: {
    [PLATFORM_NORMAL]: "#66d194",
    [PLATFORM_MOVING]: "#60b1ff",
    [PLATFORM_FRAGILE]: "#facc7b",
    [PLATFORM_SPIKE]: "#f0626c",
    [PLATFORM_BOUNCE]: "#b782ff",
  },
};
