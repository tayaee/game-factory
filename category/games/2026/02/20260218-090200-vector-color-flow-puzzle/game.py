"""Main game logic for Color Flow Puzzle."""

import pygame
import sys
import time
from typing import Optional, Tuple, List

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_SIZE, MARGIN,
    BACKGROUND_COLOR, GRID_COLOR, TEXT_COLOR, COLORS,
    FPS, POINTS_PER_CONNECTION, TIME_BONUS_MULTIPLIER, LEVEL_TIME_LIMIT
)
from level import Level


class Game:
    """Main game class for Color Flow Puzzle."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Color Flow Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Game state
        self.level_num = 1
        self.grid_size = GRID_SIZE
        self.num_colors = 3
        self.score = 0
        self.high_score = 0
        self.level_time = LEVEL_TIME_LIMIT
        self.start_time = time.time()
        self.game_state = "playing"  # playing, level_complete, game_over, win

        # Initialize level
        self.level = Level(self.grid_size, self.num_colors)

        # Interaction state
        self.selected_color = 0
        self.current_pipe = []
        self.is_drawing = False

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard input."""
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.key == pygame.K_r:
            self.level.reset()
            self.current_pipe = []
            self.is_drawing = False

    def handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Handle mouse button press."""
        if self.game_state != "playing":
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        r, c = grid_pos
        color_id = self.level.grid[r][c]

        if color_id > 0:
            # Start drawing from this dot
            self.selected_color = color_id
            self.current_pipe = [(r, c)]
            self.is_drawing = True
            # Clear existing pipe for this color
            self._clear_color_pipe(color_id)

    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Handle mouse movement while drawing."""
        if not self.is_drawing or self.game_state != "playing":
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        r, c = grid_pos

        # Check if this is a valid move
        if self._is_valid_move(r, c):
            self.current_pipe.append((r, c))
            # Update grid
            self.level.grid[r][c] = self.selected_color

            # Check if we reached the matching dot
            if (r, c) in self._get_matching_dot_pos():
                self._complete_pipe()
                self.is_drawing = False
                self.current_pipe = []

    def handle_mouse_up(self, event: pygame.event.Event) -> None:
        """Handle mouse button release."""
        if self.is_drawing:
            # Check if pipe was completed
            if not self._is_pipe_complete():
                # Incomplete pipe - clear it
                self._clear_color_pipe(self.selected_color)
            self.is_drawing = False
            self.current_pipe = []

    def _is_valid_move(self, r: int, c: int) -> bool:
        """Check if a move to the given cell is valid."""
        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
            return False

        # Can't move to same cell
        if self.current_pipe and (r, c) == self.current_pipe[-1]:
            return False

        # Check if adjacent (including same cell for dots)
        if self.current_pipe:
            last_r, last_c = self.current_pipe[-1]
            if abs(r - last_r) + abs(c - last_c) != 1:
                return False

        # Check if cell is empty or is the matching dot
        cell_color = self.level.grid[r][c]
        if cell_color == 0:
            return True
        elif cell_color == self.selected_color:
            # Can only traverse own cells or reach the matching dot
            if (r, c) in self._get_matching_dot_pos():
                return True
            if (r, c) not in self.current_pipe:
                # Can cross back over own pipe (backtracking)
                return True
        return False

    def _get_matching_dot_pos(self) -> List[Tuple[int, int]]:
        """Get the position of the matching dot for the selected color."""
        positions = self.level.dot_positions[self.selected_color - 1]
        return [(positions[0], positions[1]), (positions[2], positions[3])]

    def _is_pipe_complete(self) -> bool:
        """Check if the current pipe connects both dots."""
        matching_dots = self._get_matching_dot_pos()
        return all(dot in self.current_pipe for dot in matching_dots)

    def _complete_pipe(self) -> None:
        """Mark a pipe as completed and add score."""
        self.level.completed_pipes.add(self.selected_color)
        self.score += POINTS_PER_CONNECTION

    def _clear_color_pipe(self, color_id: int) -> None:
        """Clear the pipe for a given color from the grid."""
        matching_dots = set(self._get_matching_dot_pos())

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.level.grid[r][c] == color_id and (r, c) not in matching_dots:
                    self.level.grid[r][c] = 0

    def screen_to_grid(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to grid coordinates."""
        x, y = pos
        grid_x = x - MARGIN
        grid_y = y - MARGIN

        col = grid_x // CELL_SIZE
        row = grid_y // CELL_SIZE

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return row, col
        return None

    def grid_to_screen(self, row: int, col: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates."""
        return MARGIN + col * CELL_SIZE + CELL_SIZE // 2, MARGIN + row * CELL_SIZE + CELL_SIZE // 2

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.game_state != "playing":
            return

        # Update level time
        elapsed = time.time() - self.start_time
        self.level_time = max(0, LEVEL_TIME_LIMIT - elapsed)

        if self.level_time <= 0:
            self.game_state = "game_over"
            return

        # Check if level is complete
        if self.level.is_complete():
            # Add time bonus
            time_bonus = int(self.level_time * TIME_BONUS_MULTIPLIER)
            self.score += time_bonus
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_state = "level_complete"

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(BACKGROUND_COLOR)

        # Draw header
        self.draw_header()

        # Draw grid background
        self.draw_grid()

        # Draw pipes
        self.draw_pipes()

        # Draw dots
        self.draw_dots()

        # Draw current pipe being drawn
        if self.is_drawing and len(self.current_pipe) > 1:
            self.draw_current_pipe()

        # Draw overlay for game states
        if self.game_state != "playing":
            self.draw_overlay()

    def draw_header(self) -> None:
        """Draw the header with score and level info."""
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level: {self.level_num}", True, TEXT_COLOR)
        time_text = self.font.render(f"Time: {int(self.level_time)}", True, TEXT_COLOR)

        self.screen.blit(score_text, (20, 20))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 20))
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 20))

        # Instructions
        if self.level_num == 1:
            inst_text = self.font.render("Click and drag to connect colors", True, (150, 150, 150))
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 60))

    def draw_grid(self) -> None:
        """Draw the grid background."""
        grid_width = self.grid_size * CELL_SIZE
        grid_height = self.grid_size * CELL_SIZE

        # Draw grid lines
        for i in range(self.grid_size + 1):
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (x, MARGIN), (x, MARGIN + grid_height), 2)

            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (MARGIN, y), (MARGIN + grid_width, y), 2)

    def draw_pipes(self) -> None:
        """Draw all completed and in-progress pipes."""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color_id = self.level.grid[r][c]
                if color_id > 0:
                    # Check if this is a dot
                    is_dot = any(
                        (r, c) == (pos[0], pos[1]) or (r, c) == (pos[2], pos[3])
                        for pos in self.level.dot_positions
                    )

                    if not is_dot:
                        self.draw_cell_pipe(r, c, COLORS[color_id - 1])

    def draw_cell_pipe(self, r: int, c: int, color: Tuple[int, int, int]) -> None:
        """Draw a pipe segment in a cell, connecting to adjacent same-colored cells."""
        x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2
        y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2
        half_cell = CELL_SIZE // 2 - 5

        # Determine which directions have connections
        connections = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                if self.level.grid[nr][nc] == self.level.grid[r][c]:
                    connections.append((dr, dc))

        # Draw pipe based on connections
        if not connections:
            pygame.draw.circle(self.screen, color, (x, y), 10)
        else:
            # Draw thick lines for each connection
            for dr, dc in connections:
                end_x = x + dc * half_cell
                end_y = y + dr * half_cell
                pygame.draw.line(self.screen, color, (x, y), (end_x, end_y), 12)

            # Draw center circle to connect pipe segments
            pygame.draw.circle(self.screen, color, (x, y), 8)

    def draw_dots(self) -> None:
        """Draw the colored dots."""
        dot_radius = 15
        for positions in self.level.dot_positions:
            color_id = self.level.dot_positions.index(positions) + 1
            color = COLORS[color_id - 1]

            for r, c in [(positions[0], positions[1]), (positions[2], positions[3])]:
                x, y = self.grid_to_screen(r, c)
                pygame.draw.circle(self.screen, color, (x, y), dot_radius)
                # Add white outline
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), dot_radius, 2)

    def draw_current_pipe(self) -> None:
        """Draw the pipe currently being drawn."""
        if len(self.current_pipe) < 2:
            return

        color = COLORS[self.selected_color - 1]
        points = [self.grid_to_screen(r, c) for r, c in self.current_pipe]

        pygame.draw.lines(self.screen, color, False, points, 10)

    def draw_overlay(self) -> None:
        """Draw overlay for game over or level complete states."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.game_state == "game_over":
            text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            sub_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.font.render("Press R to restart", True, (150, 150, 150))
        elif self.game_state == "level_complete":
            text = self.large_font.render("LEVEL COMPLETE!", True, (100, 255, 100))
            bonus_text = self.font.render(f"Time Bonus: {int(self.level_time * TIME_BONUS_MULTIPLIER)}", True, TEXT_COLOR)
            sub_text = self.font.render("Press SPACE for next level", True, TEXT_COLOR)
            restart_text = None

        text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - 50
        self.screen.blit(text, (text_x, text_y))

        if self.game_state == "game_over":
            sub_x = SCREEN_WIDTH // 2 - sub_text.get_width() // 2
            self.screen.blit(sub_text, (sub_x, text_y + 60))
            restart_x = SCREEN_WIDTH // 2 - restart_text.get_width() // 2
            self.screen.blit(restart_text, (restart_x, text_y + 100))
        else:
            bonus_x = SCREEN_WIDTH // 2 - bonus_text.get_width() // 2
            self.screen.blit(bonus_text, (bonus_x, text_y + 50))
            sub_x = SCREEN_WIDTH // 2 - sub_text.get_width() // 2
            self.screen.blit(sub_text, (sub_x, text_y + 90))

        # Handle level transition
        if self.game_state == "level_complete":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.next_level()

    def next_level(self) -> None:
        """Advance to the next level."""
        self.level_num += 1
        self.num_colors = min(self.num_colors + 1, 6)
        self.score = 0
        self.level_time = LEVEL_TIME_LIMIT
        self.start_time = time.time()
        self.level = Level(self.grid_size, self.num_colors)
        self.game_state = "playing"

    # AI/RL Interface
    def get_observation(self) -> dict:
        """Get current game state for AI agents."""
        grid_state = [[self.level.grid[r][c] for c in range(self.grid_size)]
                       for r in range(self.grid_size)]

        return {
            "grid": grid_state,
            "grid_size": self.grid_size,
            "num_colors": self.num_colors,
            "level_time": self.level_time,
            "score": self.score,
            "game_state": self.game_state,
            "dot_positions": self.level.dot_positions
        }

    def get_valid_actions(self) -> List[int]:
        """Get list of valid actions for the current state."""
        actions = []
        for color_id in range(1, self.num_colors + 1):
            actions.extend([color_id * 4 + i for i in range(4)])  # Up, Down, Left, Right for each color
        return actions
