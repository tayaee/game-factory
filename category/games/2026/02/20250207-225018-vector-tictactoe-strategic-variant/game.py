import pygame
import sys
from typing import Optional, Tuple
from config import *
from board import Board


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Tic-Tac-Toe: Strategic Variant")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.board = Board()
        self.current_player = 1
        self.selected_piece = None
        self.valid_destinations = []
        self.game_over = False
        self.winner = None
        self.win_reason = ""
        self.total_score = {1: 0, 2: 0}
        self.turn_count = 0
        self.mouse_pos = (0, 0)

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:
                    self.handle_click(event.pos)

        return True

    def handle_click(self, pos: Tuple[int, int]) -> None:
        cell = self.board.get_cell_from_pos(pos[0], pos[1])
        if not cell:
            self.selected_piece = None
            self.valid_destinations = []
            return

        row, col = cell
        piece_count = self.board.count_pieces(self.current_player)

        if piece_count < MAX_PIECES_PER_PLAYER:
            if self.board.is_empty(row, col):
                self.place_piece(row, col)
        else:
            clicked_value = self.board.get_cell(row, col)

            if clicked_value == self.current_player:
                self.selected_piece = (row, col)
                self.update_valid_destinations()
            elif self.selected_piece and (row, col) in self.valid_destinations:
                self.move_piece(self.selected_piece, (row, col))
            else:
                self.selected_piece = None
                self.valid_destinations = []

    def update_valid_destinations(self) -> None:
        if not self.selected_piece:
            self.valid_destinations = []
            return

        pr, pc = self.selected_piece
        self.valid_destinations = []

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = pr + dr, pc + dc
                if self.board.is_valid_cell(nr, nc) and self.board.is_empty(nr, nc):
                    self.valid_destinations.append((nr, nc))

    def place_piece(self, row: int, col: int) -> None:
        self.board.set_cell(row, col, self.current_player)
        self.board.record_state()
        self.turn_count += 1

        if self.board.check_win(self.current_player):
            self.game_over = True
            self.winner = self.current_player
            self.win_reason = "Three in a row!"
            self.total_score[self.current_player] += REWARD_WIN
            self.total_score[3 - self.current_player] += REWARD_LOSS
        elif self.board.check_repetition_draw():
            self.game_over = True
            self.winner = 0
            self.win_reason = "Position repeated 3 times"
            self.total_score[1] += REWARD_DRAW
            self.total_score[2] += REWARD_DRAW
        else:
            self.switch_player()

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        self.board.set_cell(from_row, from_col, 0)
        self.board.set_cell(to_row, to_col, self.current_player)
        self.board.record_state()

        self.selected_piece = None
        self.valid_destinations = []
        self.turn_count += 1

        if self.board.check_win(self.current_player):
            self.game_over = True
            self.winner = self.current_player
            self.win_reason = "Three in a row!"
            self.total_score[self.current_player] += REWARD_WIN
            self.total_score[3 - self.current_player] += REWARD_LOSS
        elif self.board.check_repetition_draw():
            self.game_over = True
            self.winner = 0
            self.win_reason = "Position repeated 3 times"
            self.total_score[1] += REWARD_DRAW
            self.total_score[2] += REWARD_DRAW
        else:
            self.switch_player()

    def switch_player(self) -> None:
        self.current_player = 3 - self.current_player
        self.total_score[self.current_player] += 1

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_title()
        self.draw_board()
        self.draw_pieces()
        self.draw_highlights()
        self.draw_ui()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_title(self) -> None:
        title = "Strategic Tic-Tac-Toe"
        text = self.title_font.render(title, True, TEXT_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(text, rect)

    def draw_board(self) -> None:
        board_width = BOARD_SIZE * CELL_SIZE
        board_height = BOARD_SIZE * CELL_SIZE

        board_rect = pygame.Rect(
            BOARD_OFFSET_X - 10,
            BOARD_OFFSET_Y - 10,
            board_width + 20,
            board_height + 20
        )
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect, border_radius=10)

        for i in range(1, BOARD_SIZE):
            y = BOARD_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(
                self.screen,
                LINE_COLOR,
                (BOARD_OFFSET_X, y),
                (BOARD_OFFSET_X + board_width, y),
                3
            )

        for i in range(1, BOARD_SIZE):
            x = BOARD_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(
                self.screen,
                LINE_COLOR,
                (x, BOARD_OFFSET_Y),
                (x, BOARD_OFFSET_Y + board_height),
                3
            )

    def draw_pieces(self) -> None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = self.board.get_cell(row, col)
                if value != 0:
                    x, y = self.board.get_cell_center(row, col)
                    color = PLAYER1_COLOR if value == 1 else PLAYER2_COLOR
                    self.draw_piece(x, y, color, 1.0)

    def draw_piece(self, x: int, y: int, color: Tuple[int, int, int], scale: float = 1.0) -> None:
        radius = int(PIECE_RADIUS * scale)

        for r in range(radius, 0, -3):
            alpha = int(255 * (r / radius))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha // 3), (r, r), r)
            self.screen.blit(s, (x - r, y - r))

        pygame.draw.circle(self.screen, color, (x, y), radius)

        highlight_color = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
        pygame.draw.circle(self.screen, highlight_color, (x - radius // 3, y - radius // 3), radius // 4)

    def draw_highlights(self) -> None:
        if self.selected_piece:
            row, col = self.selected_piece
            x, y = self.board.get_cell_center(row, col)
            color = PLAYER1_COLOR if self.current_player == 1 else PLAYER2_COLOR
            self.draw_piece(x, y, color, HOVER_SCALE)

            pygame.draw.circle(
                self.screen,
                HIGHLIGHT_COLOR,
                (x, y),
                PIECE_RADIUS + 5,
                3
            )

        for row, col in self.valid_destinations:
            bx, by, bw, bh = self.board.get_cell_rect(row, col)
            center_x = bx + bw // 2
            center_y = by + bh // 2

            s = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.circle(s, (*VALID_MOVE_COLOR, 50), (bw // 2, bh // 2), 30)
            self.screen.blit(s, (bx, by))

            pygame.draw.circle(
                self.screen,
                VALID_MOVE_COLOR,
                (center_x, center_y),
                35,
                2
            )

        cell = self.board.get_cell_from_pos(self.mouse_pos[0], self.mouse_pos[1])
        if cell and not self.game_over:
            row, col = cell
            if self.board.is_empty(row, col) and (row, col) in self.valid_destinations:
                bx, by, bw, bh = self.board.get_cell_rect(row, col)
                pygame.draw.rect(
                    self.screen,
                    HIGHLIGHT_COLOR,
                    (bx + 5, by + 5, bw - 10, bh - 10),
                    2,
                    border_radius=5
                )

    def draw_ui(self) -> None:
        ui_y = SCREEN_HEIGHT - UI_HEIGHT + 10

        p1_color = PLAYER1_COLOR
        p2_color = PLAYER2_COLOR

        p1_label = "Player 1 (Blue)" if self.current_player == 1 else "Player 1"
        p2_label = "Player 2 (Red)" if self.current_player == 2 else "Player 2"

        p1_text = self.font.render(p1_label, True, p1_color if self.current_player == 1 else TEXT_COLOR)
        p2_text = self.font.render(p2_label, True, p2_color if self.current_player == 2 else TEXT_COLOR)

        p1_score = self.small_font.render(f"Score: {self.total_score[1]}", True, TEXT_COLOR)
        p2_score = self.small_font.render(f"Score: {self.total_score[2]}", True, TEXT_COLOR)

        self.screen.blit(p1_text, (50, ui_y))
        self.screen.blit(p1_score, (50, ui_y + 30))
        self.screen.blit(p2_text, (350, ui_y))
        self.screen.blit(p2_score, (350, ui_y + 30))

        turn_info = self.get_turn_info()
        info_text = self.small_font.render(turn_info, True, (100, 100, 100))
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, ui_y + 60))
        self.screen.blit(info_text, info_rect)

        help_text = self.small_font.render("[ESC] Quit  [SPACE] Restart", True, (150, 150, 150))
        help_rect = help_text.get_rect(right=SCREEN_WIDTH - 20, bottom=SCREEN_HEIGHT - 10)
        self.screen.blit(help_text, help_rect)

    def get_turn_info(self) -> str:
        piece_count = self.board.count_pieces(self.current_player)
        if piece_count < MAX_PIECES_PER_PLAYER:
            remaining = MAX_PIECES_PER_PLAYER - piece_count
            return f"Place your piece ({remaining} remaining)"
        else:
            return "Select a piece to move"

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.winner == 0:
            result_text = "DRAW"
            color = (200, 200, 100)
        else:
            result_text = f"PLAYER {self.winner} WINS"
            color = PLAYER1_COLOR if self.winner == 1 else PLAYER2_COLOR

        result = self.title_font.render(result_text, True, color)
        reason = self.font.render(self.win_reason, True, (220, 220, 220))

        p1_score = self.font.render(f"Player 1 Score: {self.total_score[1]}", True, PLAYER1_COLOR)
        p2_score = self.font.render(f"Player 2 Score: {self.total_score[2]}", True, PLAYER2_COLOR)

        restart = self.font.render("Press SPACE to play again", True, HIGHLIGHT_COLOR)

        result_rect = result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        reason_rect = reason.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        p1_rect = p1_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        p2_rect = p2_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        self.screen.blit(result, result_rect)
        self.screen.blit(reason, reason_rect)
        self.screen.blit(p1_score, p1_rect)
        self.screen.blit(p2_score, p2_rect)
        self.screen.blit(restart, restart_rect)

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(FPS)
