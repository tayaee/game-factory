"""Game entities for Vector Columns Falling Match."""

import random
from typing import List, Tuple, Set
from config import (
    GRID_COLS, GRID_ROWS, EMPTY, GEM_COLORS,
    BASE_SCORE, CHAIN_MULTIPLIER
)


class FallingColumn:
    """Represents a falling column of three gems."""

    def __init__(self, col: int = 2):
        self.col = col
        self.row = 0
        self.gems = [random.randint(1, len(GEM_COLORS)) for _ in range(3)]

    def cycle(self) -> None:
        """Cycle the gems: top becomes middle, middle becomes bottom, bottom becomes top."""
        self.gems = [self.gems[-1]] + self.gems[:-1]

    def move_left(self) -> bool:
        """Move column left. Returns True if successful."""
        if self.col > 0:
            self.col -= 1
            return True
        return False

    def move_right(self) -> bool:
        """Move column right. Returns True if successful."""
        if self.col < GRID_COLS - 1:
            self.col += 1
            return True
        return False

    def get_gems(self) -> List[int]:
        """Get the gem colors in this column."""
        return self.gems


class GameState:
    """Manages the game grid, logic, and state."""

    def __init__(self):
        self.grid: List[List[int]] = [[EMPTY for _ in range(GRID_ROWS)]
                                        for _ in range(GRID_COLS)]
        self.falling_column: FallingColumn = None
        self.score: int = 0
        self.game_over: bool = False
        self.paused: bool = False
        self.level: int = 1
        self.gems_cleared: int = 0
        self.chain_count: int = 0
        self.fall_delay: int = 800
        self.spawn_new_column()

    def spawn_new_column(self) -> None:
        """Create a new falling column at the top."""
        self.falling_column = FallingColumn(GRID_COLS // 2)
        self.chain_count = 0

        # Check if spawn position is blocked
        if not self._is_valid_spawn():
            self.game_over = True

    def _is_valid_spawn(self) -> bool:
        """Check if the new column can spawn."""
        col = self.falling_column.col
        gems = self.falling_column.gems
        for i, gem in enumerate(gems):
            row = i
            if row < GRID_ROWS and self.grid[col][row] != EMPTY:
                return False
        return True

    def is_valid_position(self, col: int, row_offset: int) -> bool:
        """Check if a position is valid for the falling column."""
        column = self.falling_column
        if col < 0 or col >= GRID_COLS:
            return False
        for i, gem in enumerate(column.gems):
            row = row_offset + i
            if row >= GRID_ROWS:
                return False
            if row >= 0 and self.grid[col][row] != EMPTY:
                return False
        return True

    def lock_column(self) -> None:
        """Lock the falling column into the grid and check for matches."""
        if not self.falling_column:
            return

        col = self.falling_column.col
        gems = self.falling_column.gems

        for i, gem in enumerate(gems):
            row = self.falling_column.row + i - 2
            if 0 <= row < GRID_ROWS:
                self.grid[col][row] = gem

        self._apply_gravity()
        self._check_and_clear_matches()

    def _apply_gravity(self) -> None:
        """Make gems fall down to fill empty spaces."""
        for col in range(GRID_COLS):
            # Collect non-empty gems
            gems = [self.grid[col][row] for row in range(GRID_ROWS)
                    if self.grid[col][row] != EMPTY]
            # Fill column from bottom
            for row in range(GRID_ROWS - 1, -1, -1):
                offset = GRID_ROWS - 1 - row
                if offset < len(gems):
                    self.grid[col][row] = gems[-(offset + 1)]
                else:
                    self.grid[col][row] = EMPTY

    def _check_and_clear_matches(self) -> None:
        """Find and clear all matching sets of 3+ gems."""
        to_clear: Set[Tuple[int, int]] = set()

        # Check vertical matches
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                gem = self.grid[col][row]
                if gem != EMPTY:
                    if (self.grid[col][row + 1] == gem and
                        self.grid[col][row + 2] == gem):
                        to_clear.add((col, row))
                        to_clear.add((col, row + 1))
                        to_clear.add((col, row + 2))
                        # Extend the match
                        k = row + 3
                        while k < GRID_ROWS and self.grid[col][k] == gem:
                            to_clear.add((col, k))
                            k += 1

        # Check horizontal matches
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                gem = self.grid[col][row]
                if gem != EMPTY:
                    if (self.grid[col + 1][row] == gem and
                        self.grid[col + 2][row] == gem):
                        to_clear.add((col, row))
                        to_clear.add((col + 1, row))
                        to_clear.add((col + 2, row))
                        # Extend the match
                        k = col + 3
                        while k < GRID_COLS and self.grid[k][row] == gem:
                            to_clear.add((k, row))
                            k += 1

        # Check diagonal matches (top-left to bottom-right)
        for col in range(GRID_COLS - 2):
            for row in range(GRID_ROWS - 2):
                gem = self.grid[col][row]
                if gem != EMPTY:
                    if (self.grid[col + 1][row + 1] == gem and
                        self.grid[col + 2][row + 2] == gem):
                        to_clear.add((col, row))
                        to_clear.add((col + 1, row + 1))
                        to_clear.add((col + 2, row + 2))
                        # Extend the match
                        k = 3
                        while (col + k < GRID_COLS and row + k < GRID_ROWS and
                               self.grid[col + k][row + k] == gem):
                            to_clear.add((col + k, row + k))
                            k += 1

        # Check diagonal matches (bottom-left to top-right)
        for col in range(GRID_COLS - 2):
            for row in range(2, GRID_ROWS):
                gem = self.grid[col][row]
                if gem != EMPTY:
                    if (self.grid[col + 1][row - 1] == gem and
                        self.grid[col + 2][row - 2] == gem):
                        to_clear.add((col, row))
                        to_clear.add((col + 1, row - 1))
                        to_clear.add((col + 2, row - 2))
                        # Extend the match
                        k = 3
                        while (col + k < GRID_COLS and row - k >= 0 and
                               self.grid[col + k][row - k] == gem):
                            to_clear.add((col + k, row - k))
                            k += 1

        if to_clear:
            self.chain_count += 1
            cleared = len(to_clear)
            self.gems_cleared += cleared

            # Calculate score with chain multiplier
            chain_bonus = int(BASE_SCORE * (CHAIN_MULTIPLIER ** (self.chain_count - 1)))
            self.score += cleared * chain_bonus

            # Clear the gems
            for col, row in to_clear:
                self.grid[col][row] = EMPTY

            # Apply gravity and check for chain reactions
            self._apply_gravity()
            self._check_and_clear_matches()

        # Update level based on gems cleared
        self._update_level()

    def _update_level(self) -> None:
        """Update the game level based on progress."""
        from config import LEVEL_LINES, SPEED_DECREASE, MIN_FALL_DELAY

        new_level = 1
        for threshold in LEVEL_LINES:
            if self.gems_cleared >= threshold:
                new_level += 1

        if new_level != self.level:
            self.level = new_level
            self.fall_delay = max(
                MIN_FALL_DELAY,
                800 - (self.level - 1) * SPEED_DECREASE
            )

    def get_observation(self) -> dict:
        """Get the current game state for RL agents."""
        return {
            "grid": [row[:] for row in self.grid],
            "falling_column": {
                "col": self.falling_column.col if self.falling_column else 0,
                "row": self.falling_column.row if self.falling_column else 0,
                "gems": self.falling_column.gems if self.falling_column else [0, 0, 0]
            },
            "score": self.score,
            "game_over": self.game_over
        }

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.grid = [[EMPTY for _ in range(GRID_ROWS)]
                     for _ in range(GRID_COLS)]
        self.score = 0
        self.game_over = False
        self.paused = False
        self.level = 1
        self.gems_cleared = 0
        self.chain_count = 0
        self.fall_delay = 800
        self.spawn_new_column()
