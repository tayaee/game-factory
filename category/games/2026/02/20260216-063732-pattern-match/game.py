import pygame
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
GRID_SIZE = 4
CELL_SIZE = 80
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 150

# Colors
COLOR_BG = (20, 20, 30)
COLOR_GRID = (50, 50, 70)
COLOR_CELL_EMPTY = (40, 40, 60)
COLOR_TEXT = (220, 220, 220)
COLOR_HIGHLIGHT = (255, 255, 100)

# Symbol colors
SYMBOL_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
]

# Symbol shapes
SHAPE_CIRCLE = 0
SHAPE_SQUARE = 1
SHAPE_TRIANGLE = 2
SHAPE_DIAMOND = 3


@dataclass
class Cell:
    color_idx: int
    shape: int
    revealed: bool = False


class PatternMatchGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pattern Match")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

        self.grid: List[List[Optional[Cell]]] = []
        self.target_pattern: List[Tuple[int, int]] = []
        self.selected_cells: List[Tuple[int, int]] = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_state = "menu"  # menu, showing_pattern, playing, game_over
        self.pattern_timer = 0
        self.show_duration = 180  # Frames to show pattern
        self.message = ""
        self.message_timer = 0

        self.target_cells_for_pattern = set()

    def generate_pattern(self) -> List[Tuple[int, int]]:
        """Generate a random pattern based on current level."""
        pattern_size = min(2 + self.level, 8)
        available = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        return random.sample(available, pattern_size)

    def generate_grid(self):
        """Generate the grid with colored symbols."""
        self.grid = []
        for r in range(GRID_SIZE):
            row = []
            for c in range(GRID_SIZE):
                color_idx = random.randint(0, len(SYMBOL_COLORS) - 1)
                shape = random.choice([SHAPE_CIRCLE, SHAPE_SQUARE, SHAPE_TRIANGLE, SHAPE_DIAMOND])
                row.append(Cell(color_idx, shape, False))
            self.grid.append(row)

    def start_level(self):
        """Initialize a new level."""
        self.generate_grid()
        self.target_pattern = self.generate_pattern()
        self.target_cells_for_pattern = set(self.target_pattern)
        self.selected_cells = []
        self.pattern_timer = self.show_duration
        self.game_state = "showing_pattern"

    def get_cell_rect(self, row: int, col: int) -> pygame.Rect:
        """Get the rectangle for a grid cell."""
        x = GRID_OFFSET_X + col * CELL_SIZE
        y = GRID_OFFSET_Y + row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE - 4, CELL_SIZE - 4)

    def draw_symbol(self, surface, shape, color_idx, center_x, center_y, size=25):
        """Draw a symbol at the given position."""
        color = SYMBOL_COLORS[color_idx]
        if shape == SHAPE_CIRCLE:
            pygame.draw.circle(surface, color, (center_x, center_y), size)
        elif shape == SHAPE_SQUARE:
            rect = pygame.Rect(center_x - size, center_y - size, size * 2, size * 2)
            pygame.draw.rect(surface, color, rect)
        elif shape == SHAPE_TRIANGLE:
            points = [
                (center_x, center_y - size),
                (center_x - size, center_y + size),
                (center_x + size, center_y + size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif shape == SHAPE_DIAMOND:
            points = [
                (center_x, center_y - size),
                (center_x + size, center_y),
                (center_x, center_y + size),
                (center_x - size, center_y)
            ]
            pygame.draw.polygon(surface, color, points)

    def draw_grid(self):
        """Draw the game grid."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = self.get_cell_rect(r, c)
                cell = self.grid[r][c]

                # Draw cell background
                bg_color = COLOR_CELL_EMPTY
                if (r, c) in self.selected_cells:
                    bg_color = (70, 70, 100)
                elif (r, c) in self.target_cells_for_pattern and self.game_state == "showing_pattern":
                    bg_color = (80, 60, 60)

                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 2, border_radius=8)

                # Draw symbol
                self.draw_symbol(self.screen, cell.shape, cell.color_idx,
                               rect.centerx, rect.centery)

    def draw_ui(self):
        """Draw the user interface."""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Level
        level_text = self.font_medium.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 20))

        # Lives
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (SCREEN_WIDTH // 2 - 50, 20))

        # Message
        if self.message_timer > 0:
            msg_color = COLOR_HIGHLIGHT if "Correct" in self.message else (255, 100, 100)
            msg_text = self.font_medium.render(self.message, True, msg_color)
            rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(msg_text, rect)

    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill(COLOR_BG)

        title = self.font_large.render("PATTERN MATCH", True, COLOR_HIGHLIGHT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        instructions = [
            "Memorize the highlighted pattern,",
            "then recreate it by clicking cells.",
            "",
            "Press SPACE or CLICK to start"
        ]

        y = 300
        for line in instructions:
            text = self.font_small.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 35

        high_score = self.font_small.render(f"High Score: {self.score}", True, (150, 150, 150))
        high_score_rect = high_score.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(high_score, high_score_rect)

    def draw_game_over(self):
        """Draw the game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)

        final_score = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(final_score, score_rect)

        level_reached = self.font_medium.render(f"Level Reached: {self.level}", True, COLOR_TEXT)
        level_rect = level_reached.get_rect(center=(SCREEN_WIDTH // 2, 370))
        self.screen.blit(level_reached, level_rect)

        restart_text = self.font_small.render("Press SPACE or CLICK to restart", True, COLOR_HIGHLIGHT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(restart_text, restart_rect)

    def handle_click(self, pos):
        """Handle mouse click."""
        if self.game_state != "playing":
            return

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = self.get_cell_rect(r, c)
                if rect.collidepoint(pos):
                    if (r, c) in self.selected_cells:
                        self.selected_cells.remove((r, c))
                    else:
                        self.selected_cells.append((r, c))
                    self.check_pattern()
                    break

    def check_pattern(self):
        """Check if the selected pattern matches the target."""
        selected_set = set(self.selected_cells)

        if len(selected_set) == len(self.target_pattern):
            if selected_set == self.target_cells_for_pattern:
                # Correct!
                self.score += self.level * 100
                self.level += 1
                self.message = "Correct! +{} points".format(self.level * 100)
                self.message_timer = 60
                self.start_level()
            else:
                # Wrong!
                self.lives -= 1
                self.message = "Wrong pattern!"
                self.message_timer = 60
                self.selected_cells = []

                if self.lives <= 0:
                    self.game_state = "game_over"

    def update(self):
        """Update game state."""
        if self.message_timer > 0:
            self.message_timer -= 1

        if self.game_state == "showing_pattern":
            self.pattern_timer -= 1
            if self.pattern_timer <= 0:
                self.game_state = "playing"

    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.game_state == "menu":
                            self.score = 0
                            self.level = 1
                            self.lives = 3
                            self.start_level()
                        elif self.game_state == "game_over":
                            self.game_state = "menu"
                        elif self.game_state == "playing":
                            self.handle_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == "menu":
                            self.score = 0
                            self.level = 1
                            self.lives = 3
                            self.start_level()
                        elif self.game_state == "game_over":
                            self.game_state = "menu"

            self.update()

            # Draw
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "showing_pattern" or self.game_state == "playing":
                self.screen.fill(COLOR_BG)
                self.draw_grid()
                self.draw_ui()

                if self.game_state == "showing_pattern":
                    timer_text = self.font_medium.render(
                        f"Memorize! {self.pattern_timer // 60 + 1}",
                        True, COLOR_HIGHLIGHT
                    )
                    timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
                    self.screen.blit(timer_text, timer_rect)
            elif self.game_state == "game_over":
                self.screen.fill(COLOR_BG)
                self.draw_grid()
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    game = PatternMatchGame()
    game.run()


if __name__ == "__main__":
    main()
