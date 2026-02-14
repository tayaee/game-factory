"""Main game logic for Vector Snake Rattle Coin Dash."""

import pygame
from config import *
from entities import Snake, Coin


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Snake Rattle Coin Dash")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

        self.reset_game()

    def reset_game(self):
        """Reset the entire game state."""
        self.snake = Snake()
        self.coin = Coin()
        self.coin.spawn(self.snake.body)
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.speed = INITIAL_SPEED
        self.frame_count = 0
        self.coins_collected = 0

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.set_direction(DIR_UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.set_direction(DIR_DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.set_direction(DIR_LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.set_direction(DIR_RIGHT)

        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        self.coin.update()
        self.frame_count += 1

        # Update snake at current speed
        if self.frame_count >= (FPS // self.speed):
            self.frame_count = 0

            # Move snake
            if not self.snake.update():
                self._game_over()
                return

            # Check coin collision
            if self.snake.check_coin_collision(self.coin.position):
                self._collect_coin()

    def _collect_coin(self):
        """Handle coin collection."""
        self.score += SCORE_COIN
        self.snake.grow()
        self.coins_collected += 1

        # Increase speed every 5 coins
        if self.coins_collected % 5 == 0 and self.speed < MAX_SPEED:
            self.speed = min(MAX_SPEED, self.speed + SPEED_INCREMENT)

        # Spawn new coin
        self.coin.spawn(self.snake.body)

    def _game_over(self):
        """Handle game over."""
        self.game_over = True
        self.score += PENALTY_DEATH

        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw isometric grid
        self._draw_isometric_grid()

        # Draw coin
        self.coin.draw(self.screen)

        # Draw snake
        self.snake.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game over screen
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_isometric_grid(self):
        """Draw the isometric grid."""
        # Draw the grid as diamonds
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                screen_x, screen_y = grid_to_screen(x, y)

                # Determine if this cell is on the edge
                is_top_edge = y == 0
                is_bottom_edge = y == GRID_SIZE - 1
                is_left_edge = x == GRID_SIZE - 1
                is_right_edge = x == 0

                # Draw grid cell (lighter outline)
                half_size = CELL_SIZE // 2
                points = [
                    (screen_x, screen_y - half_size),
                    (screen_x + half_size, screen_y),
                    (screen_x, screen_y + half_size),
                    (screen_x - half_size, screen_y),
                ]

                # Fill with very dark gray
                if is_top_edge or is_bottom_edge or is_left_edge or is_right_edge:
                    pygame.draw.polygon(self.screen, (30, 30, 30), points)

                # Draw grid lines
                color = (60, 60, 60) if not (is_top_edge or is_bottom_edge or is_left_edge or is_right_edge) else (100, 100, 100)
                width = 2 if (is_top_edge or is_bottom_edge or is_left_edge or is_right_edge) else 1
                pygame.draw.polygon(self.screen, color, points, width)

    def _draw_ui(self):
        """Draw user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, (10, 10, 10), ui_rect)
        pygame.draw.line(self.screen, COLOR_GRID_LINES, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Title
        title_text = self.small_font.render("SNAKE RATTLE COIN DASH", True, COLOR_TEXT_DIM)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 30))

        # Coins collected
        coins_text = self.small_font.render(f"Coins: {self.coins_collected}", True, COLOR_COIN)
        self.screen.blit(coins_text, (20, 5))

        # Length
        length_text = self.small_font.render(f"Length: {self.snake.get_length()}", True, COLOR_TEXT_DIM)
        self.screen.blit(length_text, (160, 8))

        # Speed
        speed_text = self.small_font.render(f"Speed: {self.speed}", True, COLOR_TEXT_DIM)
        self.screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 35))

        # High score
        if self.high_score > 0:
            high_text = self.small_font.render(f"High: {self.high_score}", True, COLOR_TEXT_DIM)
            self.screen.blit(high_text, (SCREEN_WIDTH - high_text.get_width() - 20, 8))

        # Controls hint
        controls_text = self.small_font.render("Arrows/WASD to move", True, COLOR_TEXT_DIM)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 35))

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.title_font.render("GAME OVER", True, COLOR_GAME_OVER)
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        coins_text = self.small_font.render(f"Coins Collected: {self.coins_collected}", True, COLOR_COIN)
        length_text = self.small_font.render(f"Snake Length: {self.snake.get_length()}", True, (200, 200, 200))
        restart_text = self.small_font.render("Press SPACE to restart", True, (200, 200, 200))
        quit_text = self.small_font.render("Press ESC to quit", True, (200, 200, 200))

        y_offset = SCREEN_HEIGHT // 2 - 100

        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, y_offset)
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset + 50)
        )
        self.screen.blit(
            coins_text,
            (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, y_offset + 90)
        )
        self.screen.blit(
            length_text,
            (SCREEN_WIDTH // 2 - length_text.get_width() // 2, y_offset + 115)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset + 160)
        )
        self.screen.blit(
            quit_text,
            (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, y_offset + 190)
        )

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
