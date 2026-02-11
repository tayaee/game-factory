import pygame
import sys
from config import *
from player import Player
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Super Mario Bros Jump and Dash Pro")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)

        self.reset_game()

    def reset_game(self):
        self.level = Level()
        start_platform = self.level.platforms[0]
        self.player = Player(
            start_platform.x + 50,
            start_platform.y - PLAYER_HEIGHT
        )
        self.camera_x = 0
        self.score = 0
        self.game_over = False
        self.victory = False
        self.visited_platforms = set()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over or self.victory:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.player.start_jump()
                    if event.key == pygame.K_z:
                        direction = 1 if self.player.facing_right else -1
                        # Dash in movement direction or facing direction
                        if keys[pygame.K_LEFT]:
                            direction = -1
                        elif keys[pygame.K_RIGHT]:
                            direction = 1
                        self.player.dash(direction)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.release_jump()

        # Continuous input
        if not self.game_over and not self.victory:
            self.player.update(keys, self.level.platforms)

        return True

    def check_collisions(self):
        if self.game_over or self.victory:
            return

        player_rect = self.player.get_rect()

        # Check spike collisions
        for platform in self.level.platforms:
            if platform.has_spike:
                spike_rect = pygame.Rect(platform.x, platform.y - 15, platform.width, 15)
                if player_rect.colliderect(spike_rect):
                    self.die()
                    return

            # Coin collection
            coins_collected = platform.collect_coins(player_rect)
            self.score += coins_collected * SCORE_PER_COIN

            # Score for visiting new platforms
            if player_rect.colliderect(platform.rect) and id(platform) not in self.visited_platforms:
                self.visited_platforms.add(id(platform))
                self.score += SCORE_PER_PLATFORM

                # Check checkpoint
                for checkpoint_x, checkpoint_y in self.level.checkpoints:
                    if abs(platform.x - checkpoint_x) < 50:
                        self.player.set_checkpoint(platform.x + 50, platform.y - PLAYER_HEIGHT)

        # Check victory
        if self.player.x >= self.level.goal_x:
            self.victory = True

        # Check fall death
        if self.player.is_off_screen(self.camera_x):
            self.die()

    def die(self):
        self.score += DEATH_PENALTY
        if self.score < 0:
            self.score = 0
        self.player.reset()
        self.camera_x = max(0, self.player.start_x - SCREEN_WIDTH // 3)
        self.visited_platforms.clear()

    def update_camera(self):
        target_x = self.player.x - SCREEN_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_x = max(0, self.camera_x)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw level
        self.level.draw(self.screen, self.camera_x)

        # Draw player
        self.player.draw(self.screen, self.camera_x)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

        # Dash gauge
        dash_bar_width = 150
        dash_bar_height = 16
        dash_bar_x = SCREEN_WIDTH - dash_bar_width - 10
        dash_bar_y = 10

        # Dash bar background
        pygame.draw.rect(
            self.screen,
            DASH_BAR_EMPTY_COLOR,
            (dash_bar_x, dash_bar_y, dash_bar_width, dash_bar_height),
            border_radius=4
        )

        # Dash bar fill
        charge_width = (self.player.dash_charges / MAX_DASH_CHARGES) * dash_bar_width
        if charge_width > 0:
            pygame.draw.rect(
                self.screen,
                DASH_BAR_COLOR,
                (dash_bar_x, dash_bar_y, charge_width, dash_bar_height),
                border_radius=4
            )

        # Dash charges text
        dash_text = self.font.render(f"DASH: {self.player.dash_charges}/{MAX_DASH_CHARGES}", True, TEXT_COLOR)
        self.screen.blit(dash_text, (dash_bar_x, dash_bar_y + 20))

        # Controls hint
        controls_text = self.font.render("ARROWS: Move | SPACE: Jump | Z: Dash", True, (150, 150, 150))
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.font.render("Press SPACE to restart", True, TEXT_COLOR)

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        # Victory screen
        if self.victory:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            victory_text = self.large_font.render("VICTORY!", True, GOAL_COLOR)
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.font.render("Press SPACE to play again", True, TEXT_COLOR)

            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def run(self):
        running = True
        while running:
            running = self.handle_input()

            if not self.game_over and not self.victory:
                self.level.update()
                self.check_collisions()
                self.update_camera()

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
