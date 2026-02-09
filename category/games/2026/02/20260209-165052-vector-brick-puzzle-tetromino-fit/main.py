"""
Vector Brick Puzzle: Tetromino Fit
A 10x10 grid puzzle game where players place tetromino pieces to clear lines.
"""

import pygame
import random
import sys
from typing import List, Tuple, Optional, Set

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 10
CELL_SIZE = 40
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 80

TRAY_Y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE + 60
TRAY_CELL_SIZE = 25

# Window dimensions
WINDOW_WIDTH = GRID_OFFSET_X * 2 + GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = TRAY_Y + TRAY_CELL_SIZE * 4 + 60

# Colors
COLORS = {
    "background": (18, 18, 18),
    "grid_line": (51, 51, 51),
    "grid_cell": (30, 30, 30),
    "block_active": (0, 173, 181),
    "block_preview": (0, 173, 181, 128),
    "block_invalid": (255, 80, 80, 128),
    "text": (238, 238, 238),
    "score_bg": (40, 40, 40),
    "game_over": (255, 50, 50),
}

# Tetromino shapes (relative coordinates)
TETROMINOES = {
    "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}

# Extended shapes for variety
EXTENDED_SHAPES = {
    "I5": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    "L5": [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
    "plus": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    "corner": [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
    "square3": [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)],
    "small_L": [(0, 0), (0, 1), (1, 1)],
    "dot": [(0, 0)],
    "line2": [(0, 0), (1, 0)],
    "line3": [(0, 0), (1, 0), (2, 0)],
}

ALL_SHAPES = {**TETROMINOES, **EXTENDED_SHAPES}
SHAPE_NAMES = list(ALL_SHAPES.keys())


class Piece:
    """Represents a tetromino piece."""

    def __init__(self, shape_name: str):
        self.shape_name = shape_name
        self.cells = ALL_SHAPES[shape_name].copy()
        self.color = COLORS["block_active"]

    def get_bounds(self) -> Tuple[int, int]:
        """Get width and height of the piece."""
        if not self.cells:
            return 0, 0
        max_x = max(c[0] for c in self.cells) + 1
        max_y = max(c[1] for c in self.cells) + 1
        return max_x, max_y

    def can_place(self, grid: List[List[bool]], grid_x: int, grid_y: int) -> bool:
        """Check if piece can be placed at grid position."""
        for dx, dy in self.cells:
            x, y = grid_x + dx, grid_y + dy
            if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
                return False
            if grid[y][x]:
                return False
        return True

    def place(self, grid: List[List[bool]], grid_x: int, grid_y: int) -> None:
        """Place piece on grid."""
        for dx, dy in self.cells:
            x, y = grid_x + dx, grid_y + dy
            grid[y][x] = True

    def get_block_count(self) -> int:
        """Return number of blocks in piece."""
        return len(self.cells)


class Game:
    """Main game class."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Brick Puzzle: Tetromino Fit")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game state."""
        self.grid: List[List[bool]] = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.pieces: List[Optional[Piece]] = []
        self.dragging_piece: Optional[int] = None
        self.drag_offset = (0, 0)
        self.game_over = False

        self.generate_new_pieces()

    def generate_new_pieces(self) -> None:
        """Generate three new random pieces."""
        self.pieces = [Piece(random.choice(SHAPE_NAMES)) for _ in range(3)]

    def get_tray_position(self, index: int) -> Tuple[int, int]:
        """Get the x, y position for a piece in the tray."""
        tray_width = WINDOW_WIDTH - GRID_OFFSET_X * 2
        slot_width = tray_width // 3
        x = GRID_OFFSET_X + slot_width * index + slot_width // 2
        y = TRAY_Y + TRAY_CELL_SIZE * 2
        return x, y

    def get_piece_rect(self, index: int) -> pygame.Rect:
        """Get bounding rectangle for a piece in tray."""
        if self.pieces[index] is None:
            return pygame.Rect(0, 0, 0, 0)

        piece = self.pieces[index]
        width, height = piece.get_bounds()
        x, y = self.get_tray_position(index)

        return pygame.Rect(
            x - TRAY_CELL_SIZE,
            y - TRAY_CELL_SIZE,
            width * TRAY_CELL_SIZE + TRAY_CELL_SIZE,
            height * TRAY_CELL_SIZE + TRAY_CELL_SIZE
        )

    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates."""
        grid_x = (screen_x - GRID_OFFSET_X) // CELL_SIZE
        grid_y = (screen_y - GRID_OFFSET_Y) // CELL_SIZE
        return grid_x, grid_y

    def check_lines(self) -> int:
        """Check and clear complete lines. Returns number of lines cleared."""
        lines_cleared = 0
        rows_to_clear = []
        cols_to_clear = []

        # Check rows
        for y in range(GRID_SIZE):
            if all(self.grid[y][x] for x in range(GRID_SIZE)):
                rows_to_clear.append(y)

        # Check columns
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] for y in range(GRID_SIZE)):
                cols_to_clear.append(x)

        # Clear rows
        for y in rows_to_clear:
            for x in range(GRID_SIZE):
                self.grid[y][x] = False
            lines_cleared += 1

        # Clear columns
        for x in cols_to_clear:
            for y in range(GRID_SIZE):
                self.grid[y][x] = False
            lines_cleared += 1

        return lines_cleared

    def can_place_any_piece(self) -> bool:
        """Check if any piece can be placed anywhere on grid."""
        for piece in self.pieces:
            if piece is None:
                continue
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if piece.can_place(self.grid, x, y):
                        return True
        return False

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click."""
        if self.game_over:
            # Check for restart button
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 60,
                WINDOW_HEIGHT // 2 + 40,
                120, 40
            )
            if button_rect.collidepoint(pos):
                self.reset_game()
            return

        # Check if clicking on a piece in tray
        for i, piece in enumerate(self.pieces):
            if piece is None:
                continue
            rect = self.get_piece_rect(i)
            if rect.collidepoint(pos):
                self.dragging_piece = i
                self.drag_offset = (
                    pos[0] - rect.centerx,
                    pos[1] - rect.centery
                )
                break

    def handle_release(self, pos: Tuple[int, int]) -> None:
        """Handle mouse release."""
        if self.dragging_piece is None:
            return

        piece = self.pieces[self.dragging_piece]
        if piece is None:
            self.dragging_piece = None
            return

        # Calculate grid position for top-left of piece
        grid_x, grid_y = self.screen_to_grid(pos[0], pos[1])

        # Adjust for drag offset and piece center
        width, height = piece.get_bounds()
        grid_x -= width // 2
        grid_y -= height // 2

        if piece.can_place(self.grid, grid_x, grid_y):
            # Place piece
            piece.place(self.grid, grid_x, grid_y)

            # Add placement score
            self.score += piece.get_block_count() * 10

            # Remove piece from tray
            self.pieces[self.dragging_piece] = None

            # Check for line clears
            lines = self.check_lines()
            if lines > 0:
                # Bonus for multiple lines
                self.score += lines * 100 * lines

            # Check if all pieces placed
            if all(p is None for p in self.pieces):
                self.generate_new_pieces()

            # Check game over
            if not self.can_place_any_piece():
                self.game_over = True

        self.dragging_piece = None

    def draw_grid(self) -> None:
        """Draw the game grid."""
        # Draw cells
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * CELL_SIZE,
                    GRID_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                color = COLORS["block_active"] if self.grid[y][x] else COLORS["grid_cell"]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

    def draw_piece_on_grid(self, piece: Piece, grid_x: int, grid_y: int, valid: bool) -> None:
        """Draw piece preview on grid."""
        color = COLORS["block_active"] if valid else COLORS["game_over"]
        alpha_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        for dx, dy in piece.cells:
            x, y = grid_x + dx, grid_y + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * CELL_SIZE,
                    GRID_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

    def draw_piece_at_pos(self, piece: Piece, center_x: int, center_y: int, cell_size: int) -> None:
        """Draw piece centered at position."""
        width, height = piece.get_bounds()
        start_x = center_x - (width * cell_size) // 2
        start_y = center_y - (height * cell_size) // 2

        for dx, dy in piece.cells:
            rect = pygame.Rect(
                start_x + dx * cell_size,
                start_y + dy * cell_size,
                cell_size,
                cell_size
            )
            pygame.draw.rect(self.screen, piece.color, rect)
            pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

    def draw_tray(self) -> None:
        """Draw the piece tray."""
        # Draw tray label
        label = self.small_font.render("Available Pieces", True, COLORS["text"])
        self.screen.blit(label, (GRID_OFFSET_X, TRAY_Y - 25))

        # Draw pieces
        for i, piece in enumerate(self.pieces):
            if piece is None or i == self.dragging_piece:
                continue

            x, y = self.get_tray_position(i)
            self.draw_piece_at_pos(piece, x, y, TRAY_CELL_SIZE)

    def draw_dragging_piece(self, mouse_pos: Tuple[int, int]) -> None:
        """Draw the piece being dragged."""
        if self.dragging_piece is None:
            return

        piece = self.pieces[self.dragging_piece]
        if piece is None:
            return

        x, y = mouse_pos
        self.draw_piece_at_pos(piece, x, y, CELL_SIZE)

        # Draw preview on grid
        grid_x, grid_y = self.screen_to_grid(x, y)
        width, height = piece.get_bounds()
        grid_x -= width // 2
        grid_y -= height // 2

        valid = piece.can_place(self.grid, grid_x, grid_y)
        self.draw_piece_on_grid(piece, grid_x, grid_y, valid)

    def draw_score(self) -> None:
        """Draw score display."""
        score_text = self.font.render(f"Score: {self.score}", True, COLORS["text"])
        self.screen.blit(score_text, (GRID_OFFSET_X, 20))

    def draw_game_over(self) -> None:
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        text = self.font.render("GAME OVER", True, COLORS["game_over"])
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, text_rect)

        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, COLORS["text"])
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Restart button
        button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 60,
            WINDOW_HEIGHT // 2 + 40,
            120, 40
        )
        pygame.draw.rect(self.screen, COLORS["block_active"], button_rect)
        pygame.draw.rect(self.screen, COLORS["text"], button_rect, 2)

        restart_text = self.small_font.render("Restart", True, COLORS["text"])
        restart_rect = restart_text.get_rect(center=button_rect.center)
        self.screen.blit(restart_text, restart_rect)

    def draw(self) -> None:
        """Draw the entire game."""
        self.screen.fill(COLORS["background"])

        self.draw_grid()
        self.draw_tray()
        self.draw_score()

        if self.dragging_piece is not None:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_dragging_piece(mouse_pos)

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_release(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
