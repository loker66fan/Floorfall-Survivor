from __future__ import annotations

import random

from game_platform import Platform
from settings import (
    DEFAULT_DIFFICULTY,
    DIFFICULTY_PRESETS,
    MOVING_PLATFORM_SPEED_MAX,
    MOVING_PLATFORM_SPEED_MIN,
    PLATFORM_BOUNCE,
    PLATFORM_EDGE_PADDING,
    PLATFORM_FRAGILE,
    PLATFORM_GAP_MAX,
    PLATFORM_GAP_MIN,
    PLATFORM_MAX_WIDTH,
    PLATFORM_MIN_WIDTH,
    PLATFORM_MOVING,
    PLATFORM_NORMAL,
    PLATFORM_SPAWN_BUFFER,
    PLATFORM_SPIKE,
    PLATFORM_TARGET_COUNT,
    PLAYER_HEIGHT,
    PLAYER_START_X,
    PLAYER_START_Y,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class LevelManager:
    def __init__(self, seed: int | None = None, difficulty_mode: str = DEFAULT_DIFFICULTY) -> None:
        self.rng = random.Random(seed)
        self.difficulty_mode = difficulty_mode if difficulty_mode in DIFFICULTY_PRESETS else DEFAULT_DIFFICULTY
        self.preset = DIFFICULTY_PRESETS[self.difficulty_mode]
        self.spawn_cursor = 0.0
        self.last_spawn_x = PLAYER_START_X
        self.spike_streak = 0

    def set_difficulty_mode(self, difficulty_mode: str) -> None:
        if difficulty_mode not in DIFFICULTY_PRESETS:
            difficulty_mode = DEFAULT_DIFFICULTY
        self.difficulty_mode = difficulty_mode
        self.preset = DIFFICULTY_PRESETS[difficulty_mode]

    def reset(self) -> None:
        self.spawn_cursor = PLAYER_START_Y + PLAYER_HEIGHT + 40
        self.last_spawn_x = PLAYER_START_X
        self.spike_streak = 0

    def build_initial_platforms(self) -> list[Platform]:
        self.reset()
        platforms: list[Platform] = []

        start_width = 132
        start_x = max(PLATFORM_EDGE_PADDING, min(PLAYER_START_X - 46, SCREEN_WIDTH - start_width - PLATFORM_EDGE_PADDING))
        start_y = PLAYER_START_Y + PLAYER_HEIGHT + 34
        platforms.append(Platform(start_x, start_y, start_width, PLATFORM_NORMAL))
        self.last_spawn_x = start_x
        self.spawn_cursor = start_y

        while self.spawn_cursor < SCREEN_HEIGHT + PLATFORM_SPAWN_BUFFER + self.preset["spawn_buffer_offset"]:
            platform = self._spawn_platform(self.spawn_cursor + self._next_gap(0.0), difficulty=0.0, safe_bias=True)
            platforms.append(platform)
            self.spawn_cursor = platform.y

        return platforms

    def ensure_platforms(self, platforms: list[Platform], difficulty: float) -> None:
        if platforms:
            self.spawn_cursor = max(self.spawn_cursor, max(platform.y for platform in platforms))

        target_count = max(10, PLATFORM_TARGET_COUNT + self.preset["platform_count_bonus"])
        spawn_limit = SCREEN_HEIGHT + PLATFORM_SPAWN_BUFFER + self.preset["spawn_buffer_offset"]
        active_count = len([platform for platform in platforms if not platform.broken])
        while active_count < target_count or self.spawn_cursor < spawn_limit:
            platform = self._spawn_platform(self.spawn_cursor + self._next_gap(difficulty), difficulty=difficulty)
            platforms.append(platform)
            self.spawn_cursor = platform.y
            active_count += 1

    def _spawn_platform(self, y: float, difficulty: float, safe_bias: bool = False) -> Platform:
        width_shrink = int(20 * difficulty)
        width_bonus = self.preset["width_bonus"]
        min_width = max(68, PLATFORM_MIN_WIDTH - width_shrink + width_bonus)
        max_width = max(min_width + 8, PLATFORM_MAX_WIDTH - width_shrink + width_bonus)
        width = self.rng.randint(min_width, max_width)

        reach = int(160 + difficulty * 65 + self.preset["reach_bonus"])
        if self.rng.random() < 0.2:
            x = self.rng.randint(PLATFORM_EDGE_PADDING, SCREEN_WIDTH - width - PLATFORM_EDGE_PADDING)
        else:
            min_x = max(PLATFORM_EDGE_PADDING, int(self.last_spawn_x - reach))
            max_x = min(SCREEN_WIDTH - width - PLATFORM_EDGE_PADDING, int(self.last_spawn_x + reach))
            if min_x > max_x:
                min_x, max_x = PLATFORM_EDGE_PADDING, SCREEN_WIDTH - width - PLATFORM_EDGE_PADDING
            x = self.rng.randint(min_x, max_x)

        kind = self._choose_platform_type(difficulty, safe_bias=safe_bias)
        move_speed = 0.0
        move_direction = 1
        if kind == PLATFORM_MOVING:
            move_speed = self.rng.uniform(MOVING_PLATFORM_SPEED_MIN, MOVING_PLATFORM_SPEED_MAX + difficulty * 20)
            move_direction = self.rng.choice([-1, 1])

        self.last_spawn_x = x
        if kind == PLATFORM_SPIKE:
            self.spike_streak += 1
        else:
            self.spike_streak = 0

        return Platform(x=x, y=y, width=width, kind=kind, move_speed=move_speed, move_direction=move_direction)

    def _choose_platform_type(self, difficulty: float, safe_bias: bool = False) -> str:
        if safe_bias:
            choices = [PLATFORM_NORMAL, PLATFORM_MOVING, PLATFORM_FRAGILE]
            choices.extend([PLATFORM_NORMAL] * self.preset["safe_choice_bias"])
            return self.rng.choice(choices)

        if self.spike_streak >= 1:
            choices = [PLATFORM_NORMAL, PLATFORM_MOVING, PLATFORM_FRAGILE, PLATFORM_BOUNCE]
            return self.rng.choice(choices)

        weights = {
            PLATFORM_NORMAL: 0.55 - difficulty * 0.18,
            PLATFORM_MOVING: 0.16 + difficulty * 0.06 + self.preset["moving_weight_bonus"],
            PLATFORM_FRAGILE: 0.13 + difficulty * 0.04 + self.preset["fragile_weight_bonus"],
            PLATFORM_SPIKE: (0.08 + difficulty * 0.11) * self.preset["hazard_weight_scale"],
            PLATFORM_BOUNCE: 0.08 + difficulty * 0.03 + self.preset["bounce_weight_bonus"],
        }
        weights[PLATFORM_NORMAL] = max(0.25, 1.0 - sum(weight for kind, weight in weights.items() if kind != PLATFORM_NORMAL))
        for kind, weight in list(weights.items()):
            weights[kind] = max(0.02, weight)

        total = sum(weights.values())
        pick = self.rng.random() * total
        cumulative = 0.0
        for kind, weight in weights.items():
            cumulative += weight
            if pick <= cumulative:
                return kind
        return PLATFORM_NORMAL

    def _next_gap(self, difficulty: float) -> int:
        extra_gap = int(26 * difficulty)
        min_gap = max(58, PLATFORM_GAP_MIN + extra_gap // 2 + self.preset["gap_min_offset"])
        max_gap = max(min_gap + 8, PLATFORM_GAP_MAX + extra_gap + self.preset["gap_max_offset"])
        return self.rng.randint(min_gap, max_gap)
