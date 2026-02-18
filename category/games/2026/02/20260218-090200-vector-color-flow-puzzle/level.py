"""Level generator and management for Color Flow Puzzle."""

import random
from typing import List, Tuple, Set


class LevelGenerator:
    """Generate solvable color flow puzzle levels."""

    def __init__(self, grid_size: int, num_colors: int):
        self.grid_size = grid_size
        self.num_colors = num_colors

    def generate(self) -> Tuple[List[List[int]], List[Tuple[int, int, int, int]]]:
        """Generate a solvable level with the specified number of color pairs.

        Returns:
            Tuple of (initial_grid, dot_positions) where dot_positions is a list
            of (row1, col1, row2, col2) for each color pair.
        """
        # Create empty grid
        grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Generate valid dot positions
        dot_positions = self._generate_dot_positions()

        # Place dots on the grid
        for color_id, (r1, c1, r2, c2) in enumerate(dot_positions, 1):
            grid[r1][c1] = color_id
            grid[r2][c2] = color_id

        return grid, dot_positions

    def _generate_dot_positions(self) -> List[Tuple[int, int, int, int]]:
        """Generate valid dot positions for all color pairs."""
        available_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        random.shuffle(available_cells)

        positions = []
        for _ in range(self.num_colors):
            if len(available_cells) < 2:
                break

            pos1 = available_cells.pop()
            pos2 = available_cells.pop()

            # Ensure dots are not adjacent horizontally or vertically
            # to make the puzzle more interesting
            while abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) <= 1 and available_cells:
                available_cells.insert(0, pos2)
                pos2 = available_cells.pop()

            positions.append((pos1[0], pos1[1], pos2[0], pos2[1]))

        return positions


class Level:
    """Represents a single puzzle level."""

    def __init__(self, grid_size: int, num_colors: int):
        self.grid_size = grid_size
        self.num_colors = num_colors
        self.initial_grid, self.dot_positions = LevelGenerator(
            grid_size, num_colors
        ).generate()
        self.reset()

    def reset(self):
        """Reset the level to initial state."""
        self.grid = [row[:] for row in self.initial_grid]
        self.pipes = {color_id: [] for color_id in range(1, self.num_colors + 1)}
        self.completed_pipes = set()

    def get_empty_cells(self) -> int:
        """Count empty cells that are not dots."""
        count = 0
        dot_cells = {(r1, c1) for (r1, c1, _, _) in self.dot_positions}
        dot_cells.update({(r2, c2) for (_, _, r2, c2) in self.dot_positions})

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.grid[r][c] == 0 and (r, c) not in dot_cells:
                    count += 1
        return count

    def is_full(self) -> bool:
        """Check if all cells are filled."""
        return self.get_empty_cells() == 0

    def is_complete(self) -> bool:
        """Check if all color pairs are connected."""
        for color_id in range(1, self.num_colors + 1):
            if not self._is_color_connected(color_id):
                return False
        return self.is_full()

    def _is_color_connected(self, color_id: int) -> bool:
        """Check if a color's dots are connected by its pipe."""
        dots = [(r1, c1) for (r1, c1, _, _) in [self.dot_positions[color_id - 1]]]
        dots.append((self.dot_positions[color_id - 1][2], self.dot_positions[color_id - 1][3]))

        # Get all cells with this color (including pipe)
        color_cells = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.grid[r][c] == color_id:
                    color_cells.append((r, c))

        # Use BFS to check if both dots are connected
        if not color_cells:
            return False

        visited = set()
        queue = [color_cells[0]]
        visited.add(color_cells[0])

        while queue:
            current = queue.pop(0)
            if current in dots:
                dots.remove(current)

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = current[0] + dr, current[1] + dc
                if (nr, nc) in color_cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))

        return len(dots) == 0
