#!/usr/bin/env python3
"""Headless regression tests for matrix_pygame.py.

Runs under SDL's dummy video/audio drivers so it works in CI or any
container without a display. Uses stdlib unittest only (no pytest
dependency) since pygame is already required to run the app itself.

    python3 -m unittest test_matrix_pygame.py -v
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest

import pygame

import matrix_pygame as mp


class MatrixPygameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.width, cls.height = 400, 300
        cls.screen = pygame.display.set_mode((cls.width, cls.height))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.settings = mp.Settings()
        self.font = mp.find_font(self.settings.font_size)
        self.columns = max(1, int((self.width / self.settings.font_size) * self.settings.density))
        self.drops = mp.build_drops(self.columns)

    def test_find_font_returns_a_font(self):
        self.assertIsInstance(self.font, pygame.font.Font)

    def test_build_drops_length_matches_columns(self):
        self.assertEqual(len(self.drops), self.columns)

    def test_rand_char_is_from_active_charset(self):
        for charset in mp.CHARSET_ORDER:
            self.settings.charset = charset
            char = mp.rand_char(self.settings)
            self.assertIn(char, mp.CHARSETS[charset])

    def test_render_frame_runs_for_every_theme(self):
        for theme in mp.THEME_ORDER:
            self.settings.theme = theme
            for _ in range(10):
                mp.render_frame(
                    self.screen, self.settings, self.drops, self.columns,
                    self.width, self.height, 16, self.font, (self.width // 2, self.height // 2),
                )

    def test_render_frame_runs_with_glow_and_glitch_toggled(self):
        for glow in (True, False):
            for glitch in (True, False):
                self.settings.glow = glow
                self.settings.glitch = glitch
                mp.render_frame(
                    self.screen, self.settings, self.drops, self.columns,
                    self.width, self.height, 16, self.font, (0, 0),
                )

    def test_glow_never_exceeds_its_source_color(self):
        # Regression test: an earlier version stacked the bloom layers with
        # pygame.BLEND_RGBA_ADD. Because the head color is already
        # near-white (e.g. classic theme (200, 255, 220)), summing three
        # overlapping copies of it saturated straight to solid white/gray
        # boxes in a *single* draw call, well before any cross-frame
        # buildup. Alpha compositing over black can only pull a pixel
        # toward the source color, never past it, so every channel in the
        # glow's bounding box must stay <= the corresponding channel of the
        # color it was drawn with.
        surface = pygame.Surface((80, 80))
        surface.fill((0, 0, 0))
        head_color = mp.THEMES["green"]["head"]
        mp.draw_glow_char(surface, self.font, "ワ", head_color, (20, 20))

        raw = pygame.image.tostring(surface, "RGB")
        max_per_channel = (max(raw[0::3]), max(raw[1::3]), max(raw[2::3]))
        for channel_name, actual, source in zip("RGB", max_per_channel, head_color):
            self.assertLessEqual(
                actual, source,
                f"glow's {channel_name} channel reached {actual}, brighter than the "
                f"source color {head_color} — additive blending is saturating instead "
                "of compositing",
            )

    def test_handle_key_cycles_without_crashing(self):
        keys = [
            pygame.K_c, pygame.K_t, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET, pygame.K_g, pygame.K_f, pygame.K_m,
            pygame.K_r, pygame.K_h, pygame.K_SPACE,
        ]
        columns, drops, font, running = self.columns, self.drops, self.font, True
        for key in keys:
            columns, drops, font, running = mp.handle_key(
                key, self.settings, self.width, self.height, columns, drops, font
            )
            self.assertTrue(running)

    def test_handle_key_quit_keys_stop_the_loop(self):
        for key in (pygame.K_ESCAPE, pygame.K_q):
            _, _, _, running = mp.handle_key(
                key, self.settings, self.width, self.height, self.columns, self.drops, self.font
            )
            self.assertFalse(running)

    def test_draw_help_runs(self):
        small_font = mp.find_font(16)
        mp.draw_help(self.screen, small_font, self.settings)


if __name__ == "__main__":
    unittest.main()
