"""
Diamond Mine Puzzle Classic - Boulder Dash style grid-based puzzle game.
Collect diamonds while avoiding falling boulders. AI-friendly with clear state space.
"""

import os
import pygame
import sys
from enum import Enum
from typing import List, Tuple, Optional, Dict


class TileType(Enum):
    EMPTY = 0
    WALL = 1
    DIRT = 2
    DIAMOND = 3
    BOULDER = 4
    PLAYER = 5
    EXIT = 6
    EXIT_OPEN = 7


class Action(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    NONE = 4


class DiamondMineGame:
    """
    Diamond Mine Puzzle - Boulder Dash style game.

    Grid: 20x15 cells
    Player moves through dirt, collects diamonds, avoids falling boulders.
    Exit opens when all diamonds are collected.

    State representation:
    - 2D grid of TileType values
    - Player position
    - Diamonds collected/total
    - Game state (playing, won, lost)

    Actions: 4 discrete moves (UP, DOWN, LEFT, RIGHT)

    Rewards:
    - +50: Collect diamond
    - +500: Reach exit
    - -1: Each step
    - -1000: Death by boulder or trap
    """

    # Game constants
    GRID_WIDTH = 20
    GRID_HEIGHT = 15
    TILE_SIZE = 32
    WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
    WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE + 40  # Extra space for HUD
    FPS = 30

    # Colors
    COLOR_BG = (20, 15, 10)
    COLOR_WALL = (100, 100, 100)
    COLOR_DIRT = (139, 90, 43)
    COLOR_DIAMOND = (0, 200, 255)
    COLOR_BOULDER = (139, 69, 19)
    COLOR_PLAYER = (255, 200, 0)
    COLOR_EXIT = (100, 50, 100)
    COLOR_EXIT_OPEN = (0, 200, 50)
    COLOR_TEXT = (220, 220, 220)

    def __init__(self, render: bool = True):
        """
        Initialize the game.

        Args:
            render: If False, run in headless mode for AI training
        """
        self.render = render
        if self.render:
            pygame.init()
            pygame.display.set_caption("Diamond Mine Puzzle")
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 28)
        else:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.init()
            pygame.display.set_mode((1, 1))

        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.grid = [[TileType.EMPTY for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.player_x = 1
        self.player_y = 1
        self.diamonds_total = 0
        self.diamonds_collected = 0
        self.score = 0
        self.steps = 0
        self.game_over = False
        self.victory = False
        self.falling_boulders: List[Tuple[int, int]] = []

        self._generate_level()

    def _generate_level(self) -> None:
        """Generate a playable level with walls, dirt, diamonds, and boulders."""
        # Border walls
        for x in range(self.GRID_WIDTH):
            self.grid[0][x] = TileType.WALL
            self.grid[self.GRID_HEIGHT - 1][x] = TileType.WALL
        for y in range(self.GRID_HEIGHT):
            self.grid[y][0] = TileType.WALL
            self.grid[y][self.GRID_WIDTH - 1] = TileType.WALL

        # Place exit in bottom-right area
        self.grid[self.GRID_HEIGHT - 2][self.GRID_WIDTH - 2] = TileType.EXIT

        # Fill with dirt, diamonds, and boulders
        self.diamonds_total = 0
        for y in range(2, self.GRID_HEIGHT - 2):
            for x in range(2, self.GRID_WIDTH - 2):
                # Keep player start area clear
                if x < 4 and y < 4:
                    continue

                # Keep exit area clear
                if x > self.GRID_WIDTH - 5 and y > self.GRID_HEIGHT - 5:
                    continue

                rand = (x * 17 + y * 13) % 100
                if rand < 8:
                    self.grid[y][x] = TileType.DIAMOND
                    self.diamonds_total += 1
                elif rand < 20:
                    self.grid[y][x] = TileType.BOULDER
                elif rand < 90:
                    self.grid[y][x] = TileType.DIRT

        # Ensure minimum diamonds
        while self.diamonds_total < 5:
            for _ in range(5):
                x = 5 + (self.diamonds_total * 3) % (self.GRID_WIDTH - 10)
                y = 3 + (self.diamonds_total * 5) % (self.GRID_HEIGHT - 6)
                if self.grid[y][x] == TileType.DIRT:
                    self.grid[y][x] = TileType.DIAMOND
                    self.diamonds_total += 1

    def get_tile(self, x: int, y: int) -> TileType:
        """Get tile type at position, treating player position as PLAYER."""
        if x == self.player_x and y == self.player_y:
            return TileType.PLAYER
        return self.grid[y][x]

    def set_tile(self, x: int, y: int, tile: TileType) -> None:
        """Set tile type at position."""
        self.grid[y][x] = tile

    def is_empty(self, x: int, y: int) -> bool:
        """Check if position is empty (no wall, dirt, diamond, boulder, or player)."""
        if not (0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT):
            return False
        tile = self.get_tile(x, y)
        return tile == TileType.EMPTY or tile == TileType.EXIT_OPEN

    def step(self, action: Action) -> Tuple[int, bool, int]:
        """
        Execute one game step.

        Args:
            action: Action to take

        Returns:
            Tuple of (reward, done, score)
        """
        if self.game_over:
            return 0, True, self.score

        reward = 0
        self.steps += 1

        # Process player movement
        if action != Action.NONE:
            dx, dy = self._get_direction_delta(action)
            new_x = self.player_x + dx
            new_y = self.player_y + dy

            if self._can_move_to(new_x, new_y):
                reward += self._move_to(new_x, new_y)

        # Apply gravity to boulders
        self._apply_gravity()

        # Update falling boulder tracking and check for death
        reward += self._check_boulder_death()

        # Step penalty
        reward -= 1

        # Check victory condition
        if self.victory:
            self.game_over = True
            reward += 500

        return reward, self.game_over, self.score

    def _get_direction_delta(self, action: Action) -> Tuple[int, int]:
        """Get delta for movement direction."""
        deltas = {
            Action.UP: (0, -1),
            Action.DOWN: (0, 1),
            Action.LEFT: (-1, 0),
            Action.RIGHT: (1, 0),
            Action.NONE: (0, 0)
        }
        return deltas.get(action, (0, 0))

    def _can_move_to(self, x: int, y: int) -> bool:
        """Check if player can move to position."""
        if not (0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT):
            return False

        tile = self.grid[y][x]

        if tile == TileType.WALL:
            return False

        if tile == TileType.BOULDER:
            # Check if we can push it
            dx = x - self.player_x
            if dx == 0:  # Can't push up/down
                return False
            push_x = x + dx
            return self.is_empty(push_x, y)

        if tile == TileType.EXIT:
            return self.diamonds_collected >= self.diamonds_total

        if tile == TileType.DIRT or tile == TileType.DIAMOND or tile == TileType.EMPTY:
            return True

        return False

    def _move_to(self, x: int, y: int) -> int:
        """Move player to new position, returns reward gained."""
        reward = 0
        tile = self.grid[y][x]

        # Handle boulder push
        if tile == TileType.BOULDER:
            dx = x - self.player_x
            push_x = x + dx
            self.grid[y][push_x] = TileType.BOULDER
            self.grid[y][x] = TileType.EMPTY

        # Collect diamond
        if tile == TileType.DIAMOND:
            self.diamonds_collected += 1
            self.score += 50
            reward += 50

            # Open exit if all diamonds collected
            if self.diamonds_collected >= self.diamonds_total:
                self._open_exit()

        # Remove dirt
        if tile == TileType.DIRT:
            self.grid[y][x] = TileType.EMPTY

        # Check for exit
        if tile == TileType.EXIT and self.diamonds_collected >= self.diamonds_total:
            self.victory = True

        # Move player
        self.player_x = x
        self.player_y = y

        return reward

    def _open_exit(self) -> None:
        """Open the exit door."""
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if self.grid[y][x] == TileType.EXIT:
                    self.grid[y][x] = TileType.EXIT_OPEN

    def _apply_gravity(self) -> None:
        """Apply gravity to boulders."""
        self.falling_boulders.clear()
        moved = True

        # Process from bottom to top, handle falling
        for _ in range(2):  # Two passes for proper falling
            for y in range(self.GRID_HEIGHT - 2, 0, -1):
                for x in range(1, self.GRID_WIDTH - 1):
                    if self.grid[y][x] == TileType.BOULDER:
                        # Check if can fall straight down
                        if self._is_fallable(x, y + 1):
                            self.grid[y][x] = TileType.EMPTY
                            self.grid[y + 1][x] = TileType.BOULDER
                            self.falling_boulders.append((x, y + 1))
                        # Check if can roll off another boulder
                        elif self.grid[y + 1][x] in (TileType.BOULDER, TileType.WALL, TileType.DIAMOND):
                            # Roll right
                            if (self._is_fallable(x + 1, y) and
                                self._is_fallable(x + 1, y + 1)):
                                self.grid[y][x] = TileType.EMPTY
                                self.grid[y][x + 1] = TileType.BOULDER
                            # Roll left
                            elif (self._is_fallable(x - 1, y) and
                                  self._is_fallable(x - 1, y + 1)):
                                self.grid[y][x] = TileType.EMPTY
                                self.grid[y][x - 1] = TileType.BOULDER

    def _is_fallable(self, x: int, y: int) -> bool:
        """Check if a boulder can fall into this position."""
        if not (0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT):
            return False
        tile = self.grid[y][x]
        return tile == TileType.EMPTY or (
            tile == TileType.EXIT_OPEN and x != self.player_x and y != self.player_y
        )

    def _check_boulder_death(self) -> int:
        """Check if player was crushed by a falling boulder."""
        for bx, by in self.falling_boulders:
            if bx == self.player_x and by == self.player_y:
                self.game_over = True
                self.victory = False
                return -1000
        return 0

    def get_state(self) -> Dict:
        """Get current game state as a dictionary."""
        return {
            'grid': [[t.value for t in row] for row in self.grid],
            'player': (self.player_x, self.player_y),
            'diamonds_collected': self.diamonds_collected,
            'diamonds_total': self.diamonds_total,
            'score': self.score,
            'steps': self.steps,
            'game_over': self.game_over,
            'victory': self.victory
        }

    def get_grid_state(self) -> List[List[int]]:
        """
        Get game state as a 2D grid.
        Returns:
            2D array of TileType values with player position included.
        """
        grid_state = [[t.value for t in row] for row in self.grid]
        if 0 <= self.player_y < self.GRID_HEIGHT and 0 <= self.player_x < self.GRID_WIDTH:
            grid_state[self.player_y][self.player_x] = TileType.PLAYER.value
        return grid_state

    def draw(self) -> None:
        """Render the game state."""
        if not self.render:
            return

        # Background
        self.screen.fill(self.COLOR_BG)

        # Draw grid
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                rect = pygame.Rect(
                    x * self.TILE_SIZE,
                    y * self.TILE_SIZE + 40,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )

                tile = self.get_tile(x, y)

                if tile == TileType.WALL:
                    pygame.draw.rect(self.screen, self.COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, (80, 80, 80), rect, 2)

                elif tile == TileType.DIRT:
                    pygame.draw.rect(self.screen, self.COLOR_DIRT, rect, border_radius=4)
                    # Add texture
                    pygame.draw.circle(self.screen, (120, 80, 35),
                                     (x * self.TILE_SIZE + 10, y * self.TILE_SIZE + 50), 3)

                elif tile == TileType.DIAMOND:
                    pygame.draw.rect(self.screen, self.COLOR_DIRT, rect, border_radius=4)
                    center = (x * self.TILE_SIZE + self.TILE_SIZE // 2,
                             y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2)
                    points = [
                        (center[0], center[1] - 10),
                        (center[0] + 8, center[1]),
                        (center[0], center[1] + 10),
                        (center[0] - 8, center[1])
                    ]
                    pygame.draw.polygon(self.screen, self.COLOR_DIAMOND, points)

                elif tile == TileType.BOULDER:
                    pygame.draw.rect(self.screen, self.COLOR_DIRT, rect, border_radius=4)
                    pygame.draw.circle(self.screen, self.COLOR_BOULDER,
                                     (x * self.TILE_SIZE + self.TILE_SIZE // 2,
                                      y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2),
                                     self.TILE_SIZE // 2 - 4)
                    pygame.draw.circle(self.screen, (100, 50, 10),
                                     (x * self.TILE_SIZE + self.TILE_SIZE // 2 - 4,
                                      y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2 - 4),
                                     4)

                elif tile == TileType.EXIT:
                    pygame.draw.rect(self.screen, self.COLOR_EXIT, rect)
                    pygame.draw.rect(self.screen, (150, 100, 150),
                                   (rect.x + 6, rect.y + 6, rect.width - 12, rect.height - 12), 3)

                elif tile == TileType.EXIT_OPEN:
                    pygame.draw.rect(self.screen, self.COLOR_EXIT_OPEN, rect)
                    pygame.draw.line(self.screen, (255, 255, 255),
                                   (rect.x + 6, rect.y + 6), (rect.x + rect.width - 6, rect.y + rect.height - 6), 3)

                elif tile == TileType.PLAYER:
                    pygame.draw.circle(self.screen, self.COLOR_PLAYER,
                                      (x * self.TILE_SIZE + self.TILE_SIZE // 2,
                                       y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2),
                                      self.TILE_SIZE // 2 - 2)
                    # Eyes
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                     (x * self.TILE_SIZE + self.TILE_SIZE // 2 - 5,
                                      y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2 - 3), 2)
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                     (x * self.TILE_SIZE + self.TILE_SIZE // 2 + 5,
                                      y * self.TILE_SIZE + 40 + self.TILE_SIZE // 2 - 3), 2)

        # Draw HUD
        pygame.draw.rect(self.screen, (30, 25, 20), (0, 0, self.WINDOW_WIDTH, 40))

        diamonds_text = self.font.render(
            f"Diamonds: {self.diamonds_collected}/{self.diamonds_total}",
            True, self.COLOR_TEXT
        )
        self.screen.blit(diamonds_text, (10, 6))

        score_text = self.font.render(f"Score: {self.score}", True, self.COLOR_TEXT)
        self.screen.blit(score_text, (self.WINDOW_WIDTH - 150, 6))

        if self.game_over:
            if self.victory:
                msg = "VICTORY!"
                color = (0, 200, 50)
            else:
                msg = "GAME OVER"
                color = (220, 50, 50)

            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            text = self.font.render(msg, True, color)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
            self.screen.blit(text, text_rect)

            restart_text = self.font.render("Press R to restart, ESC to quit", True, self.COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def handle_input(self) -> Action:
        """Handle keyboard input for human control."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    return Action.UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    return Action.DOWN
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    return Action.LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    return Action.RIGHT
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        return Action.NONE

    def run(self) -> None:
        """Main game loop for human play."""
        while True:
            action = self.handle_input()
            self.step(action)
            self.draw()
            self.clock.tick(self.FPS)


def main():
    """Entry point for running the game."""
    game = DiamondMineGame(render=True)
    game.run()


if __name__ == "__main__":
    main()
