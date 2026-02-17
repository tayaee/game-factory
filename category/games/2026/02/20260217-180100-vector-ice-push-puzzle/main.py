"""
Vector Ice Push Puzzle
A sliding puzzle game where you navigate a frozen maze.
Slide ice blocks strategically to reach the goal and solve the puzzle.
"""

import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 10
CELL_SIZE = min(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE) - 4
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2
FPS = 60

# Colors
COLOR_BG = (20, 25, 35)
COLOR_GRID = (40, 45, 55)
COLOR_WALL = (80, 90, 100)
COLOR_ICE_BLOCK = (100, 180, 220)
COLOR_PLAYER = (50, 200, 150)
COLOR_GOAL = (255, 200, 50)
COLOR_FLOOR = (30, 35, 45)
COLOR_TEXT = (220, 230, 240)
COLOR_UI_BG = (25, 30, 40)
COLOR_ACCENT = (0, 200, 255)

# Cell types
CELL_EMPTY = 0
CELL_WALL = 1
CELL_ICE_BLOCK = 2
CELL_GOAL = 3

class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameLevel:
    """Level definitions for the puzzle game."""

    LEVELS = [
        {
            "name": "Level 1 - First Steps",
            "description": "Slide to the exit",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 2, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 3, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1)
        },
        {
            "name": "Level 2 - Block Navigation",
            "description": "Use the ice block to create a stopping point",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1)
        },
        {
            "name": "Level 3 - Double Block Challenge",
            "description": "Strategically push both blocks",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 2, 0, 2, 0, 0, 1],
                [1, 0, 1, 1, 0, 1, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1)
        },
        {
            "name": "Level 4 - Maze Slide",
            "description": "Navigate through the frozen corridors",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                [1, 0, 1, 0, 0, 2, 0, 1, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
                [1, 0, 0, 2, 0, 1, 0, 0, 3, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1)
        },
        {
            "name": "Level 5 - Frozen Labyrinth",
            "description": "Master the art of ice sliding",
            "grid": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 0, 1, 1, 0, 1, 1],
                [1, 0, 1, 2, 0, 2, 1, 0, 0, 1],
                [1, 0, 1, 0, 0, 0, 1, 0, 1, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 2, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 0, 3, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
            "player_start": (1, 1)
        },
    ]

    @classmethod
    def get_level(cls, index):
        if 0 <= index < len(cls.LEVELS):
            return cls.LEVELS[index]
        return None


class GameState:
    PLAYING = 0
    LEVEL_COMPLETE = 1
    GAME_COMPLETE = 2
    START = 3


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Ice Push Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.current_level = 0
        self.state = GameState.START
        self.reset_level()
        self.total_score = 0

    def reset_level(self):
        level_data = GameLevel.get_level(self.current_level)
        if level_data:
            self.level_name = level_data["name"]
            self.level_description = level_data["description"]
            self.grid = [row[:] for row in level_data["grid"]]
            self.player_pos = list(level_data["player_start"])
            self.moves = 0
            self.score = 0
            self.goal_pos = None

            # Find goal position
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if self.grid[y][x] == CELL_GOAL:
                        self.goal_pos = (x, y)

    def is_valid_cell(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

    def get_cell(self, x, y):
        if self.is_valid_cell(x, y):
            return self.grid[y][x]
        return CELL_WALL

    def slide_position(self, x, y, direction):
        """Calculate where a position will slide to given a direction."""
        dx, dy = direction
        while self.is_valid_cell(x + dx, y + dy):
            cell = self.get_cell(x + dx, y + dy)
            if cell == CELL_WALL or cell == CELL_ICE_BLOCK:
                break
            x += dx
            y += dy
        return (x, y)

    def can_push_block(self, block_x, block_y, direction):
        """Check if an ice block can be pushed in the given direction."""
        dx, dy = direction
        next_x, next_y = block_x + dx, block_y + dy

        if not self.is_valid_cell(next_x, next_y):
            return False

        next_cell = self.get_cell(next_x, next_y)
        return next_cell == CELL_EMPTY or next_cell == CELL_GOAL

    def move(self, direction):
        if self.state != GameState.PLAYING:
            return

        dx, dy = direction
        start_x, start_y = self.player_pos

        # Check if there's an ice block in the direction of movement
        next_x, next_y = start_x + dx, start_y + dy
        next_cell = self.get_cell(next_x, next_y)

        # Push ice block if present
        if next_cell == CELL_ICE_BLOCK:
            if self.can_push_block(next_x, next_y, direction):
                # Find where the block will slide to
                block_final_x, block_final_y = self.slide_position(
                    next_x + dx, next_y + dy, direction
                )

                # Update block position
                self.grid[next_y][next_x] = CELL_EMPTY
                self.grid[block_final_y][block_final_x] = CELL_ICE_BLOCK
            else:
                # Cannot push block, no movement
                return

        # Slide the player
        final_x, final_y = self.slide_position(start_x, start_y, direction)
        self.player_pos = [final_x, final_y]
        self.moves += 1
        self.score = max(0, 1000 - self.moves * 10)

        # Check win condition
        if self.player_pos == list(self.goal_pos):
            self.total_score += self.score
            self.state = GameState.LEVEL_COMPLETE

    def draw_grid(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = GRID_OFFSET_X + x * CELL_SIZE
                cell_y = GRID_OFFSET_Y + y * CELL_SIZE

                # Draw cell background
                cell = self.grid[y][x]

                if cell == CELL_WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Wall 3D effect
                    pygame.draw.rect(self.screen, (60, 70, 80),
                                   (cell_x, cell_y, CELL_SIZE - 4, CELL_SIZE - 4))
                elif cell == CELL_ICE_BLOCK:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Ice block
                    block_margin = 4
                    pygame.draw.rect(self.screen, COLOR_ICE_BLOCK,
                                   (cell_x + block_margin, cell_y + block_margin,
                                    CELL_SIZE - block_margin * 2, CELL_SIZE - block_margin * 2))
                    # Ice shine effect
                    pygame.draw.line(self.screen, (150, 220, 250),
                                   (cell_x + block_margin, cell_y + block_margin),
                                   (cell_x + CELL_SIZE - block_margin, cell_y + CELL_SIZE - block_margin), 2)
                    pygame.draw.line(self.screen, (180, 230, 255),
                                   (cell_x + block_margin, cell_y + CELL_SIZE - block_margin),
                                   (cell_x + block_margin + 10, cell_y + block_margin), 2)
                elif cell == CELL_GOAL:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Goal
                    center_x = cell_x + CELL_SIZE // 2
                    center_y = cell_y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, COLOR_GOAL,
                                     (center_x, center_y), CELL_SIZE // 3)
                    pygame.draw.circle(self.screen, (255, 230, 100),
                                     (center_x, center_y), CELL_SIZE // 4)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))

                # Draw cell border
                pygame.draw.rect(self.screen, COLOR_GRID,
                               (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_player(self):
        player_x = GRID_OFFSET_X + self.player_pos[0] * CELL_SIZE + CELL_SIZE // 2
        player_y = GRID_OFFSET_Y + self.player_pos[1] * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3

        # Player glow
        glow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*COLOR_PLAYER, 50),
                         (CELL_SIZE // 2, CELL_SIZE // 2), radius + 5)
        self.screen.blit(glow_surface,
                        (GRID_OFFSET_X + self.player_pos[0] * CELL_SIZE,
                         GRID_OFFSET_Y + self.player_pos[1] * CELL_SIZE))

        # Player body
        pygame.draw.circle(self.screen, COLOR_PLAYER, (player_x, player_y), radius)

        # Player inner detail
        pygame.draw.circle(self.screen, (80, 220, 180), (player_x, player_y), radius - 3)

        # Direction indicator (diamond)
        diamond_size = radius // 2
        diamond_points = [
            (player_x, player_y - diamond_size),
            (player_x + diamond_size, player_y),
            (player_x, player_y + diamond_size),
            (player_x - diamond_size, player_y)
        ]
        pygame.draw.polygon(self.screen, (255, 255, 255), diamond_points)

    def draw_ui(self):
        # Top bar background
        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, COLOR_ACCENT, (0, 60), (SCREEN_WIDTH, 60), 2)

        # Level name
        level_text = self.font.render(self.level_name, True, COLOR_TEXT)
        self.screen.blit(level_text, (20, 15))

        # Level description
        desc_text = self.small_font.render(self.level_description, True, (150, 160, 170))
        self.screen.blit(desc_text, (20, 40))

        # Moves
        moves_text = self.font.render(f"Moves: {self.moves}", True, COLOR_TEXT)
        moves_rect = moves_text.get_rect(right=SCREEN_WIDTH - 20, top=10)
        self.screen.blit(moves_text, moves_rect)

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_GOAL)
        score_rect = score_text.get_rect(right=SCREEN_WIDTH - 20, top=35)
        self.screen.blit(score_text, score_rect)

        # Level indicator
        level_num_text = self.small_font.render(
            f"Level {self.current_level + 1}/{len(GameLevel.LEVELS)}",
            True, COLOR_ACCENT
        )
        level_num_rect = level_num_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(level_num_text, level_num_rect)

        # Controls hint
        hint_text = self.tiny_font.render("Arrow Keys: Move | R: Restart | ESC: Quit",
                                         True, (100, 110, 120))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        self.screen.blit(hint_text, hint_rect)

    def draw_start_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("VECTOR ICE PUSH PUZZLE", True, COLOR_ACCENT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Slide strategically to reach the goal", True, COLOR_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(subtitle, subtitle_rect)

        hint = self.small_font.render("Press any arrow key to start", True, COLOR_PLAYER)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(hint, hint_rect)

        # Draw decorative ice blocks
        for i in range(5):
            x = SCREEN_WIDTH // 2 - 100 + i * 50
            y = SCREEN_HEIGHT // 2 + 80
            pygame.draw.rect(self.screen, COLOR_ICE_BLOCK, (x, y, 30, 30), 2)
            pygame.draw.line(self.screen, COLOR_ICE_BLOCK, (x + 5, y + 5), (x + 25, y + 25), 2)

    def draw_level_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("LEVEL COMPLETE!", True, COLOR_GOAL)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        score_text = self.small_font.render(f"Level Score: {self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        if self.current_level < len(GameLevel.LEVELS) - 1:
            hint = self.small_font.render("Press any arrow key for next level", True, COLOR_PLAYER)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint, hint_rect)
        else:
            hint = self.small_font.render("Press any arrow key to finish", True, COLOR_PLAYER)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint, hint_rect)

    def draw_game_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("GAME COMPLETE!", True, COLOR_GOAL)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(title, title_rect)

        total_score_text = self.font.render(f"Total Score: {self.total_score}", True, COLOR_TEXT)
        total_score_rect = total_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(total_score_text, total_score_rect)

        moves_text = self.small_font.render(f"Total Moves: {self.moves}", True, (150, 160, 170))
        moves_rect = moves_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(moves_text, moves_rect)

        hint = self.small_font.render("Press R to play again or ESC to quit", True, COLOR_ACCENT)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(hint, hint_rect)

    def draw(self):
        self.screen.fill(COLOR_BG)

        self.draw_grid()
        self.draw_player()
        self.draw_ui()

        if self.state == GameState.START:
            self.draw_start_screen()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.GAME_COMPLETE:
            self.draw_game_complete()

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                self.current_level = 0
                self.total_score = 0
                self.state = GameState.START
                self.reset_level()

            direction = None
            if event.key == pygame.K_UP:
                direction = Direction.UP
            elif event.key == pygame.K_DOWN:
                direction = Direction.DOWN
            elif event.key == pygame.K_LEFT:
                direction = Direction.LEFT
            elif event.key == pygame.K_RIGHT:
                direction = Direction.RIGHT

            if direction:
                if self.state == GameState.START:
                    self.state = GameState.PLAYING
                elif self.state == GameState.LEVEL_COMPLETE:
                    if self.current_level < len(GameLevel.LEVELS) - 1:
                        self.current_level += 1
                        self.state = GameState.PLAYING
                        self.reset_level()
                    else:
                        self.state = GameState.GAME_COMPLETE
                elif self.state == GameState.GAME_COMPLETE:
                    self.current_level = 0
                    self.total_score = 0
                    self.state = GameState.START
                    self.reset_level()
                elif self.state == GameState.PLAYING:
                    self.move(direction)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
