"""Main game loop and rendering for Vector Tetris Grid Logic."""

import pygame
from config import *
from entities import GameState, Tetromino


class Game:
    """Main game class handling rendering and input."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Tetris Grid Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 36)

        self.game_state = GameState()

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_r:
                    self.game_state.reset()

                if event.key == pygame.K_p:
                    self.game_state.paused = not self.game_state.paused

                if not self.game_state.game_over and not self.game_state.paused:
                    if event.key == pygame.K_LEFT:
                        self.game_state.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.game_state.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.game_state.soft_drop()
                    elif event.key == pygame.K_UP or event.key == pygame.K_x:
                        self.game_state.rotate_piece(1)
                    elif event.key == pygame.K_z:
                        self.game_state.rotate_piece(-1)
                    elif event.key == pygame.K_SPACE:
                        self.game_state.hard_drop()
                    elif event.key == pygame.K_c or event.key == pygame.K_LSHIFT:
                        self.game_state.hold()

        return True

    def update(self, dt: int) -> None:
        """Update game state."""
        self.game_state.update(dt)

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(COLOR_BG)

        self._draw_ui()
        self._draw_grid()
        self._draw_ghost_piece()
        self._draw_current_piece()
        self._draw_next_piece()
        self._draw_hold_piece()

        if self.game_state.game_over:
            self._draw_game_over()
        elif self.game_state.paused:
            self._draw_paused()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw the user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect)
        pygame.draw.line(self.screen, COLOR_GRID_BORDER, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Title
        title_text = self.title_font.render("TETRIS", True, COLORS[0])
        self.screen.blit(title_text, (20, 25))

        # Score
        score_label = self.small_font.render("Score", True, COLOR_TEXT_DIM)
        score_value = self.font.render(f"{self.game_state.score:,}", True, COLOR_TEXT)
        self.screen.blit(score_label, (140, 10))
        self.screen.blit(score_value, (140, 32))

        # Lines
        lines_label = self.small_font.render("Lines", True, COLOR_TEXT_DIM)
        lines_value = self.font.render(f"{self.game_state.lines_cleared}", True, COLOR_TEXT)
        self.screen.blit(lines_label, (260, 10))
        self.screen.blit(lines_value, (260, 32))

        # Level
        level_label = self.small_font.render("Level", True, COLOR_TEXT_DIM)
        level_value = self.font.render(f"{self.game_state.level}", True, COLOR_TEXT)
        self.screen.blit(level_label, (360, 10))
        self.screen.blit(level_value, (360, 32))

    def _draw_grid(self) -> None:
        """Draw the game grid."""
        # Grid background
        grid_rect = pygame.Rect(
            GRID_OFFSET_X - 2,
            GRID_OFFSET_Y - 2,
            GRID_WIDTH * BLOCK_SIZE + 4,
            GRID_HEIGHT * BLOCK_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLOR_GRID_BG, grid_rect)
        pygame.draw.rect(self.screen, COLOR_GRID_BORDER, grid_rect, 2)

        # Draw locked blocks
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                x = GRID_OFFSET_X + col * BLOCK_SIZE
                y = GRID_OFFSET_Y + row * BLOCK_SIZE

                if self.game_state.grid[row][col] is not None:
                    self._draw_block(x, y, self.game_state.grid[row][col])
                else:
                    # Draw empty cell
                    cell_rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, COLOR_GRID_LINES, cell_rect, 1)

    def _draw_ghost_piece(self) -> None:
        """Draw the ghost piece at the landing position."""
        ghost_row = self.game_state.current_piece.get_ghost_position(self.game_state.grid)

        for r, c in self.game_state.current_piece.blocks:
            if 0 <= ghost_row + r < GRID_HEIGHT and 0 <= ghost_row + r < GRID_HEIGHT:
                x = GRID_OFFSET_X + (self.game_state.current_piece.col + c) * BLOCK_SIZE
                y = GRID_OFFSET_Y + (ghost_row + r) * BLOCK_SIZE
                self._draw_ghost_block(x, y)

    def _draw_current_piece(self) -> None:
        """Draw the currently falling piece."""
        color_idx = self.game_state.current_piece.color_index

        for r, c in self.game_state.current_piece.get_blocks():
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                x = GRID_OFFSET_X + c * BLOCK_SIZE
                y = GRID_OFFSET_Y + r * BLOCK_SIZE
                self._draw_block(x, y, color_idx)

    def _draw_next_piece(self) -> None:
        """Draw the next piece preview."""
        # Label
        next_label = self.small_font.render("Next", True, COLOR_TEXT_DIM)
        self.screen.blit(next_label, (PREVIEW_OFFSET_X, PREVIEW_OFFSET_Y - 25))

        # Background
        preview_rect = pygame.Rect(
            PREVIEW_OFFSET_X - 5,
            PREVIEW_OFFSET_Y - 5,
            5 * PREVIEW_BLOCK_SIZE + 10,
            4 * PREVIEW_BLOCK_SIZE + 10
        )
        pygame.draw.rect(self.screen, COLOR_GRID_BG, preview_rect)
        pygame.draw.rect(self.screen, COLOR_GRID_BORDER, preview_rect, 1)

        # Draw piece
        color_idx = self.game_state.next_piece.color_index
        for r, c in self.game_state.next_piece.blocks:
            x = PREVIEW_OFFSET_X + (c + 1) * PREVIEW_BLOCK_SIZE
            y = PREVIEW_OFFSET_Y + (r + 1) * PREVIEW_BLOCK_SIZE
            self._draw_small_block(x, y, color_idx)

    def _draw_hold_piece(self) -> None:
        """Draw the hold piece display."""
        hold_y = PREVIEW_OFFSET_Y + 140

        # Label
        hold_label = self.small_font.render("Hold", True, COLOR_TEXT_DIM)
        self.screen.blit(hold_label, (PREVIEW_OFFSET_X, hold_y - 25))

        # Background
        hold_rect = pygame.Rect(
            PREVIEW_OFFSET_X - 5,
            hold_y - 5,
            5 * PREVIEW_BLOCK_SIZE + 10,
            4 * PREVIEW_BLOCK_SIZE + 10
        )
        pygame.draw.rect(self.screen, COLOR_GRID_BG, hold_rect)
        pygame.draw.rect(self.screen, COLOR_GRID_BORDER, hold_rect, 1)

        if self.game_state.hold_piece is not None:
            color_idx = SHAPE_ORDER.index(self.game_state.hold_piece)
            piece = Tetromino(self.game_state.hold_piece)
            for r, c in piece.blocks:
                x = PREVIEW_OFFSET_X + (c + 1) * PREVIEW_BLOCK_SIZE
                y = hold_y + (r + 1) * PREVIEW_BLOCK_SIZE
                color = COLORS[color_idx] if self.game_state.can_hold else COLOR_GHOST
                self._draw_small_block(x, y, color_idx, color)

    def _draw_block(self, x: int, y: int, color_idx: int) -> None:
        """Draw a single block at grid position."""
        color = COLORS[color_idx]
        rect = pygame.Rect(x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)

        # Main block
        pygame.draw.rect(self.screen, color, rect)

        # Highlight
        highlight = pygame.Rect(x + 3, y + 3, BLOCK_SIZE - 6, 3)
        highlight_color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
        pygame.draw.rect(self.screen, highlight_color, highlight)

        # Shadow
        shadow = pygame.Rect(x + 3, y + BLOCK_SIZE - 6, BLOCK_SIZE - 6, 3)
        shadow_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        pygame.draw.rect(self.screen, shadow_color, shadow)

        # Border
        pygame.draw.rect(self.screen, (30, 30, 35), rect, 1)

    def _draw_ghost_block(self, x: int, y: int) -> None:
        """Draw a ghost block outline."""
        rect = pygame.Rect(x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
        pygame.draw.rect(self.screen, COLOR_GHOST, rect, 2)

    def _draw_small_block(self, x: int, y: int, color_idx: int, override_color=None) -> None:
        """Draw a small preview block."""
        color = override_color if override_color else COLORS[color_idx]
        rect = pygame.Rect(x, y, PREVIEW_BLOCK_SIZE - 1, PREVIEW_BLOCK_SIZE - 1)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (30, 30, 35), rect, 1)

    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("GAME OVER", True, (220, 80, 80))
        score_text = self.font.render(f"Final Score: {self.game_state.score:,}", True, COLOR_TEXT)
        lines_text = self.font.render(f"Lines Cleared: {self.game_state.lines_cleared}", True, COLOR_TEXT)
        restart_text = self.small_font.render("Press R to play again", True, COLOR_TEXT_DIM)
        quit_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 80))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y - 20))
        self.screen.blit(lines_text, (center_x - lines_text.get_width() // 2, center_y + 15))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 60))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 90))

    def _draw_paused(self) -> None:
        """Draw paused overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("PAUSED", True, COLOR_TEXT)
        continue_text = self.small_font.render("Press P to continue", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 20))
        self.screen.blit(continue_text, (center_x - continue_text.get_width() // 2, center_y + 30))

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()
