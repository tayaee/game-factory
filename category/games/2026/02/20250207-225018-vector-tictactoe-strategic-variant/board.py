from typing import List, Tuple, Optional
from config import *


class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board_history = []

    def get_cell(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set_cell(self, row: int, col: int, player: int) -> None:
        self.grid[row][col] = player

    def is_empty(self, row: int, col: int) -> bool:
        return self.grid[row][col] == 0

    def is_valid_cell(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_player_pieces(self, player: int) -> List[Tuple[int, int]]:
        pieces = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col] == player:
                    pieces.append((row, col))
        return pieces

    def count_pieces(self, player: int) -> int:
        return len(self.get_player_pieces(player))

    def is_adjacent(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and (r1 != r2 or c1 != c2)

    def get_valid_moves(self, player: int) -> List[Tuple[Optional[Tuple[int, int]], Tuple[int, int]]]:
        moves = []
        piece_count = self.count_pieces(player)

        if piece_count < MAX_PIECES_PER_PLAYER:
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if self.is_empty(row, col):
                        moves.append((None, (row, col)))
        else:
            pieces = self.get_player_pieces(player)
            for piece in pieces:
                pr, pc = piece
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = pr + dr, pc + dc
                        if self.is_valid_cell(nr, nc) and self.is_empty(nr, nc):
                            moves.append(((pr, pc), (nr, nc)))

        return moves

    def check_win(self, player: int) -> bool:
        for row in range(BOARD_SIZE):
            if all(self.grid[row][col] == player for col in range(BOARD_SIZE)):
                return True

        for col in range(BOARD_SIZE):
            if all(self.grid[row][col] == player for row in range(BOARD_SIZE)):
                return True

        if all(self.grid[i][i] == player for i in range(BOARD_SIZE)):
            return True

        if all(self.grid[i][BOARD_SIZE - 1 - i] == player for i in range(BOARD_SIZE)):
            return True

        return False

    def is_full(self) -> bool:
        return all(self.grid[row][col] != 0 for row in range(BOARD_SIZE) for col in range(BOARD_SIZE))

    def get_state_key(self) -> str:
        return ''.join(str(self.grid[row][col]) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE))

    def record_state(self) -> None:
        state_key = self.get_state_key()
        self.board_history.append(state_key)

    def check_repetition_draw(self) -> bool:
        if not self.board_history:
            return False

        current_state = self.board_history[-1]
        count = sum(1 for state in self.board_history if state == current_state)
        return count >= MAX_REPETITION

    def get_cell_from_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        col = (x - BOARD_OFFSET_X) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None

    def get_cell_rect(self, row: int, col: int) -> Tuple[int, int, int, int]:
        x = BOARD_OFFSET_X + col * CELL_SIZE
        y = BOARD_OFFSET_Y + row * CELL_SIZE
        return x, y, CELL_SIZE, CELL_SIZE

    def get_cell_center(self, row: int, col: int) -> Tuple[int, int]:
        x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        return x, y
