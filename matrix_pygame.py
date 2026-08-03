#!/usr/bin/env python3
"""Matrix-style digital rain visualizer, built with pygame.

Run:
    python3 matrix_pygame.py

Controls are printed on launch and shown in the in-app help overlay (H).
"""

import random
import sys

import pygame

CHARSETS = {
    "katakana": "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789",
    "binary": "01",
    "latin": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "hex": "0123456789ABCDEF",
}
CHARSET_ORDER = ["katakana", "binary", "latin", "hex"]

THEMES = {
    "green": {"fg": (0, 200, 90), "head": (200, 255, 220)},
    "amber": {"fg": (200, 130, 0), "head": (255, 235, 190)},
    "cyan": {"fg": (0, 190, 210), "head": (210, 250, 255)},
    "red": {"fg": (200, 30, 30), "head": (255, 210, 210)},
    "white": {"fg": (170, 180, 180), "head": (255, 255, 255)},
    "rainbow": {"fg": None, "head": (255, 255, 255)},
}
THEME_ORDER = ["green", "amber", "cyan", "red", "white", "rainbow"]

FPS = 60

# Katakana needs a CJK-capable font; most default monospace fonts don't have
# those glyphs and would render as tofu boxes, so prefer a CJK font when
# one is installed and only fall back to pygame's built-in font otherwise.
_FONT_CANDIDATES = [
    "notosansmonocjkjp",
    "notosanscjkjp",
    "msgothic",
    "ipagothic",
    "hiraginosans",
    "unifont",
    "dejavusansmono",
    "consolas",
    "couriernew",
]


def find_font(size):
    for name in _FONT_CANDIDATES:
        path = pygame.font.match_font(name)
        if path:
            try:
                return pygame.font.Font(path, size)
            except OSError:
                continue
    return pygame.font.Font(None, size)


class Settings:
    def __init__(self):
        self.charset = "katakana"
        self.theme = "green"
        self.speed = 1.0
        self.density = 1.0
        self.font_size = 18
        self.trail_alpha = 40  # 0-255, lower = longer trails
        self.glow = True
        self.glitch = False
        self.mouse_react = True
        self.paused = False
        self.show_help = True


class Drop:
    __slots__ = ("y", "speed", "hue")

    def __init__(self, y, speed, hue):
        self.y = y
        self.speed = speed
        self.hue = hue

    @staticmethod
    def random(start_above=True):
        y = random.uniform(-30, 0) if start_above else random.uniform(0, 30)
        return Drop(y, random.uniform(0.5, 1.0), random.uniform(0, 360))


def build_drops(columns):
    return [Drop.random() for _ in range(columns)]


def rand_char(settings):
    chars = CHARSETS[settings.charset]
    return chars[random.randrange(len(chars))]


def theme_colors(settings, drop, hue_step):
    theme = THEMES[settings.theme]
    if settings.theme == "rainbow":
        drop.hue = (drop.hue + hue_step) % 360
        fg = pygame.Color(0)
        fg.hsva = (drop.hue, 100, 70, 100)
        head = pygame.Color(0)
        head.hsva = (drop.hue, 40, 100, 100)
        return (fg.r, fg.g, fg.b), (head.r, head.g, head.b)
    return theme["fg"], theme["head"]


def draw_glow_char(surface, font, char, color, pos):
    """Cheap bloom: stack a few translucent oversized copies behind the crisp glyph.

    Uses normal alpha compositing (not additive) so it converges to a soft
    halo instead of accumulating to solid white as the glyph sweeps through
    overlapping sub-pixel positions across frames.
    """
    glow_surf = font.render(char, True, color)
    for offset, alpha in ((3, 30), (2, 45), (1, 65)):
        blob = pygame.transform.smoothscale(
            glow_surf,
            (glow_surf.get_width() + offset * 2, glow_surf.get_height() + offset * 2),
        )
        blob.set_alpha(alpha)
        surface.blit(blob, (pos[0] - offset, pos[1] - offset))
    surface.blit(glow_surf, pos)


def main():
    pygame.init()
    pygame.display.set_caption("Matrix Visualizer")
    screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    settings = Settings()
    font = find_font(settings.font_size)
    small_font = find_font(16)

    width, height = screen.get_size()
    columns = max(1, int((width / settings.font_size) * settings.density))
    drops = build_drops(columns)

    print(__doc__)
    print_controls()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                columns = max(1, int((width / settings.font_size) * settings.density))
                drops = build_drops(columns)
            elif event.type == pygame.KEYDOWN:
                columns, drops, font, running = handle_key(
                    event.key, settings, width, height, columns, drops, font
                )

        if not settings.paused:
            mouse_pos = pygame.mouse.get_pos()
            render_frame(screen, settings, drops, columns, width, height, dt, font, mouse_pos)

        if settings.show_help:
            draw_help(screen, small_font, settings)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def render_frame(screen, settings, drops, columns, width, height, dt, font, mouse_pos):
    trail = pygame.Surface((width, height))
    trail.set_alpha(settings.trail_alpha)
    trail.fill((0, 0, 0))
    screen.blit(trail, (0, 0))

    col_width = width / columns
    mouse_x, mouse_y = mouse_pos

    for i, drop in enumerate(drops):
        x = i * col_width
        y = drop.y * settings.font_size

        speed_mul = 1.0
        if settings.mouse_react:
            dx = x - mouse_x
            dy = y - mouse_y
            if dx * dx + dy * dy < 150 * 150:
                speed_mul = 2.5

        if not (settings.glitch and random.random() < 0.02):
            fg, head = theme_colors(settings, drop, hue_step=2)
            char = rand_char(settings)
            if settings.glow:
                draw_glow_char(screen, font, char, head, (x, y))
            else:
                screen.blit(font.render(char, True, head), (x, y))
            trail_char = rand_char(settings)
            trail_surf = font.render(trail_char, True, fg)
            trail_surf.set_alpha(220)
            screen.blit(trail_surf, (x, y - settings.font_size))

        if y > height and random.random() > 0.975:
            drop.y = 0
            drop.speed = random.uniform(0.5, 1.0)
        drop.y += drop.speed * settings.speed * speed_mul * (dt / 16.0)


def handle_key(key, settings, width, height, columns, drops, font):
    running = True
    rebuild = False

    if key in (pygame.K_ESCAPE, pygame.K_q):
        running = False
    elif key == pygame.K_SPACE:
        settings.paused = not settings.paused
    elif key == pygame.K_h:
        settings.show_help = not settings.show_help
    elif key == pygame.K_c:
        idx = (CHARSET_ORDER.index(settings.charset) + 1) % len(CHARSET_ORDER)
        settings.charset = CHARSET_ORDER[idx]
    elif key == pygame.K_t:
        idx = (THEME_ORDER.index(settings.theme) + 1) % len(THEME_ORDER)
        settings.theme = THEME_ORDER[idx]
    elif key == pygame.K_UP:
        settings.speed = round(min(3.0, settings.speed + 0.1), 2)
    elif key == pygame.K_DOWN:
        settings.speed = round(max(0.2, settings.speed - 0.1), 2)
    elif key == pygame.K_RIGHT:
        settings.density = round(min(2.0, settings.density + 0.1), 2)
        rebuild = True
    elif key == pygame.K_LEFT:
        settings.density = round(max(0.3, settings.density - 0.1), 2)
        rebuild = True
    elif key == pygame.K_RIGHTBRACKET:
        settings.font_size = min(32, settings.font_size + 2)
        rebuild = True
    elif key == pygame.K_LEFTBRACKET:
        settings.font_size = max(10, settings.font_size - 2)
        rebuild = True
    elif key == pygame.K_g:
        settings.glow = not settings.glow
    elif key == pygame.K_f:
        settings.glitch = not settings.glitch
    elif key == pygame.K_m:
        settings.mouse_react = not settings.mouse_react
    elif key == pygame.K_r:
        rebuild = True

    if rebuild:
        font = find_font(settings.font_size)
        columns = max(1, int((width / settings.font_size) * settings.density))
        drops = build_drops(columns)

    return columns, drops, font, running


def draw_help(screen, font, settings):
    lines = [
        f"[H] hide help   [SPACE] {'resume' if settings.paused else 'pause'}   [Q/ESC] quit",
        f"[C] charset: {settings.charset}   [T] theme: {settings.theme}",
        f"[UP/DOWN] speed: {settings.speed:.1f}x   [LEFT/RIGHT] density: {settings.density:.1f}x",
        f"[ [ / ] ] font size: {settings.font_size}px",
        f"[G] glow: {'on' if settings.glow else 'off'}   [F] glitch: {'on' if settings.glitch else 'off'}"
        f"   [M] mouse react: {'on' if settings.mouse_react else 'off'}   [R] reset",
    ]
    pad = 8
    line_h = font.get_height() + 4
    box_w = max(font.size(line)[0] for line in lines) + pad * 2
    box_h = line_h * len(lines) + pad * 2

    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((0, 15, 5, 190))
    pygame.draw.rect(overlay, (0, 255, 100, 120), overlay.get_rect(), width=1)
    for i, line in enumerate(lines):
        text = font.render(line, True, (180, 255, 190))
        overlay.blit(text, (pad, pad + i * line_h))
    screen.blit(overlay, (10, 10))


def print_controls():
    print(
        "\n".join(
            [
                "Controls:",
                "  SPACE        pause / resume",
                "  H            toggle help overlay",
                "  C            cycle character set",
                "  T            cycle theme",
                "  UP / DOWN    speed +/-",
                "  LEFT / RIGHT density +/-",
                "  [ / ]        font size -/+",
                "  G            toggle glow",
                "  F            toggle glitch flicker",
                "  M            toggle mouse reactivity",
                "  R            reset drops",
                "  Q / ESC      quit",
            ]
        )
    )


if __name__ == "__main__":
    main()
