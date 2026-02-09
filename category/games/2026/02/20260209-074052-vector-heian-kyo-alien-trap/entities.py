"""Game entities for Heian-Kyo Alien Trap."""

from typing import List, Tuple, Optional, Set
from enum import Enum
import random
from config import *


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class Alien:
    """Represents an alien enemy."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.in_hole = False
        self.hole_time = 0  # Time spent in hole
        self.is_buried = False
        self.move_timer = 0
        self.pursuit_mode = False

    def update(self, player_row: int, player_col: int, walls: Set[Tuple[int, int]],
               holes: Set[Tuple[int, int]], grid_rows: int, grid_cols: int) -> None:
        """Update alien AI movement."""
        if self.in_hole:
            self.hole_time += 1
            return

        self.move_timer += 1
        if self.move_timer < ALIEN_MOVE_INTERVAL:
            return

        self.move_timer = 0

        # Simple AI: sometimes move randomly, sometimes pursue player
        if random.random() < 0.6:
            self._move_randomly(walls, holes, grid_rows, grid_cols)
        else:
            self._move_toward_player(player_row, player_col, walls, holes, grid_rows, grid_cols)

    def _move_randomly(self, walls: Set[Tuple[int, int]], holes: Set[Tuple[int, int]],
                      grid_rows: int, grid_cols: int) -> None:
        """Move in a random valid direction."""
        directions = list(Direction)
        random.shuffle(directions)

        for direction in directions:
            dr, dc = direction.value
            new_row = self.row + dr
            new_col = self.col + dc

            if (0 <= new_row < grid_rows and 0 <= new_col < grid_cols and
                (new_row, new_col) not in walls and (new_row, new_col) not in holes):
                self.row = new_row
                self.col = new_col
                return

    def _move_toward_player(self, player_row: int, player_col: int,
                           walls: Set[Tuple[int, int]], holes: Set[Tuple[int, int]],
                           grid_rows: int, grid_cols: int) -> None:
        """Move toward the player if possible."""
        dr = player_row - self.row
        dc = player_col - self.col

        # Choose primary direction
        if abs(dr) > abs(dc):
            directions = [Direction.UP if dr < 0 else Direction.DOWN,
                         Direction.LEFT if dc < 0 else Direction.RIGHT]
        else:
            directions = [Direction.LEFT if dc < 0 else Direction.RIGHT,
                         Direction.UP if dr < 0 else Direction.DOWN]

        for direction in directions:
            ddr, ddc = direction.value
            new_row = self.row + ddr
            new_col = self.col + ddc

            if (0 <= new_row < grid_rows and 0 <= new_col < grid_cols and
                (new_row, new_col) not in walls and (new_row, new_col) not in holes):
                self.row = new_row
                self.col = new_col
                return

    def should_escape(self) -> bool:
        """Check if alien should escape from hole."""
        return self.in_hole and self.hole_time >= ALIEN_ESCAPE_TIME


class GameState:
    """Represents the current state of the game."""

    def __init__(self, level: int = 1):
        self.level = level
        self.lives = 3
        self.score = 0
        self.total_reward = 0.0
        self.game_over = False
        self.level_complete = False

        # Grid state
        self.grid_rows = GRID_ROWS
        self.grid_cols = GRID_COLS
        self.walls: Set[Tuple[int, int]] = set()
        self.holes: Set[Tuple[int, int]] = set()

        # Player state
        self.player_row = 1
        self.player_col = 1
        self.action_progress = 0  # 0 = idle, 1-DIG_TIME = digging/filling
        self.current_action = None  # 'dig' or 'fill' or None
        self.action_pos = None  # Position where action is being performed

        # Aliens
        self.aliens: List[Alien] = []

        self._load_level(level)

    def _load_level(self, level: int) -> None:
        """Load a level based on difficulty."""
        self.walls.clear()
        self.holes.clear()
        self.aliens.clear()

        # Create border walls
        for r in range(self.grid_rows):
            self.walls.add((r, 0))
            self.walls.add((r, self.grid_cols - 1))
        for c in range(self.grid_cols):
            self.walls.add((0, c))
            self.walls.add((self.grid_rows - 1, c))

        # Add internal walls (more walls in higher levels)
        num_internal_walls = 10 + level * 3
        for _ in range(num_internal_walls):
            while True:
                r = random.randint(2, self.grid_rows - 3)
                c = random.randint(2, self.grid_cols - 3)
                if (r, c) not in self.walls and (r, c) != (1, 1):
                    self.walls.add((r, c))
                    break

        # Spawn player at safe position
        self.player_row = 1
        self.player_col = 1

        # Spawn aliens (more aliens in higher levels)
        num_aliens = 3 + level * 2
        for _ in range(num_aliens):
            while True:
                r = random.randint(2, self.grid_rows - 3)
                c = random.randint(2, self.grid_cols - 3)
                if ((r, c) not in self.walls and
                    abs(r - self.player_row) + abs(c - self.player_col) > 5):
                    self.aliens.append(Alien(r, c))
                    break

    def get_valid_actions(self) -> List[int]:
        """Get list of valid actions from current state."""
        actions = [ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT]

        # Can dig if not currently acting and at valid position
        if self.action_progress == 0:
            r, c = self.player_row, self.player_col
            if (r, c) not in self.holes and (r, c) not in self.walls:
                actions.append(ACTION_DIG)

        # Can fill if adjacent to a hole
        if self.action_progress == 0:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = self.player_row + dr, self.player_col + dc
                if (nr, nc) in self.holes:
                    actions.append(ACTION_FILL)
                    break

        return actions

    def step(self, action: int) -> Tuple[bool, float]:
        """Execute an action. Returns (done, reward)."""
        if self.game_over or self.level_complete:
            return True, 0.0

        reward = PENALTY_STEP

        # If currently digging/filling, continue the action
        if self.action_progress > 0:
            self.action_progress += 1
            if self.action_progress >= DIG_TIME:
                self._complete_action()
            self._update_aliens()
            self._check_collisions()
            return False, reward

        # Handle new actions
        if action == ACTION_UP:
            self._move_player(-1, 0)
        elif action == ACTION_DOWN:
            self._move_player(1, 0)
        elif action == ACTION_LEFT:
            self._move_player(0, -1)
        elif action == ACTION_RIGHT:
            self._move_player(0, 1)
        elif action == ACTION_DIG:
            r, c = self.player_row, self.player_col
            if (r, c) not in self.holes and (r, c) not in self.walls:
                self.current_action = 'dig'
                self.action_pos = (r, c)
                self.action_progress = 1
        elif action == ACTION_FILL:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = self.player_row + dr, self.player_col + dc
                if (nr, nc) in self.holes:
                    self.current_action = 'fill'
                    self.action_pos = (nr, nc)
                    self.action_progress = 1
                    break

        self._update_aliens()
        done, collision_reward = self._check_collisions()
        reward += collision_reward

        return done, reward

    def _move_player(self, dr: int, dc: int) -> None:
        """Move player in given direction."""
        new_row = self.player_row + dr
        new_col = self.player_col + dc

        if ((0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_cols) and
            (new_row, new_col) not in self.walls and
            (new_row, new_col) not in self.holes):
            self.player_row = new_row
            self.player_col = new_col

    def _complete_action(self) -> None:
        """Complete the current dig/fill action."""
        if self.current_action == 'dig' and self.action_pos:
            self.holes.add(self.action_pos)
        elif self.current_action == 'fill' and self.action_pos:
            # Check if there's an alien in the hole
            for alien in self.aliens:
                if (alien.row, alien.col) == self.action_pos and alien.in_hole:
                    alien.is_buried = True
                    self.score += 500
                    self.total_reward += REWARD_BURY_ALIEN
            self.holes.discard(self.action_pos)

        self.current_action = None
        self.action_pos = None
        self.action_progress = 0

    def _update_aliens(self) -> None:
        """Update all aliens."""
        for alien in self.aliens:
            if alien.is_buried:
                continue

            alien.update(self.player_row, self.player_col, self.walls, self.holes,
                        self.grid_rows, self.grid_cols)

            # Check if alien falls into a hole
            if (alien.row, alien.col) in self.holes and not alien.in_hole:
                alien.in_hole = True
                self.score += 100
                self.total_reward += REWARD_TRAP_ALIEN

            # Check if alien escapes
            if alien.should_escape():
                alien.in_hole = False
                alien.hole_time = 0
                # Move alien out of hole
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = alien.row + dr, alien.col + dc
                    if ((0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols) and
                        (nr, nc) not in self.walls and (nr, nc) not in self.holes):
                        alien.row = nr
                        alien.col = nc
                        break

    def _check_collisions(self) -> Tuple[bool, float]:
        """Check for collisions with aliens."""
        for alien in self.aliens:
            if alien.is_buried:
                continue

            if alien.row == self.player_row and alien.col == self.player_col:
                self.lives -= 1
                self.total_reward += PENALTY_DEATH

                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Respawn player at start
                    self.player_row = 1
                    self.player_col = 1
                    # Reset current action
                    self.action_progress = 0
                    self.current_action = None
                    self.action_pos = None

                return True, PENALTY_DEATH

        # Check win condition (all aliens buried)
        if all(alien.is_buried for alien in self.aliens):
            self.level_complete = True
            self.total_reward += REWARD_WIN
            return True, REWARD_WIN

        return False, 0.0

    def get_state(self) -> List[List[int]]:
        """Get the current grid state for AI agents."""
        state = [[STATE_EMPTY for _ in range(self.grid_cols)]
                for _ in range(self.grid_rows)]

        # Place walls
        for r, c in self.walls:
            state[r][c] = STATE_WALL

        # Place holes
        for r, c in self.holes:
            state[r][c] = STATE_HOLE

        # Place aliens
        for alien in self.aliens:
            if not alien.is_buried:
                if alien.in_hole:
                    state[alien.row][alien.col] = STATE_HOLE_WITH_ALIEN
                else:
                    state[alien.row][alien.col] = STATE_ALIEN

        # Place player
        state[self.player_row][self.player_col] = STATE_PLAYER

        return state

    def reset(self) -> None:
        """Reset the current level."""
        self.score = 0
        self.total_reward = 0.0
        self.game_over = False
        self.level_complete = False
        self.lives = 3
        self.action_progress = 0
        self.current_action = None
        self.action_pos = None
        self._load_level(self.level)

    def next_level(self) -> None:
        """Advance to the next level."""
        self.level += 1
        self.reset()
