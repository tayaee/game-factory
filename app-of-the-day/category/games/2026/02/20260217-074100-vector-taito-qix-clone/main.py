"""
Vector Taito Qix Clone - Territory capture arcade game.
Capture territory by drawing lines while avoiding the unpredictable spark.
AI-friendly with clear state space for reinforcement learning.
"""

import os
import pygame
import sys
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set


class CellType(Enum):
    EMPTY = 0
    CAPTURED = 1
    PLAYER = 2
    LINE = 3


class Action(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    DRAW_HOLD = 4
    DRAW_RELEASE = 5
    NONE = 6


class QixGame:
    """
    Qix Clone - Territory capture arcade game.

    Field: 600x600 pixels with 60x60 grid
    Player moves along edges, draws lines (Stix) into empty space.
    Complete a loop to capture the enclosed area.
    Qix wanders randomly inside empty space - destroys incomplete lines.
    Sparx move along edges - chase the player.
    Win by capturing 75% of the field.

    State representation:
    - 2D grid of CellType values
    - Player position and direction
    - Current line being drawn (if any)
    - Qix position and velocity
    - Sparx positions and directions

    Actions: 6 discrete actions (4 moves + draw hold/release)

    Rewards:
    - +Area size * speed_factor: Successfully capture area
    - -100: Lose a life
    - +1000: Win level
    - -1: Each step (to encourage efficiency)
    """

    # Game constants
    FIELD_SIZE = 600
    GRID_SIZE = 60  # 60x60 cells
    CELL_SIZE = FIELD_SIZE // GRID_SIZE
    WINDOW_WIDTH = FIELD_SIZE + 200  # Extra space for HUD
    WINDOW_HEIGHT = FIELD_SIZE + 60
    FPS = 60
    WIN_PERCENTAGE = 75

    # Colors
    COLOR_BG = (10, 10, 20)
    COLOR_CAPTURED = (50, 50, 150)
    COLOR_EMPTY = (10, 10, 20)
    COLOR_LINE = (0, 255, 255)
    COLOR_PLAYER = (255, 255, 0)
    COLOR_QIX = (255, 50, 50)
    COLOR_SPARX = (255, 150, 0)
    COLOR_TEXT = (220, 220, 220)
    COLOR_HUD_BG = (30, 30, 40)

    def __init__(self, render: bool = True):
        """
        Initialize the game.

        Args:
            render: If False, run in headless mode for AI training
        """
        self.render = render
        if self.render:
            pygame.init()
            pygame.display.set_caption("Qix Clone")
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 28)
            self.large_font = pygame.font.Font(None, 48)
        else:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.init()
            pygame.display.set_mode((1, 1))

        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Initialize grid - outer border is captured
        self.grid = [[CellType.EMPTY for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        for x in range(self.GRID_SIZE):
            self.grid[0][x] = CellType.CAPTURED
            self.grid[self.GRID_SIZE - 1][x] = CellType.CAPTURED
        for y in range(self.GRID_SIZE):
            self.grid[y][0] = CellType.CAPTURED
            self.grid[y][self.GRID_SIZE - 1] = CellType.CAPTURED

        # Player starts on the border
        self.player_pos = [self.GRID_SIZE // 2, 0]  # [x, y]
        self.player_dir = Action.RIGHT

        # Drawing state
        self.drawing = False
        self.current_line: List[Tuple[int, int]] = []

        # Qix (the wandering enemy)
        self.qix_pos = [self.GRID_SIZE // 2, self.GRID_SIZE // 2]
        self.qix_vel = [2, 1]
        self.qix_speed = 3

        # Sparx (edge chasers)
        self.sparx1_pos = [self.GRID_SIZE - 2, 0]
        self.sparx1_dir = Action.LEFT
        self.sparx2_pos = [1, self.GRID_SIZE - 2]
        self.sparx2_dir = Action.RIGHT
        self.sparx_speed = 2

        # Game state
        self.score = 0
        self.captured_area = 0
        self.total_cells = (self.GRID_SIZE - 2) ** 2
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.victory = False
        self.steps = 0

        # Update captured area count
        self._update_captured_area()

    def _update_captured_area(self) -> None:
        """Count captured cells."""
        count = 0
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.grid[y][x] == CellType.CAPTURED:
                    count += 1
        self.captured_area = count

    def _get_captured_percentage(self) -> float:
        """Get percentage of field captured."""
        return (self.captured_area / self.total_cells) * 100

    def _is_on_border(self, x: int, y: int) -> bool:
        """Check if position is on the captured border."""
        return (self.grid[y][x] == CellType.CAPTURED and
                (x == 0 or x == self.GRID_SIZE - 1 or
                 y == 0 or y == self.GRID_SIZE - 1))

    def _is_on_captured_area(self, x: int, y: int) -> bool:
        """Check if position is on any captured area."""
        return self.grid[y][x] == CellType.CAPTURED

    def _is_empty(self, x: int, y: int) -> bool:
        """Check if position is in empty space."""
        return self.grid[y][x] == CellType.EMPTY

    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring positions."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE:
                neighbors.append((nx, ny))
        return neighbors

    def _flood_fill_empty(self, start_x: int, start_y: int) -> Set[Tuple[int, int]]:
        """Find all empty cells connected to the given position."""
        visited = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
                continue
            if self.grid[y][x] != CellType.EMPTY:
                continue

            visited.add((x, y))

            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited:
                    stack.append((nx, ny))

        return visited

    def _flood_fill_capture(self, start_x: int, start_y: int) -> Set[Tuple[int, int]]:
        """Find all captured cells connected to the border."""
        visited = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
                continue
            if self.grid[y][x] != CellType.CAPTURED:
                continue

            visited.add((x, y))

            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited:
                    stack.append((nx, ny))

        return visited

    def _complete_capture(self) -> int:
        """
        Process completed capture using flood fill.
        Returns the number of cells captured.
        """
        if not self.current_line:
            return 0

        # Mark the line as captured
        for x, y in self.current_line:
            if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
                self.grid[y][x] = CellType.CAPTURED

        # Find all empty regions
        empty_regions = []
        processed = set()

        for y in range(1, self.GRID_SIZE - 1):
            for x in range(1, self.GRID_SIZE - 1):
                if self.grid[y][x] == CellType.EMPTY and (x, y) not in processed:
                    region = self._flood_fill_empty(x, y)
                    empty_regions.append(region)
                    processed.update(region)

        # Check which region contains the Qix
        qix_cell = (int(self.qix_pos[0] // self.CELL_SIZE),
                    int(self.qix_pos[1] // self.CELL_SIZE))

        qix_region = None
        for region in empty_regions:
            if qix_cell in region:
                qix_region = region
                break

        # Capture all regions except the one containing the Qix
        cells_captured = 0
        for region in empty_regions:
            if region != qix_region:
                for x, y in region:
                    self.grid[y][x] = CellType.CAPTURED
                    cells_captured += 1

        # Clear the current line
        self.current_line.clear()

        # Update captured area
        self._update_captured_area()

        # Check win condition
        if self._get_captured_percentage() >= self.WIN_PERCENTAGE:
            self.victory = True
            self.game_over = True

        return cells_captured

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

        # Handle drawing modifier
        if action == Action.DRAW_HOLD:
            if not self.drawing and self._is_on_captured_area(*self.player_pos):
                self.drawing = True
                # Add current position as starting point of the line
                self.current_line.append((self.player_pos[0], self.player_pos[1]))
        elif action == Action.DRAW_RELEASE:
            if self.drawing:
                # Try to complete the capture if on captured area
                if self._is_on_captured_area(*self.player_pos):
                    cells = self._complete_capture()
                    if cells > 0:
                        points = cells * self.level
                        self.score += points
                        reward += points
                else:
                    # Lost a life - didn't complete the line
                    self.lives -= 1
                    reward -= 100
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self._reset_player_position()
                self.current_line.clear()
                self.drawing = False

        # Handle movement
        dx, dy = self._get_direction_delta(action)
        if dx != 0 or dy != 0:
            self.player_dir = action

            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy

            # Check bounds
            if not (0 <= new_x < self.GRID_SIZE and 0 <= new_y < self.GRID_SIZE):
                return reward - 1, self.game_over, self.score

            # Check if we can move there
            target_cell = self.grid[new_y][new_x]

            if self.drawing:
                # Drawing mode - can draw into empty space or return to captured area
                if target_cell == CellType.EMPTY:
                    # Check if not crossing our own line
                    if (new_x, new_y) not in self.current_line:
                        self.current_line.append((new_x, new_y))
                        self.player_pos = [new_x, new_y]
                elif target_cell == CellType.CAPTURED:
                    # Reached captured area - move there and can complete the capture
                    self.player_pos = [new_x, new_y]
                    # Add the border point to complete the line loop
                    self.current_line.append((new_x, new_y))
            else:
                # Normal mode - can only move on captured area
                if target_cell == CellType.CAPTURED:
                    self.player_pos = [new_x, new_y]

        # Update Qix (only moves every few frames for better control)
        if self.steps % 3 == 0:
            self._update_qix()

        # Update Sparx
        self._update_sparx()

        # Check Qix collision with current line
        if self.drawing:
            if self._check_qix_line_collision():
                self.lives -= 1
                reward -= 100
                self.current_line.clear()
                self.drawing = False
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self._reset_player_position()

        # Check Sparx collision with player
        if self._check_sparx_collision():
            self.lives -= 1
            reward -= 100
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_player_position()

        # Step penalty
        reward -= 1

        # Victory reward
        if self.victory:
            reward += 1000

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

    def _update_qix(self) -> None:
        """Update Qix position with random wandering."""
        # Qix moves in pixel coordinates for smooth motion
        speed = self.qix_speed

        # Randomly change direction
        if self.steps % 10 == 0:
            if self.steps % 20 == 0:
                self.qix_vel[0] = (self.qix_vel[0] + 1) % 5 - 2
            else:
                self.qix_vel[1] = (self.qix_vel[1] + 1) % 5 - 2

        # Normalize and apply speed
        mag = (self.qix_vel[0]**2 + self.qix_vel[1]**2) ** 0.5
        if mag > 0:
            self.qix_vel[0] = int(self.qix_vel[0] / mag * speed)
            self.qix_vel[1] = int(self.qix_vel[1] / mag * speed)

        new_x = self.qix_pos[0] + self.qix_vel[0]
        new_y = self.qix_pos[1] + self.qix_vel[1]

        # Check bounds (stay in field, accounting for border)
        cell_size_px = self.CELL_SIZE
        if new_x < cell_size_px or new_x >= self.FIELD_SIZE - cell_size_px:
            self.qix_vel[0] *= -1
            new_x = max(cell_size_px, min(new_x, self.FIELD_SIZE - cell_size_px - 1))
        if new_y < cell_size_px or new_y >= self.FIELD_SIZE - cell_size_px:
            self.qix_vel[1] *= -1
            new_y = max(cell_size_px, min(new_y, self.FIELD_SIZE - cell_size_px - 1))

        # Check collision with captured area
        cell_x = int(new_x // cell_size_px)
        cell_y = int(new_y // cell_size_px)

        if (0 <= cell_x < self.GRID_SIZE and
            0 <= cell_y < self.GRID_SIZE and
            self.grid[cell_y][cell_x] == CellType.CAPTURED):
            # Bounce off captured area
            self.qix_vel[0] *= -1
            self.qix_vel[1] *= -1
        else:
            self.qix_pos = [new_x, new_y]

    def _update_sparx(self) -> None:
        """Update Sparx positions along the border."""
        for _ in range(self.sparx_speed):
            # Update first Sparx
            dx1, dy1 = self._get_direction_delta(self.sparx1_dir)
            new_x1 = self.sparx1_pos[0] + dx1
            new_y1 = self.sparx1_pos[1] + dy1

            # Sparx stays on the outer border
            if new_x1 <= 0:
                self.sparx1_dir = Action.RIGHT
                new_x1 = 0
            elif new_x1 >= self.GRID_SIZE - 1:
                self.sparx1_dir = Action.LEFT
                new_x1 = self.GRID_SIZE - 1

            if self.sparx1_pos[1] == 0:
                # Moving along top edge
                self.sparx1_pos = [new_x1, 0]
            elif self.sparx1_pos[1] == self.GRID_SIZE - 1:
                # Moving along bottom edge
                self.sparx1_pos = [new_x1, self.GRID_SIZE - 1]

            # Update second Sparx
            dx2, dy2 = self._get_direction_delta(self.sparx2_dir)
            new_x2 = self.sparx2_pos[0] + dx2
            new_y2 = self.sparx2_pos[1] + dy2

            if new_x2 <= 0:
                self.sparx2_dir = Action.RIGHT
                new_x2 = 0
            elif new_x2 >= self.GRID_SIZE - 1:
                self.sparx2_dir = Action.LEFT
                new_x2 = self.GRID_SIZE - 1

            if self.sparx2_pos[1] == self.GRID_SIZE - 1:
                # Moving along bottom edge
                self.sparx2_pos = [new_x2, self.GRID_SIZE - 1]
            elif self.sparx2_pos[1] == 0:
                # Moving along top edge
                self.sparx2_pos = [new_x2, 0]

    def _check_qix_line_collision(self) -> bool:
        """Check if Qix collides with the current line."""
        qix_cell_x = int(self.qix_pos[0] // self.CELL_SIZE)
        qix_cell_y = int(self.qix_pos[1] // self.CELL_SIZE)

        # Check collision with any point in the current line
        for line_x, line_y in self.current_line:
            if abs(line_x - qix_cell_x) <= 1 and abs(line_y - qix_cell_y) <= 1:
                return True

        return False

    def _check_sparx_collision(self) -> bool:
        """Check if Sparx collides with the player."""
        for sparx_pos in [self.sparx1_pos, self.sparx2_pos]:
            if (abs(sparx_pos[0] - self.player_pos[0]) <= 1 and
                abs(sparx_pos[1] - self.player_pos[1]) <= 1):
                return True
        return False

    def _reset_player_position(self) -> None:
        """Reset player to a safe position after losing a life."""
        # Find a safe position on the border
        for x in range(1, self.GRID_SIZE // 2):
            if self.grid[0][x] == CellType.CAPTURED:
                self.player_pos = [x, 0]
                return
        self.player_pos = [self.GRID_SIZE // 2, 0]

    def get_state(self) -> Dict:
        """Get current game state as a dictionary."""
        return {
            'grid': [[t.value for t in row] for row in self.grid],
            'player': tuple(self.player_pos),
            'drawing': self.drawing,
            'current_line': self.current_line.copy(),
            'qix': tuple(self.qix_pos),
            'qix_vel': tuple(self.qix_vel),
            'sparx1': tuple(self.sparx1_pos),
            'sparx2': tuple(self.sparx2_pos),
            'score': self.score,
            'lives': self.lives,
            'captured_percentage': self._get_captured_percentage(),
            'level': self.level,
            'game_over': self.game_over,
            'victory': self.victory,
            'steps': self.steps
        }

    def get_grid_state(self) -> List[List[int]]:
        """
        Get game state as a 2D grid.
        Returns:
            2D array with player, qix, and sparx positions included.
        """
        grid_state = [[t.value for t in row] for row in self.grid]

        # Add current line
        for x, y in self.current_line:
            if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
                grid_state[y][x] = CellType.LINE.value

        # Add player
        px, py = self.player_pos
        if 0 <= px < self.GRID_SIZE and 0 <= py < self.GRID_SIZE:
            grid_state[py][px] = CellType.PLAYER.value

        return grid_state

    def draw(self) -> None:
        """Render the game state."""
        if not self.render:
            return

        # Background
        self.screen.fill(self.COLOR_BG)

        # Draw grid cells
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                rect = pygame.Rect(
                    x * self.CELL_SIZE,
                    y * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )

                cell_type = self.grid[y][x]

                if cell_type == CellType.CAPTURED:
                    pygame.draw.rect(self.screen, self.COLOR_CAPTURED, rect)
                else:
                    pygame.draw.rect(self.screen, self.COLOR_EMPTY, rect)

        # Draw current line
        for x, y in self.current_line:
            rect = pygame.Rect(
                x * self.CELL_SIZE,
                y * self.CELL_SIZE,
                self.CELL_SIZE,
                self.CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.COLOR_LINE, rect)

        # Draw player
        player_rect = pygame.Rect(
            self.player_pos[0] * self.CELL_SIZE + 2,
            self.player_pos[1] * self.CELL_SIZE + 2,
            self.CELL_SIZE - 4,
            self.CELL_SIZE - 4
        )
        pygame.draw.rect(self.screen, self.COLOR_PLAYER, player_rect)

        # Draw Qix (as a larger shape)
        qix_center = (
            int(self.qix_pos[0]),
            int(self.qix_pos[1])
        )
        qix_size = self.CELL_SIZE * 2
        pygame.draw.circle(self.screen, self.COLOR_QIX, qix_center, qix_size // 2)

        # Draw Sparx
        for sparx_pos in [self.sparx1_pos, self.sparx2_pos]:
            sparx_rect = pygame.Rect(
                sparx_pos[0] * self.CELL_SIZE + 1,
                sparx_pos[1] * self.CELL_SIZE + 1,
                self.CELL_SIZE - 2,
                self.CELL_SIZE - 2
            )
            pygame.draw.rect(self.screen, self.COLOR_SPARX, sparx_rect)

        # Draw HUD
        hud_y = self.FIELD_SIZE
        pygame.draw.rect(self.screen, self.COLOR_HUD_BG, (0, hud_y, self.WINDOW_WIDTH, 60))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, self.COLOR_TEXT)
        self.screen.blit(score_text, (20, hud_y + 15))

        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, self.COLOR_TEXT)
        self.screen.blit(lives_text, (200, hud_y + 15))

        # Percentage captured
        percentage = self._get_captured_percentage()
        percent_color = self.COLOR_TEXT
        if percentage >= 50:
            percent_color = (100, 255, 100)
        elif percentage >= 25:
            percent_color = (255, 255, 100)

        percent_text = self.font.render(f"Captured: {percentage:.1f}%", True, percent_color)
        self.screen.blit(percent_text, (350, hud_y + 15))

        # Drawing indicator
        if self.drawing:
            draw_text = self.font.render("DRAWING", True, self.COLOR_LINE)
            self.screen.blit(draw_text, (550, hud_y + 15))

        # Game over / Victory overlay
        if self.game_over:
            overlay = pygame.Surface((self.FIELD_SIZE, self.FIELD_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.victory:
                msg = "VICTORY!"
                color = (0, 200, 50)
            else:
                msg = "GAME OVER"
                color = (220, 50, 50)

            text = self.large_font.render(msg, True, color)
            text_rect = text.get_rect(center=(self.FIELD_SIZE // 2, self.FIELD_SIZE // 2 - 20))
            self.screen.blit(text, text_rect)

            restart_text = self.font.render("Press R to restart, ESC to quit", True, self.COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(self.FIELD_SIZE // 2, self.FIELD_SIZE // 2 + 30))
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
                elif event.key == pygame.K_SPACE:
                    return Action.DRAW_HOLD
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.drawing:
                    return Action.DRAW_RELEASE

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
    game = QixGame(render=True)
    game.run()


if __name__ == "__main__":
    main()
