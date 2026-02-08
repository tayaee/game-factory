"""Game entities and state management for Vector Tetris Grid Logic."""

import random
import copy
from config import *


class Tetromino:
    """Represents a falling Tetris piece."""

    def __init__(self, shape_type: str):
        self.shape_type = shape_type
        self.blocks = copy.deepcopy(SHAPES[shape_type])
        self.color_index = SHAPE_ORDER.index(shape_type)
        self.rotation = 0  # 0, 1, 2, 3 representing 0, 90, 180, 270 degrees

        # Starting position (centered at top)
        self.row = 0
        self.col = GRID_WIDTH // 2

    def get_blocks(self) -> list:
        """Get absolute positions of all blocks."""
        return [(self.row + r, self.col + c) for r, c in self.blocks]

    def rotate(self, direction: int = 1) -> list:
        """
        Rotate blocks clockwise (direction=1) or counter-clockwise (direction=-1).
        Returns the new block positions.
        """
        new_blocks = []
        for r, c in self.blocks:
            if direction == 1:  # Clockwise
                new_r, new_c = -c, r
            else:  # Counter-clockwise
                new_r, new_c = c, -r
            new_blocks.append((new_r, new_c))

        # Normalize blocks so min row and col are at origin
        min_r = min(r for r, c in new_blocks)
        min_c = min(c for r, c in new_blocks)
        new_blocks = [(r - min_r, c - min_c) for r, c in new_blocks]

        return new_blocks

    def get_ghost_position(self, grid: list) -> int:
        """Get the row where the ghost piece would land."""
        ghost_row = self.row
        while True:
            collision = False
            for r, c in self.blocks:
                check_row = ghost_row + r + 1
                check_col = self.col + c
                if check_row >= GRID_HEIGHT:
                    collision = True
                    break
                if check_col < 0 or check_col >= GRID_WIDTH:
                    continue
                if grid[check_row][check_col] is not None:
                    collision = True
                    break
            if collision:
                break
            ghost_row += 1
        return ghost_row


class GameState:
    """Manages the game state and logic."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the game to initial state."""
        # Grid: None for empty, int 0-6 for block type
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False

        # Piece management
        self.current_piece = self._get_random_piece()
        self.next_piece = self._get_random_piece()
        self.hold_piece = None
        self.can_hold = True

        # Timing
        self.fall_speed = INITIAL_FALL_SPEED
        self.last_fall_time = 0
        self.lock_delay = 500
        self.lock_timer = 0
        self.is_locked = False

    def _get_random_piece(self) -> Tetromino:
        """Get a random piece using 7-bag randomizer."""
        if not hasattr(self, '_bag') or not self._bag:
            self._bag = SHAPE_ORDER.copy()
            random.shuffle(self._bag)
        return Tetromino(self._bag.pop())

    def _is_valid_position(self, blocks: list, row: int, col: int) -> bool:
        """Check if a piece position is valid."""
        for r, c in blocks:
            check_row = row + r
            check_col = col + c

            # Boundary check
            if check_row < 0 or check_row >= GRID_HEIGHT:
                return False
            if check_col < 0 or check_col >= GRID_WIDTH:
                return False

            # Collision check
            if self.grid[check_row][check_col] is not None:
                return False

        return True

    def move_piece(self, dx: int, dy: int) -> bool:
        """Move the current piece. Returns True if successful."""
        if self.game_over or self.paused:
            return False

        new_row = self.current_piece.row + dy
        new_col = self.current_piece.col + dx

        if self._is_valid_position(self.current_piece.blocks, new_row, new_col):
            self.current_piece.row = new_row
            self.current_piece.col = new_col

            # Reset lock delay on horizontal move
            if dx != 0:
                self.lock_timer = 0

            return True
        return False

    def rotate_piece(self, direction: int = 1) -> bool:
        """Rotate the current piece. Returns True if successful."""
        if self.game_over or self.paused:
            return False

        if self.current_piece.shape_type == 'O':
            return False  # O doesn't rotate

        new_blocks = self.current_piece.rotate(direction)
        kick_table = WALL_KICKS['I'] if self.current_piece.shape_type == 'I' else WALL_KICKS['normal']
        kick_index = (self.current_piece.rotation + (1 if direction == 1 else 3)) % 4

        # Try wall kicks
        for dx, dy in kick_table[kick_index]:
            if direction == -1:
                dx, dy = -dx, -dy

            if self._is_valid_position(new_blocks, self.current_piece.row + dy, self.current_piece.col + dx):
                self.current_piece.blocks = new_blocks
                self.current_piece.row += dy
                self.current_piece.col += dx
                self.current_piece.rotation = (self.current_piece.rotation + direction) % 4
                self.lock_timer = 0
                return True

        return False

    def hard_drop(self) -> int:
        """Instantly drop the piece. Returns cells dropped."""
        if self.game_over or self.paused:
            return 0

        ghost_row = self.current_piece.get_ghost_position(self.grid)
        drop_distance = ghost_row - self.current_piece.row
        self.current_piece.row = ghost_row
        self.score += drop_distance * HARD_DROP_SCORE
        self._lock_piece()
        return drop_distance

    def soft_drop(self) -> bool:
        """Move piece down by one cell. Returns True if successful."""
        if self.move_piece(0, 1):
            self.score += SOFT_DROP_SCORE
            return True
        return False

    def hold(self) -> bool:
        """Hold the current piece. Returns True if successful."""
        if self.game_over or self.paused or not self.can_hold:
            return False

        current_type = self.current_piece.shape_type

        if self.hold_piece is None:
            self.hold_piece = current_type
            self.current_piece = self.next_piece
            self.next_piece = self._get_random_piece()
        else:
            hold_type = self.hold_piece
            self.hold_piece = current_type
            self.current_piece = Tetromino(hold_type)

        self.can_hold = False
        self.lock_timer = 0
        return True

    def _lock_piece(self):
        """Lock the current piece into the grid."""
        for r, c in self.current_piece.get_blocks():
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                self.grid[r][c] = self.current_piece.color_index

        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self):
        """Clear completed lines and update score."""
        lines_to_clear = []

        for row in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[row]):
                lines_to_clear.append(row)

        if lines_to_clear:
            # Remove lines from top to bottom
            for row in sorted(lines_to_clear, reverse=True):
                del self.grid[row]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

            # Update score
            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared

            if lines_cleared == 1:
                self.score += SCORE_1_LINE
            elif lines_cleared == 2:
                self.score += SCORE_2_LINES
            elif lines_cleared == 3:
                self.score += SCORE_3_LINES
            elif lines_cleared == 4:
                self.score += SCORE_4_LINES

            # Update level and speed
            new_level = self.lines_cleared // SPEED_INCREASE_INTERVAL + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(MIN_FALL_SPEED, INITIAL_FALL_SPEED - (self.level - 1) * SPEED_DECREASE)

    def _spawn_piece(self):
        """Spawn a new piece."""
        self.current_piece = self.next_piece
        self.next_piece = self._get_random_piece()
        self.can_hold = True
        self.lock_timer = 0

        # Check for game over
        if not self._is_valid_position(self.current_piece.blocks,
                                       self.current_piece.row,
                                       self.current_piece.col):
            self.game_over = True

    def update(self, dt: int) -> bool:
        """
        Update game state by dt milliseconds.
        Returns True if the piece should auto-lock.
        """
        if self.game_over or self.paused:
            return False

        self.last_fall_time += dt

        # Check if piece should fall
        if self.last_fall_time >= self.fall_speed:
            self.last_fall_time = 0

            if not self.move_piece(0, 1):
                # Can't move down, start lock delay
                self.lock_timer += self.fall_speed

                if self.lock_timer >= self.lock_delay:
                    self._lock_piece()
                    return True

        return False

    def get_state(self) -> list:
        """Get the current grid state for AI agents."""
        return [[cell if cell is not None else 0 for cell in row] for row in self.grid]

    def get_action_result(self, action: int) -> tuple:
        """
        Execute an action and return (reward, done).
        Actions: 0=left, 1=right, 2=down, 3=rotate, 4=drop, 5=hold
        """
        if self.game_over:
            return 0, True

        old_lines = self.lines_cleared

        if action == 0:
            success = self.move_piece(-1, 0)
            reward = 0.1 if success else -0.1
        elif action == 1:
            success = self.move_piece(1, 0)
            reward = 0.1 if success else -0.1
        elif action == 2:
            success = self.soft_drop()
            reward = 1.0 if success else -0.1
        elif action == 3:
            success = self.rotate_piece()
            reward = 0.1 if success else -0.1
        elif action == 4:
            drop_distance = self.hard_drop()
            reward = drop_distance * 2.0
        elif action == 5:
            success = self.hold()
            reward = 0.1 if success else 0
        else:
            reward = 0

        # Line clear bonus
        new_lines = self.lines_cleared - old_lines
        if new_lines > 0:
            reward += new_lines * 100

        return reward, self.game_over
