"""Main game logic for Vector Snake Grid Survival."""

import pygame
from config import *
from entities import Snake, Food


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Snake Grid Survival")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset the entire game state."""
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.speed = INITIAL_SPEED
        self.frame_count = 0

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

        self.food.update()
        self.frame_count += 1

        # Update snake at current speed
        if self.frame_count >= (FPS // self.speed):
            self.frame_count = 0

            # Move snake
            if not self.snake.update():
                self._game_over()
                return

            # Check food collision
            if self.snake.check_food_collision(self.food.position):
                self._eat_food()

    def _eat_food(self):
        """Handle food consumption."""
        self.score += SCORE_FOOD
        self.snake.grow()

        # Increase speed
        if self.speed < MAX_SPEED:
            self.speed = min(MAX_SPEED, self.speed + SPEED_INCREMENT)

        # Spawn new food
        self.food.spawn(self.snake.body)

    def _game_over(self):
        """Handle game over."""
        self.game_over = True
        self.score += PENALTY_DEATH

        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw grid
        self._draw_grid()

        # Draw game border
        border_rect = pygame.Rect(0, UI_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - UI_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_BORDER, border_rect, 2)

        # Draw food
        self.food.draw(self.screen)

        # Draw snake
        self.snake.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game over screen
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_grid(self):
        """Draw background grid."""
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, UI_HEIGHT), (x, SCREEN_HEIGHT), 1)

        for y in range(UI_HEIGHT, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_ui(self):
        """Draw user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, (25, 25, 30), ui_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Length
        length_text = self.font.render(f"Length: {self.snake.get_length()}", True, COLOR_TEXT)
        self.screen.blit(length_text, (20, 50))

        # Speed
        speed_text = self.small_font.render(f"Speed: {self.speed}", True, COLOR_TEXT_DIM)
        self.screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 25))

        # High score
        if self.high_score > 0:
            high_text = self.small_font.render(f"High: {self.high_score}", True, COLOR_TEXT_DIM)
            self.screen.blit(high_text, (SCREEN_WIDTH - high_text.get_width() - 20, 20))

        # Controls hint
        controls_text = self.small_font.render("Arrows/WASD to move", True, COLOR_TEXT_DIM)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 50))

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, COLOR_GAME_OVER)
        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        length_text = self.small_font.render(f"Snake Length: {self.snake.get_length()}", True, (200, 200, 200))
        restart_text = self.small_font.render("Press SPACE to restart", True, (200, 200, 200))
        quit_text = self.small_font.render("Press ESC to quit", True, (200, 200, 200))

        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80)
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30)
        )
        self.screen.blit(
            length_text,
            (SCREEN_WIDTH // 2 - length_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60)
        )
        self.screen.blit(
            quit_text,
            (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 90)
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
