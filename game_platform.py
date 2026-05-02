from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from settings import (
    FRAGILE_BREAK_DELAY,
    MOVING_PLATFORM_SPEED_MAX,
    MOVING_PLATFORM_SPEED_MIN,
    PLATFORM_BOUNCE,
    PLATFORM_FRAGILE,
    PLATFORM_HEIGHT,
    PLATFORM_MOVING,
    PLATFORM_NORMAL,
    PLATFORM_SPIKE,
    SCREEN_WIDTH,
    SHADOW,
    WHITE,
)

PLATFORM_COLORS = {
    PLATFORM_NORMAL: (102, 209, 148),
    PLATFORM_MOVING: (96, 177, 255),
    PLATFORM_FRAGILE: (250, 204, 123),
    PLATFORM_SPIKE: (240, 98, 108),
    PLATFORM_BOUNCE: (183, 130, 255),
}


@dataclass
class Platform:
    x: float
    y: float
    width: int
    kind: str = PLATFORM_NORMAL
    move_speed: float = 0.0
    move_direction: int = 1
    rect: pygame.Rect = field(init=False)
    prev_rect: pygame.Rect = field(init=False)
    broken: bool = field(default=False, init=False)
    breaking: bool = field(default=False, init=False)
    break_timer: float | None = field(default=None, init=False)
    frame_dx: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        if self.kind == PLATFORM_MOVING and self.move_speed <= 0:
            self.move_speed = (MOVING_PLATFORM_SPEED_MIN + MOVING_PLATFORM_SPEED_MAX) / 2
        self.rect = pygame.Rect(round(self.x), round(self.y), self.width, PLATFORM_HEIGHT)
        self.prev_rect = self.rect.copy()

    @property
    def is_hazard(self) -> bool:
        return self.kind == PLATFORM_SPIKE

    @property
    def is_solid(self) -> bool:
        return not self.broken and self.kind != PLATFORM_SPIKE

    def begin_frame(self) -> None:
        self.prev_rect = self.rect.copy()
        self.frame_dx = 0.0

    def update(self, dt: float) -> None:
        if self.breaking and self.break_timer is not None:
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.broken = True

        if self.broken:
            return

        if self.kind == PLATFORM_MOVING:
            self.frame_dx = self.move_speed * self.move_direction * dt
            self.x += self.frame_dx
            if self.x <= 0:
                self.x = 0
                self.move_direction = 1
            elif self.x + self.width >= SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.width
                self.move_direction = -1

        self._sync_rect()

    def shift(self, dy: float) -> None:
        self.y += dy
        self._sync_rect()

    def trigger_fragile(self) -> None:
        if self.kind == PLATFORM_FRAGILE and not self.breaking:
            self.breaking = True
            self.break_timer = FRAGILE_BREAK_DELAY

    def should_remove(self) -> bool:
        return self.broken or self.rect.bottom < -90

    def draw(self, surface: pygame.Surface) -> None:
        if self.broken:
            return

        base_color = PLATFORM_COLORS[self.kind]
        shadow_rect = self.rect.move(0, 4)
        pygame.draw.rect(surface, SHADOW, shadow_rect, border_radius=9)
        pygame.draw.rect(surface, base_color, self.rect, border_radius=9)
        pygame.draw.rect(surface, WHITE, self.rect.inflate(-16, -10), 2, border_radius=6)

        if self.kind == PLATFORM_MOVING:
            self._draw_arrows(surface)
        elif self.kind == PLATFORM_FRAGILE:
            self._draw_fragile(surface)
        elif self.kind == PLATFORM_SPIKE:
            self._draw_spikes(surface)
        elif self.kind == PLATFORM_BOUNCE:
            self._draw_bounce(surface)

    def _draw_arrows(self, surface: pygame.Surface) -> None:
        center_y = self.rect.centery
        left_x = self.rect.left + 16
        right_x = self.rect.right - 16
        arrow_color = (18, 53, 99)
        pygame.draw.line(surface, arrow_color, (left_x, center_y), (right_x, center_y), 3)
        pygame.draw.polygon(
            surface,
            arrow_color,
            [(left_x, center_y), (left_x + 10, center_y - 7), (left_x + 10, center_y + 7)],
        )
        pygame.draw.polygon(
            surface,
            arrow_color,
            [(right_x, center_y), (right_x - 10, center_y - 7), (right_x - 10, center_y + 7)],
        )

    def _draw_fragile(self, surface: pygame.Surface) -> None:
        crack_color = (122, 87, 44)
        points = [
            (self.rect.left + 12, self.rect.top + 5),
            (self.rect.centerx - 5, self.rect.centery),
            (self.rect.centerx + 4, self.rect.top + 4),
            (self.rect.right - 14, self.rect.centery + 4),
        ]
        pygame.draw.lines(surface, crack_color, False, points, 2)

    def _draw_spikes(self, surface: pygame.Surface) -> None:
        spike_color = (123, 13, 24)
        count = max(4, self.width // 16)
        spike_width = self.width / count
        for index in range(count):
            left = self.rect.left + spike_width * index
            right = left + spike_width
            top = self.rect.top - 10
            pygame.draw.polygon(
                surface,
                spike_color,
                [(left, self.rect.bottom - 2), ((left + right) / 2, top), (right, self.rect.bottom - 2)],
            )

    def _draw_bounce(self, surface: pygame.Surface) -> None:
        spring_color = (82, 36, 145)
        base_y = self.rect.centery + 1
        points = [
            (self.rect.left + 18, base_y),
            (self.rect.left + 28, base_y - 5),
            (self.rect.left + 38, base_y + 5),
            (self.rect.left + 48, base_y - 5),
            (self.rect.left + 58, base_y + 5),
            (self.rect.right - 18, base_y),
        ]
        pygame.draw.lines(surface, spring_color, False, points, 3)

    def _sync_rect(self) -> None:
        self.rect.topleft = (round(self.x), round(self.y))
