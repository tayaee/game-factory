"""
Neon Snake Retro - A classic snake game with neon visual style.

Game runs on a 20x20 grid. The snake moves one cell per second in the selected direction.
Food appears at random locations. Eating food grows the snake and increases score.
Game ends when snake hits wall or itself.

Controls: Arrow keys to change direction (cannot reverse immediately).
"""

import pygame
import random
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# Color palette - Neon retro style
class Color(Enum):
    BLACK = (0, 0, 0)
    DARK_GRAY = (15, 15, 20)
    NEON_GREEN = (57, 255, 20)
    NEON_RED = (255, 0, 80)
    NEON_BLUE = (0, 255, 255)
    NEON_PURPLE = (180, 0, 255)
    NEON_YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)


@dataclass
class Position:
    """Represents a grid position."""
    x: int
    y: int

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


class Direction(Enum):
    """Direction of snake movement."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self) -> 'Direction':
        """Returns the opposite direction."""
        if self == Direction.UP:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.UP
        if self == Direction.LEFT:
            return Direction.RIGHT
        return Direction.LEFT


class SnakeGame:
    """
    Main game class for Neon Snake Retro.

    Manages game state, snake movement, collision detection, and rendering.
    """

    # Game constants
    GRID_SIZE = 20
    CELL_SIZE = 25
    WINDOW_SIZE = GRID_SIZE * CELL_SIZE
    MOVE_INTERVAL = 150  # milliseconds between moves

    def __init__(self) -> None:
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
        pygame.display.set_caption("Neon Snake Retro")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Game state
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        # Snake starts in the middle with 3 segments
        center = self.GRID_SIZE // 2
        self.snake: List[Position] = [
            Position(center, center),
            Position(center - 1, center),
            Position(center - 2, center)
        ]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.last_move_time = pygame.time.get_ticks()
        self.spawn_food()

    def spawn_food(self) -> None:
        """Spawn food at a random position not occupied by the snake."""
        while True:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            food_pos = Position(x, y)
            if food_pos not in self.snake:
                self.food = food_pos
                break

    def get_head(self) -> Position:
        """Get the head position of the snake."""
        return self.snake[0]

    def move_snake(self) -> None:
        """Move the snake one step in the current direction."""
        if self.game_over:
            return

        # Update direction (prevent 180-degree turns)
        if self.next_direction != self.direction.opposite():
            self.direction = self.next_direction

        # Calculate new head position
        head = self.get_head()
        dx, dy = self.direction.value
        new_head = Position(head.x + dx, head.y + dy)

        # Check wall collision
        if (new_head.x < 0 or new_head.x >= self.GRID_SIZE or
            new_head.y < 0 or new_head.y >= self.GRID_SIZE):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check if food was eaten
        if new_head == self.food:
            self.score += 10
            self.spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def handle_input(self) -> None:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not self.game_started:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.game_started = True
                    return

                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                        self.game_started = True
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    return

                # Direction controls
                if event.key == pygame.K_UP:
                    self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT:
                    self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.next_direction = Direction.RIGHT
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def draw_cell(self, pos: Position, color: tuple, glow: bool = False) -> None:
        """Draw a single cell with optional neon glow effect."""
        x = pos.x * self.CELL_SIZE
        y = pos.y * self.CELL_SIZE

        # Glow effect
        if glow:
            glow_rect = pygame.Rect(x - 2, y - 2, self.CELL_SIZE + 4, self.CELL_SIZE + 4)
            pygame.draw.rect(self.screen, (color[0] // 3, color[1] // 3, color[2] // 3), glow_rect, border_radius=4)

        # Main cell
        rect = pygame.Rect(x + 1, y + 1, self.CELL_SIZE - 2, self.CELL_SIZE - 2)
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

        # Highlight
        highlight_rect = pygame.Rect(x + 4, y + 4, self.CELL_SIZE // 3, self.CELL_SIZE // 3)
        highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=2)

    def draw(self) -> None:
        """Draw the game state."""
        # Background
        self.screen.fill(Color.BLACK.value)

        # Draw grid (subtle)
        for i in range(0, self.WINDOW_SIZE, self.CELL_SIZE):
            pygame.draw.line(self.screen, Color.DARK_GRAY.value, (i, 0), (i, self.WINDOW_SIZE))
            pygame.draw.line(self.screen, Color.DARK_GRAY.value, (0, i), (self.WINDOW_SIZE, i))

        # Draw snake
        for i, segment in enumerate(self.snake):
            if i == 0:
                # Head with glow
                self.draw_cell(segment, Color.NEON_GREEN.value, glow=True)
            else:
                # Body segments with gradient effect
                brightness = max(0.4, 1 - (i / len(self.snake)) * 0.6)
                color = (
                    int(Color.NEON_GREEN.value[0] * brightness),
                    int(Color.NEON_GREEN.value[1] * brightness),
                    int(Color.NEON_GREEN.value[2] * brightness)
                )
                self.draw_cell(segment, color)

        # Draw food with pulsing glow
        pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250
        glow_size = int(4 + pulse * 4)
        food_x = self.food.x * self.CELL_SIZE + self.CELL_SIZE // 2
        food_y = self.food.y * self.CELL_SIZE + self.CELL_SIZE // 2
        pygame.draw.circle(self.screen, (100, 0, 40), (food_x, food_y), self.CELL_SIZE // 2 + glow_size)
        pygame.draw.circle(self.screen, Color.NEON_RED.value, (food_x, food_y), self.CELL_SIZE // 2 - 2)

        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, Color.NEON_BLUE.value)
        self.screen.blit(score_text, (10, 10))

        # Draw length info
        length_text = self.font.render(f"LENGTH: {len(self.snake)}", True, Color.NEON_PURPLE.value)
        self.screen.blit(length_text, (10, 45))

        # Start screen
        if not self.game_started:
            self.draw_overlay("NEON SNAKE", "Press SPACE to Start", Color.NEON_GREEN.value)

        # Game over screen
        if self.game_over:
            self.draw_overlay("GAME OVER", f"Final Score: {self.score}", Color.NEON_RED.value, "Press SPACE to Restart, Q to Quit")

        pygame.display.flip()

    def draw_overlay(self, title: str, subtitle: str, color: tuple, extra: str = None) -> None:
        """Draw an overlay screen (start/game over)."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE))
        overlay.set_alpha(200)
        overlay.fill(Color.BLACK.value)
        self.screen.blit(overlay, (0, 0))

        # Title with glow
        title_text = self.large_font.render(title, True, color)
        title_rect = title_text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2 - 40))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        sub_text = self.font.render(subtitle, True, Color.WHITE.value)
        sub_rect = sub_text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2 + 20))
        self.screen.blit(sub_text, sub_rect)

        # Extra text
        if extra:
            extra_text = self.font.render(extra, True, Color.NEON_YELLOW.value)
            extra_rect = extra_text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2 + 60))
            self.screen.blit(extra_text, extra_rect)

    def run(self) -> None:
        """Main game loop."""
        while True:
            current_time = pygame.time.get_ticks()

            self.handle_input()

            if self.game_started and not self.game_over:
                if current_time - self.last_move_time >= self.MOVE_INTERVAL:
                    self.move_snake()
                    self.last_move_time = current_time

            self.draw()
            self.clock.tick(60)


def main() -> None:
    """Entry point for the game."""
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
