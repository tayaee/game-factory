"""
Vector Fire Extinguish Logic
Tactical water-pressure puzzle to extinguish spreading flames in a grid warehouse.
"""

import pygame
import sys
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 10
CELL_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 100
FPS = 60

# Game timing
FIRE_SPREAD_INTERVAL = 5000  # milliseconds (5 seconds)
EXTINGUISH_TIME = 500  # milliseconds per cell

# Water capacity
MAX_WATER = 5
REFILL_AMOUNT = 5

# Scoring
POINTS_PER_EXTINGUISHED = 100
POINTS_PER_BOX_LOST = -10

# Colors
COLOR_BG = (20, 25, 30)
COLOR_GRID = (40, 45, 55)
COLOR_WALL = (70, 75, 85)
COLOR_BOX = (139, 90, 43)
COLOR_FIRE = (255, 100, 50)
COLOR_BOT = (50, 180, 200)
COLOR_REFILL = (0, 150, 255)
COLOR_FLOOR = (30, 35, 45)
COLOR_TEXT = (220, 230, 240)
COLOR_UI_BG = (25, 30, 40)
COLOR_ACCENT = (255, 165, 0)

# Cell types
CELL_EMPTY = 0
CELL_BOX = 1
CELL_FIRE = 2
CELL_WALL = 3
CELL_REFILL = 4

# Action space for RL
ACTION_UP = 0
ACTION_DOWN = 1
ACTION_LEFT = 2
ACTION_RIGHT = 3
ACTION_EXTINGUISH = 4


class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class WarehouseMap:
    """Warehouse map generator with obstacles, boxes, and refill stations."""

    @staticmethod
    def generate():
        grid = [[CELL_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Place refill stations at corners
        refill_positions = [(0, 0), (GRID_SIZE - 1, 0), (0, GRID_SIZE - 1), (GRID_SIZE - 1, GRID_SIZE - 1)]
        for x, y in refill_positions:
            grid[y][x] = CELL_REFILL

        # Place walls (random obstacles)
        wall_count = 15
        for _ in range(wall_count):
            x, y = random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2)
            if grid[y][x] == CELL_EMPTY:
                grid[y][x] = CELL_WALL

        # Place flammable boxes
        box_count = 30
        for _ in range(box_count):
            x, y = random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2)
            if grid[y][x] == CELL_EMPTY:
                grid[y][x] = CELL_BOX

        return grid, refill_positions


class GameState:
    PLAYING = 0
    GAME_OVER = 1
    VICTORY = 2
    START = 3


class FireExtinguishGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Fire Extinguish Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.grid, self.refill_positions = WarehouseMap.generate()
        self.state = GameState.START

        # Place bot at a safe location
        empty_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == CELL_EMPTY:
                    empty_cells.append((x, y))
        self.bot_pos = random.choice(empty_cells) if empty_cells else (GRID_SIZE // 2, GRID_SIZE // 2)

        # Start fire at a random box
        box_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == CELL_BOX:
                    box_cells.append((x, y))
        if box_cells:
            start_fire = random.choice(box_cells)
            self.grid[start_fire[1]][start_fire[0]] = CELL_FIRE

        self.water = MAX_WATER
        self.score = 0
        self.boxes_saved = 0
        self.boxes_lost = 0
        self.last_fire_spread = pygame.time.get_ticks()
        self.extinguishing = False
        self.extinguish_start = 0
        self.extinguish_pos = None

        # Count total boxes
        self.total_boxes = sum(row.count(CELL_BOX) for row in self.grid)
        self.total_boxes += sum(row.count(CELL_FIRE) for row in self.grid)

    def get_observation(self):
        """Return 10x10 grid observation for RL agents."""
        obs = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                if (x, y) == self.bot_pos:
                    row.append(4)  # Bot
                elif self.grid[y][x] == CELL_FIRE:
                    row.append(2)  # Fire
                elif self.grid[y][x] == CELL_BOX:
                    row.append(1)  # Box
                elif self.grid[y][x] == CELL_WALL:
                    row.append(3)  # Obstacle
                elif self.grid[y][x] == CELL_REFILL:
                    row.append(5)  # Refill station
                else:
                    row.append(0)  # Empty
            obs.append(row)
        return obs

    def get_reward(self, prev_grid, extinguished_count, burned_count):
        """Calculate reward for RL training."""
        return extinguished_count * POINTS_PER_EXTINGUISHED + burned_count * POINTS_PER_BOX_LOST

    def is_valid_cell(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

    def can_move_to(self, x, y):
        if not self.is_valid_cell(x, y):
            return False
        return self.grid[y][x] != CELL_WALL

    def move_bot(self, direction):
        if self.state != GameState.PLAYING:
            return

        dx, dy = direction
        new_x = self.bot_pos[0] + dx
        new_y = self.bot_pos[1] + dy

        if self.can_move_to(new_x, new_y):
            self.bot_pos = (new_x, new_y)

            # Check if on refill station
            if self.grid[new_y][new_x] == CELL_REFILL:
                self.water = MAX_WATER

    def extinguish_fire(self):
        if self.state != GameState.PLAYING or self.extinguishing:
            return

        bot_x, bot_y = self.bot_pos

        if self.grid[bot_y][bot_x] == CELL_FIRE:
            if self.water > 0:
                self.extinguishing = True
                self.extinguish_start = pygame.time.get_ticks()
                self.extinguish_pos = (bot_x, bot_y)
            else:
                # Need to refill
                pass

    def spread_fire(self):
        """Spread fire to adjacent flammable cells."""
        new_fire_positions = []

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == CELL_FIRE:
                    for dx, dy in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
                        nx, ny = x + dx, y + dy
                        if self.is_valid_cell(nx, ny) and self.grid[ny][nx] == CELL_BOX:
                            if (nx, ny) not in new_fire_positions:
                                new_fire_positions.append((nx, ny))

        for x, y in new_fire_positions:
            if random.random() < 0.3:  # 30% chance to spread
                self.grid[y][x] = CELL_FIRE
                self.boxes_lost += 1
                self.score += POINTS_PER_BOX_LOST

        # Check win/lose conditions
        fire_count = sum(row.count(CELL_FIRE) for row in self.grid)
        box_count = sum(row.count(CELL_BOX) for row in self.grid)

        if box_count == 0:
            self.state = GameState.VICTORY
        elif fire_count == 0:
            self.state = GameState.VICTORY

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == GameState.PLAYING:
            # Handle fire spread
            if current_time - self.last_fire_spread >= FIRE_SPREAD_INTERVAL:
                self.spread_fire()
                self.last_fire_spread = current_time

            # Handle extinguishing
            if self.extinguishing:
                if current_time - self.extinguish_start >= EXTINGUISH_TIME:
                    if self.extinguish_pos:
                        x, y = self.extinguish_pos
                        if self.grid[y][x] == CELL_FIRE:
                            self.grid[y][x] = CELL_EMPTY
                            self.water -= 1
                            self.boxes_saved += 1
                            self.score += POINTS_PER_EXTINGUISHED
                    self.extinguishing = False
                    self.extinguish_pos = None

    def step(self, action):
        """Execute one step for RL training."""
        prev_grid = [row[:] for row in self.grid]

        if action == ACTION_UP:
            self.move_bot(Direction.UP)
        elif action == ACTION_DOWN:
            self.move_bot(Direction.DOWN)
        elif action == ACTION_LEFT:
            self.move_bot(Direction.LEFT)
        elif action == ACTION_RIGHT:
            self.move_bot(Direction.RIGHT)
        elif action == ACTION_EXTINGUISH:
            self.extinguish_fire()

        # Run game update for fire spread
        self.update()

        # Calculate reward
        extinguished = self.boxes_saved
        burned = self.boxes_lost
        reward = self.get_reward(prev_grid, 0, 0)

        # Check if done
        done = self.state in [GameState.VICTORY]

        observation = self.get_observation()
        info = {"score": self.score, "water": self.water}

        return observation, reward, done, False, info

    def draw_grid(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = GRID_OFFSET_X + x * CELL_SIZE
                cell_y = GRID_OFFSET_Y + y * CELL_SIZE

                cell = self.grid[y][x]

                if cell == CELL_WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, (50, 55, 65),
                                   (cell_x + 2, cell_y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                elif cell == CELL_BOX:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Box with crate pattern
                    pygame.draw.rect(self.screen, COLOR_BOX,
                                   (cell_x + 3, cell_y + 3, CELL_SIZE - 6, CELL_SIZE - 6))
                    pygame.draw.rect(self.screen, (120, 80, 40),
                                   (cell_x + 8, cell_y + 8, CELL_SIZE - 16, CELL_SIZE - 16))
                elif cell == CELL_FIRE:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Animated fire effect
                    time_offset = pygame.time.get_ticks() // 100
                    fire_color = (
                        min(255, 200 + int(30 * (0.5 + 0.5 * (time_offset % 10) / 10))),
                        min(200, 80 + int(40 * (0.5 + 0.5 * (time_offset % 10) / 10))),
                        30
                    )
                    pygame.draw.rect(self.screen, fire_color,
                                   (cell_x + 3, cell_y + 3, CELL_SIZE - 6, CELL_SIZE - 6))
                    # Flame lines
                    for i in range(3):
                        flame_x = cell_x + 10 + i * 12
                        flame_height = 10 + (time_offset + i * 3) % 15
                        pygame.draw.line(self.screen, (255, 200, 50),
                                       (flame_x, cell_y + CELL_SIZE - 5),
                                       (flame_x, cell_y + CELL_SIZE - 5 - flame_height), 3)
                elif cell == CELL_REFILL:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    # Water station
                    center_x = cell_x + CELL_SIZE // 2
                    center_y = cell_y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, COLOR_REFILL,
                                     (center_x, center_y), CELL_SIZE // 3)
                    pygame.draw.circle(self.screen, (50, 200, 255),
                                     (center_x, center_y), CELL_SIZE // 4)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))

                # Grid lines
                pygame.draw.rect(self.screen, COLOR_GRID,
                               (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_bot(self):
        bot_x = GRID_OFFSET_X + self.bot_pos[0] * CELL_SIZE + CELL_SIZE // 2
        bot_y = GRID_OFFSET_Y + self.bot_pos[1] * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3

        # Bot glow
        glow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*COLOR_BOT, 60),
                         (CELL_SIZE // 2, CELL_SIZE // 2), radius + 6)
        self.screen.blit(glow_surface,
                        (GRID_OFFSET_X + self.bot_pos[0] * CELL_SIZE,
                         GRID_OFFSET_Y + self.bot_pos[1] * CELL_SIZE))

        # Bot body
        pygame.draw.circle(self.screen, COLOR_BOT, (bot_x, bot_y), radius)

        # Bot inner
        pygame.draw.circle(self.screen, (70, 200, 220), (bot_x, bot_y), radius - 3)

        # Water indicator
        water_bar_width = 20
        water_bar_height = 4
        water_bar_x = bot_x - water_bar_width // 2
        water_bar_y = bot_y + radius + 8

        pygame.draw.rect(self.screen, (50, 60, 70),
                        (water_bar_x, water_bar_y, water_bar_width, water_bar_height))
        fill_width = int(water_bar_width * (self.water / MAX_WATER))
        pygame.draw.rect(self.screen, COLOR_REFILL,
                        (water_bar_x, water_bar_y, fill_width, water_bar_height))

        # Extinguish effect
        if self.extinguishing and self.extinguish_pos:
            ex_x, ex_y = self.extinguish_pos
            screen_x = GRID_OFFSET_X + ex_x * CELL_SIZE + CELL_SIZE // 2
            screen_y = GRID_OFFSET_Y + ex_y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, (200, 240, 255), (screen_x, screen_y), CELL_SIZE // 2, 3)

    def draw_ui(self):
        # Top bar background
        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.line(self.screen, COLOR_ACCENT, (0, 80), (SCREEN_WIDTH, 80), 2)

        # Title
        title_text = self.font.render("FIRE EXTINGUISHER", True, COLOR_TEXT)
        self.screen.blit(title_text, (20, 15))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_ACCENT)
        score_rect = score_text.get_rect(right=SCREEN_WIDTH - 20, top=15)
        self.screen.blit(score_text, score_rect)

        # Water indicator (large)
        water_label = self.small_font.render("Water:", True, COLOR_TEXT)
        self.screen.blit(water_label, (20, 50))

        water_bg_rect = pygame.Rect(80, 50, 150, 20)
        pygame.draw.rect(self.screen, (40, 45, 55), water_bg_rect)
        pygame.draw.rect(self.screen, (60, 65, 75), water_bg_rect, 2)

        fill_width = 150 * (self.water / MAX_WATER)
        fill_color = COLOR_REFILL if self.water > 0 else (100, 50, 50)
        pygame.draw.rect(self.screen, fill_color, (80, 50, fill_width, 20))

        # Water droplets
        for i in range(self.water):
            droplet_x = 85 + i * 28
            droplet_y = 60
            pygame.draw.circle(self.screen, (255, 255, 255), (droplet_x, droplet_y), 5)

        # Statistics
        stats_text = self.small_font.render(
            f"Saved: {self.boxes_saved} | Lost: {self.boxes_lost}",
            True, (150, 160, 170)
        )
        stats_rect = stats_text.get_rect(right=SCREEN_WIDTH - 20, top=50)
        self.screen.blit(stats_text, stats_rect)

        # Time to next fire spread
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.last_fire_spread
        time_remaining = max(0, (FIRE_SPREAD_INTERVAL - time_elapsed) / 1000)

        time_text = self.small_font.render(f"Fire spread in: {time_remaining:.1f}s", True, COLOR_FIRE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 65))
        self.screen.blit(time_text, time_rect)

        # Controls hint
        hint_text = self.small_font.render(
            "Arrow Keys: Move | SPACE: Extinguish | R: Restart | ESC: Quit",
            True, (80, 90, 100)
        )
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        self.screen.blit(hint_text, hint_rect)

    def draw_start_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("FIRE EXTINGUISHER", True, COLOR_ACCENT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render(
            "Extinguish spreading fires before they consume the warehouse",
            True, COLOR_TEXT
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(subtitle, subtitle_rect)

        instructions = [
            "Move with Arrow Keys",
            "Press SPACE to extinguish fire",
            "Refill at blue water stations (corners)",
            "Fire spreads every 5 seconds"
        ]

        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, COLOR_BOT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 25))
            self.screen.blit(text, text_rect)

        hint = self.small_font.render("Press any key to start", True, COLOR_ACCENT)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
        self.screen.blit(hint, hint_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        title_text = "VICTORY!" if self.state == GameState.VICTORY else "GAME OVER"
        title_color = COLOR_ACCENT if self.state == GameState.VICTORY else COLOR_FIRE
        title = self.font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(score_text, score_rect)

        stats = [
            f"Boxes Saved: {self.boxes_saved}",
            f"Boxes Lost: {self.boxes_lost}"
        ]

        for i, line in enumerate(stats):
            text = self.small_font.render(line, True, (150, 160, 170))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 30))
            self.screen.blit(text, text_rect)

        hint = self.small_font.render("Press R to play again or ESC to quit", True, COLOR_BOT)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(hint, hint_rect)

    def draw(self):
        self.screen.fill(COLOR_BG)

        self.draw_grid()
        self.draw_bot()
        self.draw_ui()

        if self.state == GameState.START:
            self.draw_start_screen()
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            self.draw_game_over()

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                self.reset_game()

            if self.state == GameState.START:
                self.state = GameState.PLAYING
            elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                if event.key == pygame.K_r:
                    self.reset_game()
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_UP:
                    self.move_bot(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.move_bot(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.move_bot(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.move_bot(Direction.RIGHT)
                elif event.key == pygame.K_SPACE:
                    self.extinguish_fire()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = FireExtinguishGame()
    game.run()


if __name__ == "__main__":
    main()
