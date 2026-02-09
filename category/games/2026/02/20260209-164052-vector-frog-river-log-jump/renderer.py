"""Renderer for Vector Frog River Log Jump."""

import pygame
from game import GameState


class Renderer:
    def __init__(self, state: GameState):
        self.state = state
        self.screen = pygame.display.set_mode((state.width, state.height))
        pygame.display.set_caption("Vector Frog River Log Jump")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.grass_color = (60, 140, 60)
        self.grass_dark = (40, 100, 40)
        self.water_color = (40, 100, 160)
        self.water_dark = (30, 70, 120)
        self.log_color = (120, 80, 50)
        self.log_dark = (90, 60, 35)
        self.log_grain = (100, 70, 45)
        self.frog_color = (80, 180, 80)
        self.frog_dark = (50, 130, 50)
        self.frog_belly = (100, 200, 100)
        self.eye_color = (255, 255, 255)
        self.pupil_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.ui_bg = (0, 0, 0, 150)

    def render(self):
        # Draw background
        self.screen.fill((20, 20, 30))

        # Draw game areas
        self._draw_areas()

        # Draw logs
        for log in self.state.logs:
            self._draw_log(log)

        # Draw frog
        if self.state.frog.alive:
            self._draw_frog()

        # Draw HUD
        self._draw_hud()

        # Draw game over / win message
        if self.state.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_areas(self):
        # Draw water area (river)
        water_rect = (0, self.state.grid_size,
                     self.state.width,
                     self.state.grid_size * 12)
        pygame.draw.rect(self.screen, self.water_color, water_rect)

        # Draw water waves (subtle pattern)
        for row in range(12):
            y = (row + 1) * self.state.grid_size
            offset = (row * 13) % self.state.width
            for x in range(-20, self.state.width + 20, 40):
                wave_x = (x + offset) % (self.state.width + 40) - 20
                pygame.draw.line(self.screen, self.water_dark,
                               (wave_x, y), (wave_x + 20, y), 2)

        # Draw grass areas (safe zones)
        # Top grass
        top_grass = (0, 0, self.state.width, self.state.grid_size)
        pygame.draw.rect(self.screen, self.grass_color, top_grass)

        # Bottom grass
        bottom_grass = (0, self.state.grid_size * 13,
                       self.state.width, self.state.grid_size * 2)
        pygame.draw.rect(self.screen, self.grass_color, bottom_grass)

        # Draw grass texture
        for row in [0, 13, 14]:
            y = row * self.state.grid_size
            for x in range(0, self.state.width, 20):
                pygame.draw.line(self.screen, self.grass_dark,
                               (x + 5, y + 5), (x + 5, y + self.state.grid_size - 5), 2)
                pygame.draw.line(self.screen, self.grass_dark,
                               (x + 15, y + 8), (x + 15, y + self.state.grid_size - 8), 2)

        # Draw goal area highlight
        goal_rect = (0, 0, self.state.width, self.state.grid_size)
        s = pygame.Surface((self.state.width, self.state.grid_size), pygame.SRCALPHA)
        pygame.draw.rect(s, (100, 255, 100, 50), goal_rect)
        self.screen.blit(s, (0, 0))

    def _draw_log(self, log):
        x, y = int(log.pos.x), int(log.pos.y)
        w, h = log.width, log.height

        # Main log body
        pygame.draw.rect(self.screen, self.log_color, (x, y + 5, w, h - 10))

        # Log ends (rounded effect)
        pygame.draw.circle(self.screen, self.log_dark, (x, y + h // 2), h // 2 - 2)
        pygame.draw.circle(self.screen, self.log_dark, (x + w, y + h // 2), h // 2 - 2)

        # Wood grain texture
        for i in range(x + 10, x + w - 10, 15):
            pygame.draw.line(self.screen, self.log_grain,
                           (i, y + 10), (i, y + h - 10), 2)

        # Top highlight
        pygame.draw.rect(self.screen, (140, 100, 70), (x + 3, y + 7, w - 6, 5))

    def _draw_frog(self):
        frog = self.state.frog
        x = int(frog.pos.x)
        y = int(frog.pos.y - frog.hop_offset)
        w, h = frog.width, frog.height

        # Body
        body_rect = (x + 4, y + 8, w - 8, h - 12)
        pygame.draw.ellipse(self.screen, self.frog_color,
                           (x + 4, y + 8, w - 8, h - 12))

        # Belly
        belly_rect = (x + 8, y + 14, w - 16, h - 20)
        pygame.draw.ellipse(self.screen, self.frog_belly, belly_rect)

        # Head
        pygame.draw.ellipse(self.screen, self.frog_color, (x + 6, y + 2, w - 12, 14))

        # Eyes
        eye_size = 6
        pygame.draw.circle(self.screen, self.frog_color, (x + 10, y + 6), eye_size)
        pygame.draw.circle(self.screen, self.frog_color, (x + w - 10, y + 6), eye_size)
        pygame.draw.circle(self.screen, self.eye_color, (x + 10, y + 5), 4)
        pygame.draw.circle(self.screen, self.eye_color, (x + w - 10, y + 5), 4)
        pygame.draw.circle(self.screen, self.pupil_color, (x + 10, y + 5), 2)
        pygame.draw.circle(self.screen, self.pupil_color, (x + w - 10, y + 5), 2)

        # Legs
        leg_width = 6
        # Front legs
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + 2, y + h - 10, leg_width, 12))
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + w - 8, y + h - 10, leg_width, 12))
        # Back legs
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + 6, y + h - 8, leg_width + 2, 10))
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + w - 14, y + h - 8, leg_width + 2, 10))

    def _draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.font.render(f"Lives: {self.state.lives}", True, self.text_color)
        self.screen.blit(lives_text, (10, 45))

        # Instructions
        if not self.state.game_over and self.state.frog.pos.y > self.state.grid_size * 10:
            hint = self.small_font.render("Arrow keys to hop", True, (200, 200, 200))
            self.screen.blit(hint, (self.state.width - 150, 10))

    def _draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.state.width, self.state.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.state.win:
            msg = "GOAL REACHED!"
            submsg = f"Final Score: {self.state.score}"
            color = (100, 255, 100)
        else:
            msg = "GAME OVER"
            submsg = f"Final Score: {self.state.score}"
            color = (255, 100, 100)

        # Main message
        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(self.state.width // 2, self.state.height // 2 - 20))
        self.screen.blit(text, rect)

        # Score
        score_text = self.font.render(submsg, True, self.text_color)
        score_rect = score_text.get_rect(center=(self.state.width // 2, self.state.height // 2 + 20))
        self.screen.blit(score_text, score_rect)

        # Restart instruction
        restart_text = self.small_font.render("Press R to restart", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.state.width // 2, self.state.height // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
