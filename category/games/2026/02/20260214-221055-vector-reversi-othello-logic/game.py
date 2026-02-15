"""Vector Reversi Othello Logic - Game implementation."""

import sys
import pygame
from config import *


class ReversiGame:
    """Main Reversi/Othello game class."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Reversi - Othello Logic")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.board = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = BLACK
        self.game_over = False
        self.winner = None
        self.valid_moves = []
        self.pieces_to_flip = []
        self.flip_animation = False
        self.flip_timer = 0
        self.flip_index = 0
        self.hover_pos = None

        # Initialize starting position
        mid = GRID_SIZE // 2
        self.board[mid - 1][mid - 1] = WHITE
        self.board[mid - 1][mid] = BLACK
        self.board[mid][mid - 1] = BLACK
        self.board[mid][mid] = WHITE

        self.calculate_valid_moves()

    def is_on_board(self, row, col):
        """Check if position is on the board."""
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE

    def get_flippable_pieces(self, row, col, player):
        """Get all pieces that would be flipped by placing at (row, col)."""
        if self.board[row][col] != EMPTY:
            return []

        opponent = WHITE if player == BLACK else BLACK
        all_flippable = []

        for dx, dy in DIRECTIONS:
            flippable = []
            r, c = row + dx, col + dy

            while self.is_on_board(r, c) and self.board[r][c] == opponent:
                flippable.append((r, c))
                r += dx
                c += dy

            if (flippable and self.is_on_board(r, c) and
                    self.board[r][c] == player):
                all_flippable.extend(flippable)

        return all_flippable

    def calculate_valid_moves(self):
        """Calculate all valid moves for the current player."""
        self.valid_moves = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                flippable = self.get_flippable_pieces(row, col, self.current_player)
                if flippable:
                    self.valid_moves.append((row, col))

    def make_move(self, row, col):
        """Make a move at the given position."""
        if (row, col) not in self.valid_moves:
            return False

        flippable = self.get_flippable_pieces(row, col, self.current_player)
        self.board[row][col] = self.current_player

        if flippable:
            self.pieces_to_flip = flippable
            self.flip_animation = True
            self.flip_timer = pygame.time.get_ticks()
            self.flip_index = 0
        else:
            self.switch_turn()

        return True

    def update_flip_animation(self):
        """Update the flip animation."""
        if not self.flip_animation:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.flip_timer >= FLIP_DELAY:
            if self.flip_index < len(self.pieces_to_flip):
                row, col = self.pieces_to_flip[self.flip_index]
                self.board[row][col] = self.current_player
                self.flip_index += 1
                self.flip_timer = current_time
            else:
                self.flip_animation = False
                self.pieces_to_flip = []
                self.switch_turn()

    def switch_turn(self):
        """Switch to the other player."""
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.calculate_valid_moves()

        if not self.valid_moves:
            # Current player has no moves
            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self.calculate_valid_moves()

            if not self.valid_moves:
                # Neither player can move - game over
                self.end_game()

    def end_game(self):
        """End the game and determine winner."""
        self.game_over = True
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)

        if black_count > white_count:
            self.winner = "Black"
        elif white_count > black_count:
            self.winner = "White"
        else:
            self.winner = "Tie"

    def get_score(self):
        """Get current score."""
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        return black_count, white_count

    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            elif event.key == pygame.K_ESCAPE:
                return False

        if not self.flip_animation and not self.game_over:
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if y < BOARD_SIZE:
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    if self.is_on_board(row, col):
                        self.hover_pos = (row, col)
                    else:
                        self.hover_pos = None
                else:
                    self.hover_pos = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if y < BOARD_SIZE:
                        col = x // CELL_SIZE
                        row = y // CELL_SIZE
                        self.make_move(row, col)

        return True

    def draw_board(self):
        """Draw the game board."""
        self.screen.fill(COLOR_BG)

        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            pos = i * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (pos, 0), (pos, BOARD_SIZE), 2)
            pygame.draw.line(self.screen, COLOR_GRID, (0, pos), (BOARD_SIZE, pos), 2)

        # Draw valid move hints
        if not self.flip_animation and not self.game_over:
            for row, col in self.valid_moves:
                center_x = col * CELL_SIZE + CELL_SIZE // 2
                center_y = row * CELL_SIZE + CELL_SIZE // 2
                color = COLOR_HINT_HOVER if self.hover_pos == (row, col) else COLOR_HINT
                pygame.draw.circle(self.screen, color, (center_x, center_y), 10)

        # Draw pieces
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] != EMPTY:
                    center_x = col * CELL_SIZE + CELL_SIZE // 2
                    center_y = row * CELL_SIZE + CELL_SIZE // 2
                    color = COLOR_BLACK if self.board[row][col] == BLACK else COLOR_WHITE
                    pygame.draw.circle(self.screen, color, (center_x, center_y), CELL_SIZE // 2 - 5)
                    pygame.draw.circle(self.screen, COLOR_GRID, (center_x, center_y), CELL_SIZE // 2 - 5, 2)

    def draw_panel(self):
        """Draw the info panel."""
        panel_rect = pygame.Rect(0, BOARD_SIZE, SCREEN_WIDTH, SIDE_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)

        black_count, white_count = self.get_score()

        # Draw scores
        black_text = self.font_medium.render(f"Black: {black_count}", True, COLOR_TEXT)
        white_text = self.font_medium.render(f"White: {white_count}", True, COLOR_TEXT)
        self.screen.blit(black_text, (50, BOARD_SIZE + 20))
        self.screen.blit(white_text, (50, BOARD_SIZE + 55))

        # Draw current turn
        if not self.game_over:
            turn_text = "Black's Turn" if self.current_player == BLACK else "White's Turn"
            turn_surface = self.font_large.render(turn_text, True, COLOR_TEXT)
            self.screen.blit(turn_surface, (SCREEN_WIDTH // 2 - turn_surface.get_width() // 2, BOARD_SIZE + 35))
        else:
            if self.winner == "Tie":
                result_text = "Game Over - It's a Tie!"
            else:
                result_text = f"Game Over - {self.winner} Wins!"
            result_surface = self.font_large.render(result_text, True, COLOR_VALID_MOVE)
            self.screen.blit(result_surface, (SCREEN_WIDTH // 2 - result_surface.get_width() // 2, BOARD_SIZE + 35))

        # Draw controls hint
        hint_text = self.font_small.render("R: Restart | ESC: Quit", True, COLOR_TEXT)
        self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, BOARD_SIZE + 40))

    def draw(self):
        """Draw everything."""
        self.draw_board()
        self.draw_panel()
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False

            self.update_flip_animation()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Alias for consistency with other apps
Game = ReversiGame
