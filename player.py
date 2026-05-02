from __future__ import annotations

import pygame

from settings import (
    PLAYER_ACCENT,
    PLAYER_BOUNCE_SPEED,
    PLAYER_COLOR,
    PLAYER_GRAVITY,
    PLAYER_HEIGHT,
    PLAYER_MAX_FALL_SPEED,
    PLAYER_MOVE_SPEED,
    PLAYER_START_X,
    PLAYER_START_Y,
    PLAYER_WIDTH,
    SCREEN_WIDTH,
    SHADOW,
)


class Player:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.prev_rect = self.rect.copy()
        self.position = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.alive = True
        self.facing = 1
        self.on_platform = False
        self.reset()

    def reset(self) -> None:
        self.position.update(PLAYER_START_X, PLAYER_START_Y)
        self.velocity.update(0, 0)
        self.alive = True
        self.facing = 1
        self.on_platform = False
        self._sync_rect()
        self.prev_rect = self.rect.copy()

    def begin_frame(self) -> None:
        self.prev_rect = self.rect.copy()
        self.on_platform = False

    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        if direction:
            self.position.x += direction * PLAYER_MOVE_SPEED * dt
            self.facing = 1 if direction > 0 else -1
        self.position.x = max(0, min(self.position.x, SCREEN_WIDTH - self.rect.width))
        self._sync_rect()

    def update(self, dt: float) -> None:
        self.velocity.y = min(self.velocity.y + PLAYER_GRAVITY * dt, PLAYER_MAX_FALL_SPEED)
        self.position.y += self.velocity.y * dt
        self._sync_rect()

    def land_on(self, platform_rect: pygame.Rect) -> None:
        self.position.y = platform_rect.top - self.rect.height
        self.velocity.y = 0.0
        self.on_platform = True
        self._sync_rect()

    def ride_platform(self, dx: float) -> None:
        self.position.x += dx
        self.position.x = max(0, min(self.position.x, SCREEN_WIDTH - self.rect.width))
        self._sync_rect()

    def bounce(self, power: float = PLAYER_BOUNCE_SPEED) -> None:
        self.velocity.y = -power
        self.on_platform = False

    def hit_ceiling(self, boundary_y: int) -> None:
        self.position.y = boundary_y
        if self.velocity.y < 0:
            self.velocity.y = 0.0
        self._sync_rect()

    def die(self) -> None:
        self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        shadow = self.rect.move(0, 5)
        pygame.draw.rect(surface, SHADOW, shadow, border_radius=12)
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, border_radius=12)

        visor = pygame.Rect(self.rect.left + 7, self.rect.top + 8, self.rect.width - 14, 11)
        pygame.draw.rect(surface, PLAYER_ACCENT, visor, border_radius=6)

        eye_y = self.rect.centery + 3
        center_x = self.rect.centerx
        offset = 5 * self.facing
        pygame.draw.circle(surface, (48, 34, 18), (center_x - 6 + offset, eye_y), 2)
        pygame.draw.circle(surface, (48, 34, 18), (center_x + 2 + offset, eye_y), 2)

        feet_y = self.rect.bottom - 4
        pygame.draw.line(surface, (166, 88, 35), (self.rect.left + 9, feet_y), (self.rect.left + 15, feet_y), 3)
        pygame.draw.line(surface, (166, 88, 35), (self.rect.right - 15, feet_y), (self.rect.right - 9, feet_y), 3)

    def _sync_rect(self) -> None:
        self.rect.topleft = (round(self.position.x), round(self.position.y))
