import random
from typing import Tuple, List, Optional
from config import *
from board import Board


class BattleshipAI:
    def __init__(self, enemy_board: Board):
        self.enemy_board = enemy_board
        self.priority_queue = []
        self.hunt_mode = False
        self.current_target_hits = []
        self.possible_ship_orientations = []
        self.visited = set()
        self.init_probability_grid()

    def init_probability_grid(self):
        self.probability_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def get_next_shot(self) -> Tuple[int, int]:
        self.update_probabilities()

        if self.hunt_mode and self.current_target_hits:
            return self.get_targeted_shot()
        else:
            return self.get_probability_shot()

    def update_probabilities(self):
        self.init_probability_grid()

        for ship_name, ship_data in SHIPS.items():
            size = ship_data["size"]

            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if (row, col) in self.visited:
                        continue

                    for horizontal in [True, False]:
                        positions = self.get_potential_positions(row, col, size, horizontal)
                        if self.is_valid_placement(positions):
                            for r, c in positions:
                                self.probability_grid[r][c] += 1

    def get_potential_positions(self, row: int, col: int, size: int, horizontal: bool) -> List[Tuple[int, int]]:
        positions = []
        for i in range(size):
            if horizontal:
                r, c = row, col + i
            else:
                r, c = row + i, col
            positions.append((r, c))
        return positions

    def is_valid_placement(self, positions: List[Tuple[int, int]]) -> bool:
        if not positions:
            return False

        for r, c in positions:
            if not self.enemy_board.is_valid_cell(r, c):
                return False
            if (r, c) in self.visited and self.enemy_board.get_cell(r, c) == MISS:
                return False

        return True

    def get_probability_shot(self) -> Tuple[int, int]:
        max_prob = -1
        candidates = []

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if (row, col) not in self.visited:
                    if self.probability_grid[row][col] > max_prob:
                        max_prob = self.probability_grid[row][col]
                        candidates = [(row, col)]
                    elif self.probability_grid[row][col] == max_prob:
                        candidates.append((row, col))

        if candidates:
            return random.choice(candidates)

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if (row, col) not in self.visited:
                    candidates.append((row, col))

        return random.choice(candidates) if candidates else (0, 0)

    def get_targeted_shot(self) -> Tuple[int, int]:
        adjacent_cells = []

        for r, c in self.current_target_hits:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if self.is_valid_target(nr, nc):
                    adjacent_cells.append((nr, nc))

        if adjacent_cells:
            return random.choice(adjacent_cells)

        self.hunt_mode = False
        self.current_target_hits = []
        return self.get_probability_shot()

    def is_valid_target(self, row: int, col: int) -> bool:
        if not self.enemy_board.is_valid_cell(row, col):
            return False
        if (row, col) in self.visited:
            return False
        return True

    def process_shot_result(self, row: int, col: int, hit: bool, ship_sunk: bool):
        self.visited.add((row, col))

        if hit:
            self.current_target_hits.append((row, col))
            self.hunt_mode = True

            if ship_sunk:
                self.hunt_mode = False
                self.current_target_hits = []
        else:
            if len(self.current_target_hits) <= 1:
                self.current_target_hits = []
                self.hunt_mode = False

    def reset(self):
        self.hunt_mode = False
        self.current_target_hits = []
        self.visited = set()
        self.init_probability_grid()
