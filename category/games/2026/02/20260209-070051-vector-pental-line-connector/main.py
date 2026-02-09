"""Vector Pental Line Connector - A Gomoku-style strategy game."""

import pygame
import sys
from typing import Optional, Tuple, List

# Constants
GRID_SIZE = 15
CELL_SIZE = 40
MARGIN = 40
WINDOW_SIZE = GRID_SIZE * CELL_SIZE + 2 * MARGIN

# Colors
COLOR_BG = (220, 180, 130)
COLOR_GRID = (50, 40, 30)
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (240, 240, 240)
COLOR_HIGHLIGHT = (200, 50, 50)
COLOR_TEXT = (30, 30, 30)

# Players
EMPTY = 0
PLAYER_BLACK = 1
PLAYER_WHITE = 2


class GameState:
    """Manages the game state and board."""

    def __init__(self):
        self.board: List[List[int]] = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = PLAYER_BLACK
        self.winner: Optional[int] = None
        self.game_over = False
        self.last_move: Optional[Tuple[int, int]] = None
        self.scores = {PLAYER_BLACK: 0, PLAYER_WHITE: 0}

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid."""
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.board[row][col] == EMPTY

    def make_move(self, row: int, col: int) -> bool:
        """Attempt to make a move. Returns True if successful."""
        if not self.is_valid_move(row, col) or self.game_over:
            return False

        self.board[row][col] = self.current_player
        self.last_move = (row, col)

        # Check for win
        if self._check_win(row, col):
            self.winner = self.current_player
            self.scores[self.current_player] += 100
            self.scores[3 - self.current_player] -= 100
            self.game_over = True
        elif self._is_board_full():
            self.game_over = True
        else:
            # Score intermediate sequences
            sequences = self._count_sequences(row, col)
            self.scores[self.current_player] += sequences
            self.current_player = 3 - self.current_player  # Switch player

        return True

    def _check_win(self, row: int, col: int) -> bool:
        """Check if the last move resulted in a win."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        player = self.board[row][col]

        for dr, dc in directions:
            count = 1

            # Count in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            # Count in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count == 5:
                return True

        return False

    def _count_sequences(self, row: int, col: int) -> int:
        """Count sequences of 3 or 4 stones created by the last move."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        player = self.board[row][col]
        total = 0

        for dr, dc in directions:
            count = 1

            # Count in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            # Count in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count == 3 or count == 4:
                total += 1

        return total

    def _is_board_full(self) -> bool:
        """Check if the board is full."""
        return all(self.board[r][c] != EMPTY for r in range(GRID_SIZE) for c in range(GRID_SIZE))

    def get_board_matrix(self) -> List[List[int]]:
        """Return the board state as a 2D matrix for AI training."""
        return [row[:] for row in self.board]

    def get_action_space_size(self) -> int:
        """Return the size of the action space."""
        return GRID_SIZE * GRID_SIZE


class Renderer:
    """Handles rendering of the game."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 60))
        pygame.display.set_caption("Vector Pental Line Connector")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 48)

    def draw(self, game_state: GameState):
        """Draw the current game state."""
        self.screen.fill(COLOR_BG)

        # Draw grid
        for i in range(GRID_SIZE):
            # Horizontal lines
            start_pos = (MARGIN, MARGIN + i * CELL_SIZE)
            end_pos = (WINDOW_SIZE - MARGIN, MARGIN + i * CELL_SIZE)
            pygame.draw.line(self.screen, COLOR_GRID, start_pos, end_pos, 2)

            # Vertical lines
            start_pos = (MARGIN + i * CELL_SIZE, MARGIN)
            end_pos = (MARGIN + i * CELL_SIZE, WINDOW_SIZE - MARGIN)
            pygame.draw.line(self.screen, COLOR_GRID, start_pos, end_pos, 2)

        # Draw stones
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if game_state.board[r][c] != EMPTY:
                    x = MARGIN + c * CELL_SIZE
                    y = MARGIN + r * CELL_SIZE
                    color = COLOR_BLACK if game_state.board[r][c] == PLAYER_BLACK else COLOR_WHITE
                    pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 4)

        # Highlight last move
        if game_state.last_move:
            r, c = game_state.last_move
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + r * CELL_SIZE
            pygame.draw.circle(self.screen, COLOR_HIGHLIGHT, (x, y), 6)

        # Draw UI panel
        self._draw_ui(game_state)

        pygame.display.flip()

    def _draw_ui(self, game_state: GameState):
        """Draw the UI panel at the bottom."""
        ui_y = WINDOW_SIZE
        pygame.draw.rect(self.screen, (200, 160, 110), (0, ui_y, WINDOW_SIZE, 60))

        if game_state.game_over:
            if game_state.winner:
                winner_text = "Black" if game_state.winner == PLAYER_BLACK else "White"
                message = f"{winner_text} Wins! (+100)"
            else:
                message = "Draw! Board Full"
            text = self.large_font.render(message, True, COLOR_TEXT)
            self.screen.blit(text, (WINDOW_SIZE // 2 - text.get_width() // 2, ui_y + 15))
        else:
            turn_text = "Black's Turn" if game_state.current_player == PLAYER_BLACK else "White's Turn"
            score_text = f"Black: {game_state.scores[PLAYER_BLACK]}  |  White: {game_state.scores[PLAYER_WHITE]}"
            turn = self.font.render(turn_text, True, COLOR_TEXT)
            score = self.font.render(score_text, True, COLOR_TEXT)
            self.screen.blit(turn, (20, ui_y + 15))
            self.screen.blit(score, (WINDOW_SIZE - score.get_width() - 20, ui_y + 15))

    def get_grid_position(self, mouse_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert mouse position to grid coordinates."""
        x, y = mouse_pos
        col = round((x - MARGIN) / CELL_SIZE)
        row = round((y - MARGIN) / CELL_SIZE)
        return row, col


def main():
    """Main game loop."""
    game = GameState()
    renderer = Renderer()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not game.game_over:
                    row, col = renderer.get_grid_position(event.pos)
                    game.make_move(row, col)
                else:
                    # Reset game on click after game over
                    game = GameState()

        renderer.draw(game)
        renderer.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
