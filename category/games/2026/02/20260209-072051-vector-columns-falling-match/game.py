"""Main game logic and rendering for Vector Columns Falling Match."""

import pygame
import sys
from entities import GameState, FallingColumn
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, GRID_COLS, GRID_ROWS,
    CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, BLACK, WHITE,
    GRID_BG, GRID_BORDER, GEM_COLORS, GEM_BORDER, EMPTY,
    INITIAL_FALL_DELAY, SOFT_DROP_DELAY, LOCK_DELAY
)


class Game:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Columns: Falling Match")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)

        self.state = GameState()
        self.last_fall_time = pygame.time.get_ticks()
        self.last_lock_time = 0
        self.lock_in_progress = False

    def run(self) -> None:
        """Main game loop."""
        while True:
            self._handle_events()
            if not self.state.paused and not self.state.game_over:
                self._update()
            self._render()
            self.clock.tick(FPS)

    def _handle_events(self) -> None:
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self.state.game_over:
                    if event.key == pygame.K_r:
                        self.state.reset()
                        self.last_fall_time = pygame.time.get_ticks()
                        self.lock_in_progress = False
                elif event.key == pygame.K_p:
                    self.state.paused = not self.state.paused
                elif not self.state.paused:
                    self._handle_game_input(event)

    def _handle_game_input(self, event: pygame.event.Event) -> None:
        """Handle input during active gameplay."""
        column = self.state.falling_column

        if event.key == pygame.K_LEFT:
            if column and self.state.is_valid_position(column.col - 1,
                                                       column.row - 2):
                column.move_left()
                self.lock_in_progress = False

        elif event.key == pygame.K_RIGHT:
            if column and self.state.is_valid_position(column.col + 1,
                                                       column.row - 2):
                column.move_right()
                self.lock_in_progress = False

        elif event.key == pygame.K_UP:
            if column:
                column.cycle()
                self.lock_in_progress = False

        elif event.key == pygame.K_DOWN:
            if column and self.state.is_valid_position(column.col,
                                                       column.row - 1):
                column.row += 1

        elif event.key == pygame.K_SPACE:
            self._hard_drop()

        elif event.key == pygame.K_r:
            self.state.reset()
            self.last_fall_time = pygame.time.get_ticks()
            self.lock_in_progress = False

    def _hard_drop(self) -> None:
        """Instantly drop the column to the bottom."""
        column = self.state.falling_column
        if not column:
            return

        while self.state.is_valid_position(column.col, column.row - 1):
            column.row += 1

        self.state.lock_column()
        if not self.state.game_over:
            self.state.spawn_new_column()
        self.last_fall_time = pygame.time.get_ticks()
        self.lock_in_progress = False

    def _update(self) -> None:
        """Update game state."""
        current_time = pygame.time.get_ticks()

        column = self.state.falling_column
        if not column:
            return

        # Check if column should lock
        if not self.state.is_valid_position(column.col, column.row - 1):
            if not self.lock_in_progress:
                self.lock_in_progress = True
                self.last_lock_time = current_time

            # Check if lock delay has passed
            if current_time - self.last_lock_time >= LOCK_DELAY:
                self.state.lock_column()
                if not self.state.game_over:
                    self.state.spawn_new_column()
                self.last_fall_time = current_time
                self.lock_in_progress = False
        else:
            # Normal falling
            fall_delay = self.state.fall_delay
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                fall_delay = SOFT_DROP_DELAY

            if current_time - self.last_fall_time >= fall_delay:
                column.row += 1
                self.last_fall_time = current_time

    def _render(self) -> None:
        """Render the game."""
        self.screen.fill(BLACK)

        self._draw_grid()
        self._draw_falling_column()
        self._draw_ui()

        if self.state.paused:
            self._draw_pause_screen()

        if self.state.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_grid(self) -> None:
        """Draw the game grid."""
        # Draw grid background
        grid_rect = pygame.Rect(
            GRID_OFFSET_X - 5,
            GRID_OFFSET_Y - 5,
            GRID_COLS * CELL_SIZE + 10,
            GRID_ROWS * CELL_SIZE + 10
        )
        pygame.draw.rect(self.screen, GRID_BORDER, grid_rect)

        grid_rect = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            GRID_COLS * CELL_SIZE,
            GRID_ROWS * CELL_SIZE
        )
        pygame.draw.rect(self.screen, GRID_BG, grid_rect)

        # Draw cells
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                gem = self.state.grid[col][row]
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE

                if gem != EMPTY:
                    self._draw_gem(x, y, gem)
                else:
                    pygame.draw.rect(self.screen, (40, 40, 55),
                                   (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    def _draw_gem(self, x: int, y: int, gem_type: int) -> None:
        """Draw a gem at the specified position."""
        color = GEM_COLORS[gem_type - 1]
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 4

        # Draw gem body
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, GEM_BORDER, (center_x, center_y), radius, 2)

        # Draw highlight
        highlight_pos = (center_x - radius // 3, center_y - radius // 3)
        highlight_radius = radius // 4
        highlight_color = (min(color[0] + 80, 255), min(color[1] + 80, 255),
                          min(color[2] + 80, 255))
        pygame.draw.circle(self.screen, highlight_color, highlight_pos, highlight_radius)

    def _draw_falling_column(self) -> None:
        """Draw the falling column."""
        column = self.state.falling_column
        if not column:
            return

        for i, gem in enumerate(column.gems):
            draw_row = column.row - 2 + i
            if -2 <= draw_row < GRID_ROWS + 2:
                x = GRID_OFFSET_X + column.col * CELL_SIZE
                y = GRID_OFFSET_Y + draw_row * CELL_SIZE

                # Only draw if within grid bounds
                if 0 <= draw_row < GRID_ROWS:
                    self._draw_gem(x, y, gem)
                elif draw_row < 0:
                    # Draw above grid with transparency effect
                    temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    color = GEM_COLORS[gem - 1]
                    center = CELL_SIZE // 2
                    radius = CELL_SIZE // 2 - 4
                    pygame.draw.circle(temp_surface, (*color, 150),
                                     (center, center), radius)
                    self.screen.blit(temp_surface, (x, y))

    def _draw_ui(self) -> None:
        """Draw the UI elements."""
        # Title
        title = self.title_font.render("COLUMNS", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 10))

        # Score
        score_text = self.font.render(f"SCORE: {self.state.score}", True, WHITE)
        self.screen.blit(score_text, (20, GRID_OFFSET_Y))

        # Level
        level_text = self.font.render(f"LEVEL: {self.state.level}", True, WHITE)
        self.screen.blit(level_text, (20, GRID_OFFSET_Y + 35))

        # Gems cleared
        cleared_text = self.font.render(f"GEMS: {self.state.gems_cleared}", True, WHITE)
        self.screen.blit(cleared_text, (20, GRID_OFFSET_Y + 70))

        # Chain indicator
        if self.state.chain_count > 0:
            chain_text = self.font.render(f"CHAIN: x{self.state.chain_count}", True,
                                         (255, 200, 50))
            self.screen.blit(chain_text, (20, GRID_OFFSET_Y + 105))

        # Controls hint
        hint_y = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE + 20
        hints = [
            "ARROWS: Move/Cycle",
            "DOWN: Soft drop",
            "SPACE: Hard drop",
            "P: Pause | R: Reset",
            "ESC: Quit"
        ]
        for i, hint in enumerate(hints):
            hint_text = pygame.font.Font(None, 20).render(hint, True, (150, 150, 170))
            self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2,
                                        hint_y + i * 22))

    def _draw_pause_screen(self) -> None:
        """Draw the pause overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.large_font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2,
                                      WINDOW_HEIGHT // 2 - 20))

        resume_text = self.font.render("Press P to resume", True, (200, 200, 220))
        self.screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2,
                                       WINDOW_HEIGHT // 2 + 30))

    def _draw_game_over(self) -> None:
        """Draw the game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
                                          WINDOW_HEIGHT // 2 - 50))

        final_score_text = self.title_font.render(f"Final Score: {self.state.score}",
                                                  True, WHITE)
        self.screen.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2,
                                            WINDOW_HEIGHT // 2))

        restart_text = self.font.render("Press R to restart or ESC to quit", True,
                                       (200, 200, 220))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2,
                                        WINDOW_HEIGHT // 2 + 50))
