"""Game loop and rendering."""

import pygame
import sys
import random
from config import *
from entities import Player, Paratroopa


class Game:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, GROUND_Y - PLAYER_HEIGHT)
        self.paratroopas = []
        self.score = 0
        self.combo = 0
        self.game_over = False
        self.spawn_timer = 0
        self.difficulty_timer = 0
        self.max_paratroopas = 5

    def spawn_paratroopa(self):
        """Spawn a new paratroopa at the top of the screen."""
        x = random.randint(50, SCREEN_WIDTH - PARATROOPA_WIDTH - 50)
        y = -PARATROOPA_HEIGHT
        self.paratroopas.append(Paratroopa(x, y))

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Spawn paratroopas
        self.spawn_timer += 1
        if self.spawn_timer >= SPAWN_RATE:
            self.spawn_timer = 0
            if len(self.paratroopas) < self.max_paratroopas:
                self.spawn_paratroopa()

        # Increase difficulty over time
        self.difficulty_timer += 1
        if self.difficulty_timer >= 600:  # Every 10 seconds
            self.difficulty_timer = 0
            self.max_paratroopas = min(15, self.max_paratroopas + 1)

        # Update paratroopas
        for paratroopa in self.paratroopas[:]:
            paratroopa.update()

            # Remove if fallen off screen
            if paratroopa.y > SCREEN_HEIGHT + 50:
                self.paratroopas.remove(paratroopa)
                # Reset combo if enemy passes without being stomped
                if self.player.on_ground:
                    self.combo = 0
                continue

            # Check collision with player
            player_rect = self.player.get_hitbox()
            paratroopa_rect = paratroopa.get_hitbox()

            if player_rect.colliderect(paratroopa_rect):
                # Check if player stomped the top
                stomp_zone = self.player.get_stomp_zone()
                stomp_hitbox = paratroopa.get_stomp_hitbox()

                if stomp_zone.colliderect(stomp_hitbox) and self.player.vel_y > 0:
                    # Successful stomp
                    self.player.bounce()
                    self.paratroopas.remove(paratroopa)

                    # Score with combo
                    self.combo += 1
                    combo_multiplier = 2 ** (self.combo - 1)
                    points = SCORE_PER_STOMP * combo_multiplier
                    self.score += points
                else:
                    # Player hit the side or bottom - game over
                    self.player.alive = False
                    self.game_over = True

        # Check if player fell off bottom
        if not self.player.alive:
            self.game_over = True

        # Reset combo when touching ground
        if self.player.on_ground and self.combo > 0:
            self.combo = 0

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw clouds
        for i in range(8):
            cloud_x = (i * 120 + pygame.time.get_ticks() // 50) % (SCREEN_WIDTH + 100) - 50
            cloud_y = 50 + (i % 3) * 40
            pygame.draw.ellipse(self.screen, (200, 220, 240), (cloud_x, cloud_y, 60, 30))

        # Draw ground
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, (80, 60, 40), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

        # Draw paratroopas
        for paratroopa in self.paratroopas:
            paratroopa.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Game over overlay
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display."""
        # Score background
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (10, 10, 200, 80))
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 10, 200, 80), 2)

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Combo
        if self.combo > 0:
            combo_text = self.small_font.render(f"Combo: x{2 ** (self.combo - 1)}", True, COLOR_COMBO)
            self.screen.blit(combo_text, (20, 50))

            # Combo count
            count_text = self.tiny_font.render(f"({self.combo} stomps)", True, COLOR_COMBO)
            self.screen.blit(count_text, (130, 55))

        # Controls hint
        if not self.player.has_jumped_once and not self.game_over:
            hints = [
                "LEFT/RIGHT: Move",
                "SPACE: Jump & Stomp",
                "Stomp enemies to bounce!"
            ]
            for i, hint in enumerate(hints):
                hint_text = self.tiny_font.render(hint, True, (255, 255, 0))
                self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10 + i * 22))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80)
        )

        # Final score
        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20)
        )

        # Max combo
        max_combo = 2 ** (self.combo - 1) if self.combo > 0 else 0
        combo_text = self.small_font.render(f"Max Combo: x{max_combo}", True, COLOR_COMBO)
        self.screen.blit(
            combo_text,
            (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20)
        )

        # Restart prompt
        restart_text = self.small_font.render("Press SPACE to play again", True, COLOR_TEXT)
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70)
        )

        # Quit prompt
        quit_text = self.tiny_font.render("Press ESC to quit", True, (150, 150, 150))
        self.screen.blit(
            quit_text,
            (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 105)
        )

    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        # Restart game
                        self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def get_state(self):
        """Return current game state for AI agents."""
        nearest_paratroopa = None
        min_dist = float('inf')

        for p in self.paratroopas:
            dist = ((p.x - self.player.x) ** 2 + (p.y - self.player.y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_paratroopa = p

        return {
            'player': {
                'x': self.player.x / SCREEN_WIDTH,
                'y': self.player.y / SCREEN_HEIGHT,
                'vx': self.player.vel_x / MOVE_SPEED,
                'vy': self.player.vel_y / MAX_FALL_SPEED,
                'on_ground': self.player.on_ground,
                'has_jumped': self.player.has_jumped_once
            },
            'nearest_paratroopa': {
                'x': nearest_paratroopa.x / SCREEN_WIDTH if nearest_paratroopa else 0.5,
                'y': nearest_paratroopa.y / SCREEN_HEIGHT if nearest_paratroopa else 0.0,
                'distance': min_dist / SCREEN_HEIGHT if nearest_paratroopa else 1.0,
                'direction': nearest_paratroopa.direction if nearest_paratroopa else 1
            } if nearest_paratroopa else None,
            'paratroopa_count': len(self.paratroopas),
            'combo': self.combo,
            'score': self.score
        }
