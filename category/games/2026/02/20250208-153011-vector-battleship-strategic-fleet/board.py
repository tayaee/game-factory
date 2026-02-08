import random
from typing import List, Tuple, Optional, Dict
from config import *


class Ship:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.positions: List[Tuple[int, int]] = []
        self.hits: List[Tuple[int, int]] = []
        self.is_sunk = False

    def place(self, positions: List[Tuple[int, int]]) -> None:
        self.positions = positions.copy()
        self.hits = []
        self.is_sunk = False

    def hit(self, row: int, col: int) -> bool:
        if (row, col) in self.positions and (row, col) not in self.hits:
            self.hits.append((row, col))
            if len(self.hits) == self.size:
                self.is_sunk = True
            return True
        return False

    def contains(self, row: int, col: int) -> bool:
        return (row, col) in self.positions

    def is_hit_at(self, row: int, col: int) -> bool:
        return (row, col) in self.hits


class Board:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ships: List[Ship] = []
        self.shots: List[Tuple[int, int]] = []
        self.setup_ships()

    def setup_ships(self):
        self.ships = []
        for ship_name, ship_data in SHIPS.items():
            for _ in range(ship_data["count"]):
                self.ships.append(Ship(ship_name, ship_data["size"]))

    def place_ships_randomly(self) -> bool:
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.shots = []

        for ship in self.ships:
            placed = False
            attempts = 0
            max_attempts = 1000

            while not placed and attempts < max_attempts:
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - 1)
                horizontal = random.choice([True, False])

                if self.can_place_ship(ship, row, col, horizontal):
                    positions = self.get_ship_positions(ship, row, col, horizontal)
                    ship.place(positions)
                    for r, c in positions:
                        self.grid[r][c] = SHIP
                    placed = True

                attempts += 1

            if not placed:
                return False

        return True

    def can_place_ship(self, ship: Ship, row: int, col: int, horizontal: bool) -> bool:
        positions = self.get_ship_positions(ship, row, col, horizontal)
        if not positions:
            return False

        for r, c in positions:
            if not self.is_valid_cell(r, c):
                return False
            if self.grid[r][c] != EMPTY:
                return False
            if self.has_adjacent_ship(r, c):
                return False

        return True

    def get_ship_positions(self, ship: Ship, row: int, col: int, horizontal: bool) -> List[Tuple[int, int]]:
        positions = []
        for i in range(ship.size):
            if horizontal:
                r, c = row, col + i
            else:
                r, c = row + i, col
            positions.append((r, c))
        return positions

    def has_adjacent_ship(self, row: int, col: int) -> bool:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if self.is_valid_cell(nr, nc) and self.grid[nr][nc] == SHIP:
                    return True
        return False

    def is_valid_cell(self, row: int, col: int) -> bool:
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE

    def fire_at(self, row: int, col: int) -> Tuple[bool, Optional[Ship]]:
        if not self.is_valid_cell(row, col):
            return False, None

        if (row, col) in self.shots:
            return False, None

        self.shots.append((row, col))

        for ship in self.ships:
            if ship.contains(row, col):
                ship.hit(row, col)
                self.grid[row][col] = SUNK if ship.is_sunk else HIT
                return True, ship

        self.grid[row][col] = MISS
        return False, None

    def get_cell(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def has_ship_at(self, row: int, col: int) -> bool:
        return self.grid[row][col] == SHIP

    def is_shot_at(self, row: int, col: int) -> bool:
        return (row, col) in self.shots

    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk for ship in self.ships)

    def get_remaining_health(self) -> int:
        total_cells = sum(ship.size for ship in self.ships)
        hit_cells = sum(len(ship.hits) for ship in self.ships)
        return total_cells - hit_cells

    def get_unsunk_ship_cells(self) -> List[Tuple[int, int]]:
        cells = []
        for ship in self.ships:
            if not ship.is_sunk:
                for r, c in ship.positions:
                    if (r, c) not in ship.hits:
                        cells.append((r, c))
        return cells

    def get_hit_cells(self) -> List[Tuple[int, int]]:
        hit_cells = []
        for ship in self.ships:
            if not ship.is_sunk:
                for r, c in ship.hits:
                    hit_cells.append((r, c))
        return hit_cells

    def get_state_array(self) -> List[int]:
        state = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.grid[row][col]
                if cell == EMPTY or cell == SHIP:
                    state.append(0)
                elif cell == MISS:
                    state.append(1)
                elif cell == HIT:
                    state.append(2)
                elif cell == SUNK:
                    state.append(3)
        return state

    def get_cell_from_pos(self, x: int, y: int, offset_x: int) -> Optional[Tuple[int, int]]:
        col = (x - offset_x) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return row, col
        return None

    def get_cell_rect(self, row: int, col: int, offset_x: int) -> Tuple[int, int, int, int]:
        x = offset_x + col * CELL_SIZE
        y = BOARD_OFFSET_Y + row * CELL_SIZE
        return x, y, CELL_SIZE, CELL_SIZE
