"""Main game loop and rendering."""

import pygame
import sys
from config import *
from entities import *


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros - Infinite Slide")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = GameState()

    def run(self) -> None:
        """Main game loop."""
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self) -> None:
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.state.handle_jump()
                elif event.key == pygame.K_r and self.state.game_over:
                    self.state.reset()

    def _update(self) -> None:
        """Update game state."""
        keys = pygame.key.get_pressed()
        input_keys = (keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_SPACE])
        self.state.update(input_keys)

    def _draw(self) -> None:
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        # Draw background
        self._draw_background()

        # Calculate camera offset
        camera_x = self.state.scroll_x

        # Draw platforms
        for platform in self.state.level_gen.platforms:
            platform.draw(self.screen)

        # Draw spikes
        for spike in self.state.level_gen.spikes:
            spike.draw(self.screen)

        # Draw coins
        for coin in self.state.level_gen.coins:
            coin.draw(self.screen)

        # Draw player (with camera offset)
        player_screen_x = int(self.state.player.x - camera_x)
        player_screen_y = int(self.state.player.y)
        self._draw_player_at(player_screen_x, player_screen_y)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_background(self) -> None:
        """Draw background elements."""
        # Distance grid lines
        for x in range(0, int(self.state.scroll_x) + SCREEN_WIDTH, 100):
            screen_x = int(x - self.state.scroll_x)
            if -50 < screen_x < SCREEN_WIDTH + 50:
                pygame.draw.line(self.screen, (25, 35, 55), (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)

        # Horizontal depth lines
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (25, 35, 55), (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_player_at(self, screen_x: int, screen_y: int) -> None:
        """Draw player at screen position."""
        # Body with rounded corners
        pygame.draw.rect(self.screen, COLOR_PLAYER, (screen_x, screen_y, self.state.player.width, self.state.player.height), border_radius=4)

        # Eye (indicates facing direction)
        eye_x = screen_x + (20 if self.state.player.vx >= 0 else 4)
        pygame.draw.circle(self.screen, COLOR_PLAYER_EYE, (eye_x, screen_y + 12), 5)
        pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, screen_y + 12), 2)

        # Subtle highlight for icy feel
        highlight_x = screen_x + 5 if self.state.player.vx >= 0 else screen_x + self.state.player.width - 10
        pygame.draw.line(self.screen, (255, 150, 150), (highlight_x, screen_y + 5), (highlight_x, screen_y + 15), 2)

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # Distance and score
        dist_text = self.font.render(f"Distance: {int(self.state.player.distance_traveled)}m", True, COLOR_TEXT)
        coin_text = self.font.render(f"Coins: {self.state.player.coins_collected}", True, COLOR_COIN)
        speed_text = self.small_font.render(f"Scroll Speed: {self.state.scroll_speed:.1f}", True, (180, 180, 180))

        self.screen.blit(dist_text, (10, 10))
        self.screen.blit(coin_text, (10, 45))
        self.screen.blit(speed_text, (10, 80))

        # Danger zone indicator
        danger_x = int(DANGER_ZONE_WIDTH)
        if danger_x > 0:
            danger_surface = pygame.Surface((danger_x, SCREEN_HEIGHT), pygame.SRCALPHA)
            danger_surface.fill((255, 100, 100, 30))
            self.screen.blit(danger_surface, (0, 0))
            pygame.draw.line(self.screen, COLOR_SCROLL_LINE, (danger_x, 0), (danger_x, SCREEN_HEIGHT), 2)

        # Start screen
        if self.state.waiting_start:
            self._draw_overlay("INFINITE SLIDE", "Master the icy momentum!", "Press SPACE to start", "LEFT/RIGHT: Apply force | SPACE: Jump")

        # Game over
        elif self.state.game_over:
            score = int(self.state.player.distance_traveled) + self.state.player.coins_collected * POINTS_PER_COIN
            subtitle = f"You fell! Distance: {int(self.state.player.distance_traveled)}m"
            self._draw_overlay("GAME OVER", subtitle, f"Score: {score} (Coins: {self.state.player.coins_collected}) | Press R to retry")

    def _draw_overlay(self, title: str, subtitle: str, info: str, controls: str = "") -> None:
        """Draw overlay screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font.render(title, True, (255, 200, 100))
        subtitle_surf = self.small_font.render(subtitle, True, COLOR_TEXT)
        info_surf = self.small_font.render(info, True, (180, 180, 180))

        y_offset = SCREEN_HEIGHT // 2 - 50
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, y_offset))
        self.screen.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, y_offset + 45))
        self.screen.blit(info_surf, (SCREEN_WIDTH // 2 - info_surf.get_width() // 2, y_offset + 80))

        if controls:
            controls_surf = self.small_font.render(controls, True, (150, 150, 150))
            self.screen.blit(controls_surf, (SCREEN_WIDTH // 2 - controls_surf.get_width() // 2, y_offset + 120))
