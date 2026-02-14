"""Main game logic for Vector Balloon Pop Puzzle."""

import math
import random
import pygame
from config import *


class Balloon:
    """Represents a balloon on the grid."""

    def __init__(self, col, row, color_idx):
        self.col = col
        self.row = row
        self.color_idx = color_idx
        self.color = BALLOON_COLORS[color_idx]
        self.radius = CELL_SIZE // 2 - 4
        self.y = GRID_START_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.target_y = self.y
        self.popping = False
        self.pop_scale = 1.0
        self.pop_speed = 0.1

    def update(self):
        """Update balloon animation."""
        if self.popping:
            self.pop_scale -= self.pop_speed
            return self.pop_scale <= 0
        return False

    def move_towards_target(self):
        """Move balloon towards target position (floating up effect)."""
        if self.y > self.target_y:
            self.y -= BALLOON_FLOAT_SPEED
            if self.y < self.target_y:
                self.y = self.target_y

    def draw(self, surface):
        """Draw the balloon."""
        if self.popping:
            radius = int(self.radius * self.pop_scale)
            if radius <= 0:
                return
        else:
            radius = self.radius

        x = GRID_START_X + self.col * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(surface, self.color, (int(x), int(self.y)), radius)
        pygame.draw.circle(surface, COLOR_WHITE, (int(x - radius * 0.3), int(self.y - radius * 0.3)), int(radius * 0.2))


class Dart:
    """Represents a dart fired by the launcher."""

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = DART_SPEED
        self.active = True
        self.radius = 5

    def update(self):
        """Update dart position."""
        self.x += math.cos(self.angle) * self.speed
        self.y -= math.sin(self.angle) * self.speed

        # Check bounds
        if (self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False

    def draw(self, surface):
        """Draw the dart."""
        end_x = self.x - math.cos(self.angle) * 15
        end_y = self.y + math.sin(self.angle) * 15
        pygame.draw.line(surface, COLOR_BLACK, (self.x, self.y), (end_x, end_y), 3)
        pygame.draw.circle(surface, COLOR_GRAY, (int(self.x), int(self.y)), self.radius)


class Launcher:
    """Represents the player's dart launcher."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = LAUNCHER_Y
        self.width = LAUNCHER_WIDTH
        self.height = LAUNCHER_HEIGHT
        self.angle = math.pi / 2  # Pointing straight up

    def move_left(self):
        """Move launcher left."""
        min_x = GRID_START_X
        if self.x > min_x:
            self.x -= LAUNCHER_SPEED

    def move_right(self):
        """Move launcher right."""
        max_x = GRID_START_X + GRID_COLS * CELL_SIZE
        if self.x < max_x:
            self.x += LAUNCHER_SPEED

    def adjust_angle(self, delta):
        """Adjust aim angle."""
        self.angle = max(math.pi / 4, min(3 * math.pi / 4, self.angle + delta))

    def get_tip_position(self):
        """Get the tip position for dart spawning."""
        tip_x = self.x + math.cos(self.angle) * self.height // 2
        tip_y = self.y - math.sin(self.angle) * self.height // 2
        return tip_x, tip_y

    def draw(self, surface):
        """Draw the launcher."""
        tip_x, tip_y = self.get_tip_position()

        # Draw launcher body
        base_x = self.x - math.cos(self.angle) * self.height // 2
        base_y = self.y + math.sin(self.angle) * self.height // 2

        pygame.draw.line(surface, COLOR_GRAY, (base_x, base_y), (tip_x, tip_y), 8)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.x), int(self.y)), 15)


class Game:
    """Main game class managing all game state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Balloon Pop Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset game to initial state."""
        self.balloons = []
        self.darts = []
        self.launcher = Launcher()
        self.score = 0
        self.darts_remaining = DART_LIMIT
        self.game_over = False
        self.won = False
        self.pop_queue = []
        self.generate_balloons()

    def generate_balloons(self):
        """Generate random balloons on the grid."""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if random.random() < 0.85:  # 85% fill rate
                    color_idx = random.randint(0, len(BALLOON_COLORS) - 1)
                    self.balloons.append(Balloon(col, row, color_idx))

    def get_balloon_at(self, col, row):
        """Get balloon at grid position."""
        for balloon in self.balloons:
            if not balloon.popping and balloon.col == col and balloon.row == row:
                return balloon
        return None

    def get_neighbors(self, balloon):
        """Get adjacent balloons of the same color."""
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for dx, dy in directions:
            neighbor = self.get_balloon_at(balloon.col + dx, balloon.row + dy)
            if neighbor and neighbor.color_idx == balloon.color_idx:
                neighbors.append(neighbor)

        return neighbors

    def find_chain(self, start_balloon):
        """Find all connected balloons of the same color."""
        visited = set()
        queue = [start_balloon]
        chain = []

        while queue:
            balloon = queue.pop(0)
            if balloon in visited:
                continue

            visited.add(balloon)
            chain.append(balloon)

            for neighbor in self.get_neighbors(balloon):
                if neighbor not in visited:
                    queue.append(neighbor)

        return chain

    def pop_chain(self, chain):
        """Pop a chain of balloons and update score."""
        popped_count = len(chain)
        self.score += popped_count ** 2 * 10

        for balloon in chain:
            if not balloon.popping:
                balloon.popping = True
                self.pop_queue.append(balloon)

    def check_dart_collision(self, dart):
        """Check if dart hits any balloon."""
        for balloon in self.balloons:
            if balloon.popping:
                continue

            bx = GRID_START_X + balloon.col * CELL_SIZE + CELL_SIZE // 2
            by = balloon.y

            distance = math.sqrt((dart.x - bx) ** 2 + (dart.y - by) ** 2)

            if distance < balloon.radius + dart.radius:
                return balloon

        return None

    def update_balloon_positions(self):
        """Update balloon positions after pops (floating up)."""
        for col in range(GRID_COLS):
            balloons_in_col = sorted(
                [b for b in self.balloons if not b.popping and b.col == col],
                key=lambda b: b.row
            )

            for new_row, balloon in enumerate(balloons_in_col):
                balloon.row = new_row
                balloon.target_y = GRID_START_Y + new_row * CELL_SIZE + CELL_SIZE // 2

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.launcher.move_left()
        if keys[pygame.K_RIGHT]:
            self.launcher.move_right()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    if self.darts_remaining > 0:
                        tip_x, tip_y = self.launcher.get_tip_position()
                        self.darts.append(Dart(tip_x, tip_y, self.launcher.angle))
                        self.darts_remaining -= 1
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False

        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Update darts
        for dart in self.darts[:]:
            dart.update()

            if not dart.active:
                self.darts.remove(dart)
                continue

            hit_balloon = self.check_dart_collision(dart)
            if hit_balloon:
                chain = self.find_chain(hit_balloon)
                self.pop_chain(chain)
                self.darts.remove(dart)

        # Update popping balloons
        for balloon in self.pop_queue[:]:
            if balloon.update():
                self.balloons.remove(balloon)
                self.pop_queue.remove(balloon)

        # Update balloon positions
        for balloon in self.balloons:
            balloon.move_towards_target()

        # Check if update needed after pops
        if self.pop_queue:
            self.update_balloon_positions()

        # Check win/lose conditions
        active_balloons = [b for b in self.balloons if not b.popping]
        if not active_balloons:
            self.game_over = True
            self.won = True
        elif self.darts_remaining == 0 and not self.darts:
            self.game_over = True

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BLACK)

        # Draw grid outline
        grid_width = GRID_COLS * CELL_SIZE
        grid_height = GRID_ROWS * CELL_SIZE
        pygame.draw.rect(self.screen, COLOR_GRAY,
                        (GRID_START_X - 2, GRID_START_Y - 2,
                         grid_width + 4, grid_height + 4), 2)

        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(self.screen)

        # Draw darts
        for dart in self.darts:
            dart.draw(self.screen)

        # Draw launcher
        self.launcher.draw(self.screen)

        # Draw trajectory guide
        tip_x, tip_y = self.launcher.get_tip_position()
        guide_length = 50
        guide_x = tip_x + math.cos(self.launcher.angle) * guide_length
        guide_y = tip_y - math.sin(self.launcher.angle) * guide_length
        pygame.draw.line(self.screen, (100, 100, 100), (tip_x, tip_y), (guide_x, guide_y), 1)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_WHITE)
        darts_text = self.font.render(f"Darts: {self.darts_remaining}", True, COLOR_WHITE)
        self.screen.blit(score_text, (20, 10))
        self.screen.blit(darts_text, (SCREEN_WIDTH - 150, 10))

        # Draw game over message
        if self.game_over:
            if self.won:
                msg = "YOU WIN! Press R to restart"
                color = (46, 204, 113)
            else:
                msg = "GAME OVER! Press R to restart"
                color = (231, 76, 60)

            text = self.font.render(msg, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, COLOR_BLACK, rect.inflate(20, 10))
            self.screen.blit(text, rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
