"""Main game loop and rendering."""

import sys
import pygame
from pygame import locals
import config
from entities import GameState


class VolfiedGame:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Volfied Area Capture")
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = GameState()

        self.font_large = pygame.font.Font(None, config.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, config.FONT_SIZE_SMALL)

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == locals.K_ESCAPE:
                        running = False
                    self._handle_keydown(event)

            # Continuous key check for movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[locals.K_LEFT]:
                dx = -1
            elif keys[locals.K_RIGHT]:
                dx = 1
            elif keys[locals.K_UP]:
                dy = -1
            elif keys[locals.K_DOWN]:
                dy = 1

            if dx != 0 or dy != 0:
                self.state.player.set_direction(dx, dy)

            # Update game state
            self.state.update()

            # Render
            self._render()
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()

    def _handle_keydown(self, event) -> None:
        """Handle key press events."""
        if event.key == locals.K_r and (self.state.game_over or self.state.level_complete):
            if self.state.game_over:
                self.state.reset()
            else:
                self.state.next_level()

    def _render(self) -> None:
        """Render the game state."""
        self.screen.fill(config.BG_COLOR)

        self._draw_ui()
        self._draw_field()
        self._draw_claimed_areas()
        self._draw_boss()
        self._draw_sparks()
        self._draw_player()
        self._draw_game_over()
        self._draw_level_complete()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw UI elements."""
        title = self.font_medium.render("VECTOR VOLFIED", True, config.TEXT_COLOR)
        self.screen.blit(title, (20, 10))

        score_text = self.font_small.render(f"Score: {self.state.score}", True, config.TEXT_COLOR)
        self.screen.blit(score_text, (20, config.WINDOW_HEIGHT - 35))

        lives_text = self.font_small.render(f"Lives: {self.state.lives}", True, config.TEXT_COLOR)
        self.screen.blit(lives_text, (150, config.WINDOW_HEIGHT - 35))

        level_text = self.font_small.render(f"Level: {self.state.level}", True, config.TEXT_COLOR)
        self.screen.blit(level_text, (280, config.WINDOW_HEIGHT - 35))

        pct = self.state.get_claimed_percentage()
        pct_text = self.font_small.render(f"Claimed: {pct:.1f}% / {config.WIN_PERCENTAGE}%", True, config.TEXT_COLOR)
        self.screen.blit(pct_text, (config.WINDOW_WIDTH - 220, config.WINDOW_HEIGHT - 35))

        # Draw progress bar
        bar_width = 200
        bar_height = 15
        bar_x = config.WINDOW_WIDTH - 220
        bar_y = config.WINDOW_HEIGHT - 55

        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        fill_width = int(bar_width * min(pct / config.WIN_PERCENTAGE, 1.0))
        fill_color = config.FILL_COLOR if pct < config.WIN_PERCENTAGE else (0, 255, 0)
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

        pygame.draw.rect(self.screen, config.TEXT_COLOR, (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_field(self) -> None:
        """Draw the game field border."""
        rect = self.state.field_rect
        pygame.draw.rect(self.screen, config.FIELD_BG_COLOR, rect)
        pygame.draw.rect(self.screen, config.BORDER_COLOR, rect, 2)

    def _draw_claimed_areas(self) -> None:
        """Draw claimed/filled areas."""
        for region in self.state.claimed_regions[1:]:
            draw_rect = region.clip(self.state.field_rect)
            if draw_rect.width > 0 and draw_rect.height > 0:
                pygame.draw.rect(self.screen, config.CLAIMED_COLOR, draw_rect)
                pygame.draw.rect(self.screen, config.BORDER_COLOR, draw_rect, 1)

    def _draw_player(self) -> None:
        """Draw the player."""
        self.state.player.draw(self.screen)

    def _draw_boss(self) -> None:
        """Draw the Boss enemy."""
        self.state.boss.draw(self.screen)

    def _draw_sparks(self) -> None:
        """Draw the spark enemies."""
        for spark in self.state.sparks:
            spark.draw(self.screen)

    def _draw_game_over(self) -> None:
        """Draw game over screen."""
        if not self.state.game_over:
            return

        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, game_over_rect)

        final_score_text = self.font_medium.render(f"Final Score: {self.state.score}", True, config.TEXT_COLOR)
        score_rect = final_score_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(final_score_text, score_rect)

        restart_text = self.font_small.render("Press R to Restart", True, config.TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def _draw_level_complete(self) -> None:
        """Draw level complete screen."""
        if not self.state.level_complete or self.state.game_over:
            return

        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        level_text = self.font_large.render(f"LEVEL {self.state.level}!", True, (50, 255, 50))
        level_rect = level_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(level_text, level_rect)

        bonus_text = self.font_medium.render(f"+{config.LEVEL_COMPLETE_BONUS * self.state.level} Bonus!", True, config.TEXT_COLOR)
        bonus_rect = bonus_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(bonus_text, bonus_rect)

        next_text = self.font_small.render("Press R for Next Level", True, config.TEXT_COLOR)
        next_rect = next_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(next_text, next_rect)
