from __future__ import annotations

from pathlib import Path

import pygame

from game_platform import Platform
from level_manager import LevelManager
from player import Player
from settings import (
    DEFAULT_DIFFICULTY,
    DEATH_BUFFER,
    DIFFICULTY_LABELS,
    FPS,
    LANDING_TOLERANCE,
    SAVE_FILE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCORE_DISTANCE_FACTOR,
    SCORE_TIME_FACTOR,
    STATE_GAME_OVER,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_START,
    TITLE,
    TOP_BOUNDARY_Y,
    WORLD_SCROLL_ACCEL,
    WORLD_SCROLL_BASE,
    WORLD_SCROLL_MAX,
    PLATFORM_BOUNCE,
    PLATFORM_FRAGILE,
    PLATFORM_MOVING,
    PLATFORM_SPIKE,
)
from ui import UI


class Game:
    def __init__(self, difficulty_mode: str = DEFAULT_DIFFICULTY) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.ui = UI()
        self.player = Player()
        self.level_manager = LevelManager(difficulty_mode=difficulty_mode)

        self.platforms: list[Platform] = []
        self.running = True
        self.state = STATE_START
        self.elapsed = 0.0
        self.total_scroll = 0.0
        self.score = 0
        self.best_score = self._load_best_score()
        self.current_scroll_speed = WORLD_SCROLL_BASE
        self.current_difficulty = 0.0
        self.difficulty_mode = self.level_manager.difficulty_mode
        self.difficulty_label = DIFFICULTY_LABELS[self.difficulty_mode]
        self.scroll_speed_multiplier = self.level_manager.preset["scroll_speed_multiplier"]

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.state == STATE_PLAYING:
                self._update(dt)
            self._render()

        pygame.quit()

    def _start_round(self) -> None:
        self.player.reset()
        self.platforms = self.level_manager.build_initial_platforms()
        self.elapsed = 0.0
        self.total_scroll = 0.0
        self.score = 0
        self.current_scroll_speed = WORLD_SCROLL_BASE
        self.current_difficulty = 0.0
        self.state = STATE_PLAYING

    def _update(self, dt: float) -> None:
        self.elapsed += dt
        self.current_difficulty = min(1.0, self.elapsed / 85.0)
        self.current_scroll_speed = min(
            (WORLD_SCROLL_BASE + self.elapsed * WORLD_SCROLL_ACCEL) * self.scroll_speed_multiplier,
            WORLD_SCROLL_MAX * self.scroll_speed_multiplier,
        )
        scroll_step = self.current_scroll_speed * dt
        self.total_scroll += scroll_step

        self.player.begin_frame()
        for platform in self.platforms:
            platform.begin_frame()

        self.player.handle_input(pygame.key.get_pressed(), dt)
        self.player.update(dt)

        for platform in self.platforms:
            platform.update(dt)
            platform.shift(-scroll_step)

        self._resolve_collisions()
        self._handle_top_boundary()

        self.platforms = [platform for platform in self.platforms if not platform.should_remove()]
        self.level_manager.ensure_platforms(self.platforms, self.current_difficulty)

        self.score = int(self.elapsed * SCORE_TIME_FACTOR + self.total_scroll * SCORE_DISTANCE_FACTOR)
        if not self.player.alive or self.player.rect.top > SCREEN_HEIGHT + DEATH_BUFFER:
            self._finish_round()

    def _resolve_collisions(self) -> None:
        landing_platform: Platform | None = None

        for platform in self.platforms:
            if platform.broken:
                continue

            if platform.kind == PLATFORM_SPIKE and self.player.rect.colliderect(platform.rect.inflate(-8, -3)):
                self.player.die()
                return

            if self.player.velocity.y < 0 or not platform.is_solid:
                continue

            if not self.player.rect.colliderect(platform.rect):
                continue

            landed_from_above = (
                self.player.prev_rect.bottom <= platform.prev_rect.top + LANDING_TOLERANCE
                and self.player.rect.bottom >= platform.rect.top
            )
            if landed_from_above:
                if landing_platform is None or platform.rect.top < landing_platform.rect.top:
                    landing_platform = platform

        if landing_platform is None:
            return

        self.player.land_on(landing_platform.rect)
        if landing_platform.kind == PLATFORM_MOVING:
            self.player.ride_platform(landing_platform.frame_dx)
        elif landing_platform.kind == PLATFORM_FRAGILE:
            landing_platform.trigger_fragile()
        elif landing_platform.kind == PLATFORM_BOUNCE:
            self.player.bounce()

    def _handle_top_boundary(self) -> None:
        if self.player.rect.top > TOP_BOUNDARY_Y:
            return

        self.player.hit_ceiling(TOP_BOUNDARY_Y)

        for platform in self.platforms:
            if platform.is_solid and self.player.rect.colliderect(platform.rect):
                self.player.die()
                return

    def _finish_round(self) -> None:
        self.state = STATE_GAME_OVER
        if self.score > self.best_score:
            self.best_score = self.score
            self._save_best_score()

    def _render(self) -> None:
        self.ui.draw_background(self.screen, self.total_scroll)

        for platform in self.platforms:
            platform.draw(self.screen)
        if self.state != STATE_START or self.platforms:
            self.player.draw(self.screen)

        if self.state == STATE_PLAYING:
            self.ui.draw_hud(
                self.screen,
                self.score,
                self.best_score,
                self.elapsed,
                self.current_scroll_speed,
                self.current_difficulty,
                self.difficulty_label,
            )
        elif self.state == STATE_START:
            self.ui.draw_start(self.screen, self.best_score, self.difficulty_label)
        elif self.state == STATE_PAUSED:
            self.ui.draw_hud(
                self.screen,
                self.score,
                self.best_score,
                self.elapsed,
                self.current_scroll_speed,
                self.current_difficulty,
                self.difficulty_label,
            )
            self.ui.draw_pause(self.screen)
        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(self.screen, self.score, self.best_score, self.elapsed, self.difficulty_label)

        pygame.display.flip()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state in (STATE_START, STATE_GAME_OVER):
                    self._start_round()
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                continue

            if event.key == pygame.K_r:
                self._start_round()
                continue

            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                if self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                elif self.state == STATE_START:
                    self.running = False
                elif self.state == STATE_GAME_OVER and event.key == pygame.K_ESCAPE:
                    self.running = False

    def _load_best_score(self) -> int:
        try:
            return int(Path(SAVE_FILE).read_text(encoding="utf-8").strip() or "0")
        except (FileNotFoundError, ValueError):
            return 0

    def _save_best_score(self) -> None:
        Path(SAVE_FILE).write_text(str(self.best_score), encoding="utf-8")
