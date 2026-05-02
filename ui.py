from __future__ import annotations

import pygame

from settings import (
    BACKGROUND_ACCENT,
    BACKGROUND_BOTTOM,
    BACKGROUND_TOP,
    BLACK,
    FONT_CANDIDATES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHADOW,
    WHITE,
)


def _load_font(size: int, bold: bool = False) -> pygame.font.Font:
    font_path = None
    for name in FONT_CANDIDATES:
        font_path = pygame.font.match_font(name)
        if font_path:
            break
    return pygame.font.Font(font_path, size)


class UI:
    def __init__(self) -> None:
        self.title_font = _load_font(52, bold=True)
        self.hero_font = _load_font(48, bold=True)
        self.subtitle_font = _load_font(26)
        self.body_font = _load_font(22)
        self.small_font = _load_font(18)
        self.mini_font = _load_font(16)
        self.hud_font = _load_font(24, bold=True)
        self.background = self._build_background()

    def draw_background(self, surface: pygame.Surface, scroll_distance: float) -> None:
        surface.blit(self.background, (0, 0))

        offset = int(scroll_distance * 0.6) % 80
        grid = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(40, SCREEN_WIDTH, 80):
            pygame.draw.line(grid, (255, 255, 255, 28), (x, 0), (x, SCREEN_HEIGHT), 1)

        for y in range(-80, SCREEN_HEIGHT + 80, 80):
            line_y = y - offset
            pygame.draw.line(grid, (255, 255, 255, 22), (0, line_y), (SCREEN_WIDTH, line_y), 1)
        surface.blit(grid, (0, 0))

        for index in range(6):
            radius = 18 + index * 12
            alpha = max(18, 70 - index * 8)
            glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*BACKGROUND_ACCENT, alpha), (radius * 2, radius * 2), radius)
            surface.blit(glow, (SCREEN_WIDTH - 150 - index * 9, 68 + index * 12))

    def draw_hud(
        self,
        surface: pygame.Surface,
        score: int,
        best_score: int,
        elapsed: float,
        speed: float,
        difficulty: float,
        difficulty_label: str,
    ) -> None:
        panel_layer = pygame.Surface((232, 138), pygame.SRCALPHA)
        panel = pygame.Rect(0, 0, 220, 126)
        pygame.draw.rect(panel_layer, (*BLACK, 170), panel, border_radius=18)
        pygame.draw.rect(panel_layer, (255, 255, 255, 220), panel, 2, border_radius=18)
        surface.blit(panel_layer, (14, 14))

        lines = [
            f"Score  {score}",
            f"Best   {best_score}",
            f"Time   {elapsed:05.1f}s",
            f"Speed  {speed:04.0f}  Lv.{difficulty * 9 + 1:0.1f}",
            f"Mode   {difficulty_label}",
        ]
        for index, line in enumerate(lines):
            text = self.hud_font.render(line, True, WHITE)
            surface.blit(text, (28, 24 + index * 22))

    def draw_start(self, surface: pygame.Surface, best_score: int, difficulty_label: str) -> None:
        panel_rect = pygame.Rect(28, 90, 424, 620)
        self._draw_panel(surface, panel_rect.x, panel_rect.y, panel_rect.width, panel_rect.height)

        self._draw_badge(surface, pygame.Rect(panel_rect.left + 24, panel_rect.top + 22, 144, 34), "WINDOW MODE")
        self._draw_center_text(surface, self.hero_font, "是男人就下100层", WHITE, panel_rect.top + 94)
        self._draw_center_text(surface, self.subtitle_font, "Down 100 with Pygame", (224, 232, 240), panel_rect.top + 146)

        stat_y = panel_rect.top + 178
        self._draw_info_card(
            surface,
            pygame.Rect(panel_rect.left + 24, stat_y, 176, 72),
            "当前模式",
            difficulty_label,
            BACKGROUND_ACCENT,
        )
        self._draw_info_card(
            surface,
            pygame.Rect(panel_rect.left + 224, stat_y, 176, 72),
            "最高分",
            str(best_score),
            (121, 195, 255),
        )

        goal_rect = pygame.Rect(panel_rect.left + 24, stat_y + 88, 156, 166)
        controls_rect = pygame.Rect(panel_rect.left + 198, stat_y + 88, 202, 166)
        legend_rect = pygame.Rect(panel_rect.left + 24, stat_y + 274, 376, 78)
        cta_rect = pygame.Rect(panel_rect.left + 56, panel_rect.bottom - 82, 312, 52)

        self._draw_goal_card(surface, goal_rect)
        self._draw_controls_card(surface, controls_rect)
        self._draw_platform_legend(surface, legend_rect)
        self._draw_cta_button(surface, cta_rect, "按 Space 或 Enter 开始")
        self._draw_center_text(surface, self.mini_font, "按 ESC 退出窗口", (191, 203, 224), panel_rect.bottom - 22)

    def draw_pause(self, surface: pygame.Surface) -> None:
        self._draw_overlay(surface)
        self._draw_center_text(surface, self.title_font, "暂停", WHITE, 306)
        self._draw_center_text(surface, self.body_font, "按 P 或 ESC 继续", BACKGROUND_ACCENT, 378)

    def draw_game_over(
        self,
        surface: pygame.Surface,
        score: int,
        best_score: int,
        elapsed: float,
        difficulty_label: str,
    ) -> None:
        self._draw_overlay(surface)
        self._draw_panel(surface, 66, 200, 348, 330)
        self._draw_center_text(surface, self.title_font, "Game Over", WHITE, 270)
        self._draw_center_text(surface, self.body_font, f"本局得分  {score}", (255, 238, 190), 332)
        self._draw_center_text(surface, self.body_font, f"坚持时间  {elapsed:0.1f}s", WHITE, 370)
        self._draw_center_text(surface, self.body_font, f"最高分数  {best_score}", WHITE, 408)
        self._draw_center_text(surface, self.small_font, f"模式: {difficulty_label}", BACKGROUND_ACCENT, 438)
        self._draw_center_text(surface, self.subtitle_font, "按 Space / Enter 再来一局", BACKGROUND_ACCENT, 474)

    def _draw_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 14, 165))
        surface.blit(overlay, (0, 0))

    def _draw_panel(self, surface: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        layer = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(layer, (*BLACK, 195), rect, border_radius=24)
        pygame.draw.rect(layer, (255, 255, 255, 240), rect, 2, border_radius=24)
        highlight = pygame.Rect(18, 18, width - 36, 28)
        pygame.draw.rect(layer, (*WHITE, 45), highlight, border_radius=12)
        inner = rect.inflate(-24, -24)
        pygame.draw.rect(layer, (255, 255, 255, 18), inner, 1, border_radius=18)
        surface.blit(layer, (x, y))

    def _draw_center_text(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        center_y: int,
    ) -> None:
        render = font.render(text, True, color)
        shadow = font.render(text, True, SHADOW)
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, center_y + 3))
        rect = render.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        surface.blit(shadow, shadow_rect)
        surface.blit(render, rect)

    def _draw_badge(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        self._draw_card(surface, rect, fill=(255, 214, 102, 38), border=(255, 214, 102, 170), radius=16)
        render = self.small_font.render(text, True, BACKGROUND_ACCENT)
        text_rect = render.get_rect(center=rect.center)
        surface.blit(render, text_rect)

    def _draw_info_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        title: str,
        value: str,
        accent: tuple[int, int, int],
    ) -> None:
        self._draw_card(surface, rect, fill=(11, 18, 31, 172), border=(255, 255, 255, 110), radius=18)
        pygame.draw.rect(surface, accent, pygame.Rect(rect.x + 14, rect.y + 14, 34, 5), border_radius=3)

        title_render = self.small_font.render(title, True, (188, 199, 220))
        value_render = self.body_font.render(value, True, WHITE)
        surface.blit(title_render, (rect.x + 14, rect.y + 24))
        surface.blit(value_render, (rect.x + 14, rect.y + 42))

    def _draw_goal_card(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self._draw_card(surface, rect, fill=(10, 16, 27, 178), border=(255, 255, 255, 110), radius=20)
        label = self.small_font.render("本局目标", True, WHITE)
        surface.blit(label, (rect.x + 14, rect.y + 12))

        bullets = [
            ("保持下落节奏", (121, 195, 255)),
            ("踩住安全平台", (102, 209, 148)),
            ("避开红色尖刺", (240, 98, 108)),
            ("尽量冲击高分", BACKGROUND_ACCENT),
        ]
        for index, (text, color) in enumerate(bullets):
            y = rect.y + 48 + index * 26
            pygame.draw.circle(surface, color, (rect.x + 20, y + 8), 5)
            render = self.mini_font.render(text, True, WHITE)
            surface.blit(render, (rect.x + 34, y))

        player_rect = pygame.Rect(rect.right - 58, rect.bottom - 66, 30, 40)
        platform_rect = pygame.Rect(rect.x + 24, rect.bottom - 34, rect.width - 48, 14)
        pygame.draw.rect(surface, SHADOW, platform_rect.move(0, 4), border_radius=8)
        pygame.draw.rect(surface, (96, 177, 255), platform_rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, platform_rect.inflate(-14, -8), 2, border_radius=5)
        pygame.draw.rect(surface, SHADOW, player_rect.move(0, 4), border_radius=11)
        pygame.draw.rect(surface, (255, 174, 66), player_rect, border_radius=11)
        pygame.draw.rect(surface, (255, 242, 204), pygame.Rect(player_rect.x + 6, player_rect.y + 7, 18, 9), border_radius=5)
        pygame.draw.circle(surface, (48, 34, 18), (player_rect.centerx - 5, player_rect.centery + 2), 2)
        pygame.draw.circle(surface, (48, 34, 18), (player_rect.centerx + 3, player_rect.centery + 2), 2)

    def _draw_controls_card(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self._draw_card(surface, rect, fill=(10, 16, 27, 178), border=(255, 255, 255, 110), radius=20)
        label = self.small_font.render("按键操作", True, WHITE)
        surface.blit(label, (rect.x + 14, rect.y + 12))

        rows = [
            ("A / D", "左右移动", (121, 195, 255)),
            ("← / →", "方向键移动", (139, 220, 255)),
            ("P / ESC", "暂停 / 继续", (255, 214, 102)),
            ("R", "快速重开", (255, 153, 128)),
        ]
        for index, (key_text, title, accent) in enumerate(rows):
            row_rect = pygame.Rect(rect.x + 12, rect.y + 42 + index * 28, rect.width - 24, 24)
            if index > 0:
                pygame.draw.line(surface, (255, 255, 255, 26), (row_rect.x, row_rect.y - 4), (row_rect.right, row_rect.y - 4), 1)
            self._draw_keycap(surface, pygame.Rect(row_rect.x, row_rect.y, 72, 24), key_text, accent)
            title_render = self.mini_font.render(title, True, WHITE)
            surface.blit(title_render, (row_rect.x + 84, row_rect.y + 3))

    def _draw_platform_legend(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self._draw_card(surface, rect, fill=(10, 16, 27, 178), border=(255, 255, 255, 110), radius=20)
        label = self.small_font.render("平台提示", True, WHITE)
        surface.blit(label, (rect.x + 14, rect.y + 12))

        entries = [
            ("移动", (96, 177, 255), rect.x + 14, rect.y + 40),
            ("脆弱", (250, 204, 123), rect.x + 108, rect.y + 40),
            ("弹跳", (183, 130, 255), rect.x + 202, rect.y + 40),
            ("尖刺", (240, 98, 108), rect.x + 296, rect.y + 40),
        ]
        for text, color, x, y in entries:
            pill = pygame.Rect(x, y, 68, 28)
            self._draw_card(surface, pill, fill=(*color, 28), border=(*color, 155), radius=14)
            pygame.draw.circle(surface, color, (pill.x + 14, pill.centery), 5)
            render = self.mini_font.render(text, True, WHITE)
            surface.blit(render, (pill.x + 26, pill.y + 6))

    def _draw_cta_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        shadow_rect = rect.move(0, 6)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=20)
        button = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button, (255, 179, 76, 255), button.get_rect(), border_radius=20)
        pygame.draw.rect(button, (255, 227, 148, 255), pygame.Rect(0, 0, rect.width, rect.height // 2 + 2), border_radius=20)
        pygame.draw.rect(button, (255, 255, 255, 180), button.get_rect(), 2, border_radius=20)
        surface.blit(button, rect.topleft)

        render = self.body_font.render(text, True, BLACK)
        shadow = self.body_font.render(text, True, (255, 248, 220))
        shadow_rect = shadow.get_rect(center=(rect.centerx, rect.centery - 2))
        text_rect = render.get_rect(center=(rect.centerx, rect.centery))
        surface.blit(shadow, shadow_rect)
        surface.blit(render, text_rect)

    def _draw_keycap(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        accent: tuple[int, int, int],
    ) -> None:
        self._draw_card(surface, rect, fill=(*accent, 42), border=(*accent, 175), radius=12)
        render = self.small_font.render(text, True, WHITE)
        text_rect = render.get_rect(center=rect.center)
        surface.blit(render, text_rect)

    def _draw_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        *,
        fill: tuple[int, int, int, int],
        border: tuple[int, int, int, int],
        radius: int,
    ) -> None:
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        local_rect = pygame.Rect(0, 0, rect.width, rect.height)
        pygame.draw.rect(layer, fill, local_rect, border_radius=radius)
        pygame.draw.rect(layer, border, local_rect, 1, border_radius=radius)
        top_glow = pygame.Rect(12, 10, max(0, rect.width - 24), min(20, rect.height // 3))
        if top_glow.width > 0 and top_glow.height > 0:
            pygame.draw.rect(layer, (255, 255, 255, 18), top_glow, border_radius=10)
        surface.blit(layer, rect.topleft)

    def _build_background(self) -> pygame.Surface:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / max(1, SCREEN_HEIGHT - 1)
            color = (
                int(BACKGROUND_TOP[0] + (BACKGROUND_BOTTOM[0] - BACKGROUND_TOP[0]) * ratio),
                int(BACKGROUND_TOP[1] + (BACKGROUND_BOTTOM[1] - BACKGROUND_TOP[1]) * ratio),
                int(BACKGROUND_TOP[2] + (BACKGROUND_BOTTOM[2] - BACKGROUND_TOP[2]) * ratio),
            )
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
        return background
