"""Main game logic for Vector Hextris."""

import math
import random
import pygame
from config import *
from entities import Block, FallingBar, Hexagon


class Game:
    """Main game class managing state, rendering, and input."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        self.reset()

    def reset(self):
        """Reset game to initial state."""
        self.hexagon = Hexagon(self.center_x, self.center_y)
        self.falling_bars = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.fall_speed = FALL_SPEED_INITIAL
        self.spawn_interval = SPAWN_INTERVAL_INITIAL

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_LEFT:
                        self.hexagon.rotate(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.hexagon.rotate(1)

        return True

    def spawn_bar(self):
        """Spawn a new falling bar from a random side."""
        side = random.randint(0, HEXAGON_SIDES - 1)
        color = random.randint(0, len(BLOCK_COLORS) - 1)
        self.falling_bars.append(FallingBar(side, color))

    def update_falling_bars(self):
        """Update positions of falling bars and check collisions."""
        bars_to_remove = []

        for bar in self.falling_bars:
            bar.distance -= self.fall_speed

            # Check if bar reached the hexagon
            if bar.distance <= HEXAGON_RADIUS:
                # Add blocks to the corresponding side
                for block_data in bar.blocks:
                    block = Block(block_data['color_index'], bar.side_index, 0)
                    self.hexagon.add_block_to_side(bar.side_index, block)

                bars_to_remove.append(bar)

                # Check for game over
                if self.hexagon.get_max_stack_height() > MAX_STACK_HEIGHT:
                    self.game_over = True

        # Remove collided bars
        for bar in bars_to_remove:
            self.falling_bars.remove(bar)

    def check_and_clear_matches(self):
        """Check for matching blocks and clear them."""
        matches = self.hexagon.check_matches()
        if matches:
            # Create a set of blocks to remove
            to_remove = set()
            for match in matches:
                for side_idx, block_idx in match:
                    to_remove.add((side_idx, block_idx))

            # Remove blocks from each side (in reverse order to maintain indices)
            for side_idx, block_idx in sorted(to_remove, reverse=True):
                if block_idx < len(self.hexagon.sides[side_idx]):
                    self.hexagon.sides[side_idx].pop(block_idx)

            # Calculate score
            blocks_cleared = len(to_remove)
            self.score += int(blocks_cleared * SCORE_PER_BLOCK * (1 + self.fall_speed * 0.2))

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Increase speed over time
        if self.fall_speed < FALL_SPEED_MAX:
            self.fall_speed += SPEED_INCREASE_RATE

        # Decrease spawn interval over time
        if self.spawn_interval > SPAWN_INTERVAL_MIN:
            self.spawn_interval -= 0.01

        # Spawn new bars
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_bar()

        # Update falling bars
        self.update_falling_bars()

        # Check for matches
        self.check_and_clear_matches()

    def draw_hexagon(self):
        """Draw the central hexagon."""
        vertices = self.hexagon.get_hexagon_vertices()
        pygame.draw.polygon(self.screen, COLOR_HEXAGON, vertices)
        pygame.draw.polygon(self.screen, COLOR_HEXAGON_BORDER, vertices, 3)

    def draw_stacked_blocks(self):
        """Draw blocks stacked on hexagon sides."""
        for side_idx, blocks in enumerate(self.hexagon.sides):
            (x1, y1), (x2, y2) = self.hexagon.get_side_vertices(side_idx)
            normal = self.hexagon.get_side_normal(side_idx)

            # Calculate side direction vector
            side_dx = x2 - x1
            side_dy = y2 - y1
            side_length = math.sqrt(side_dx ** 2 + side_dy ** 2)
            side_dx /= side_length
            side_dy /= side_length

            for i, block in enumerate(blocks):
                # Position block along the side
                offset_distance = (i - len(blocks) / 2) * (BLOCK_WIDTH + 4)

                # Calculate block position
                base_x = (x1 + x2) / 2 + side_dx * offset_distance
                base_y = (y1 + y2) / 2 + side_dy * offset_distance

                # Move outward from hexagon
                stack_offset = (i + 1) * (BLOCK_HEIGHT + 2)
                block_x = base_x + normal[0] * (HEXAGON_RADIUS / 2 + stack_offset)
                block_y = base_y + normal[1] * (HEXAGON_RADIUS / 2 + stack_offset)

                # Draw block (as a rectangle rotated to align with side)
                block_surf = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
                block_surf.fill(block.color)
                block_surf.set_colorkey((0, 0, 0))

                # Rotate block to align with side
                angle = math.degrees(math.atan2(-normal[1], normal[0]))
                rotated_surf = pygame.transform.rotate(block_surf, angle)

                rect = rotated_surf.get_rect(center=(block_x, block_y))
                self.screen.blit(rotated_surf, rect)

    def draw_falling_bars(self):
        """Draw falling bars approaching the hexagon."""
        for bar in self.falling_bars:
            normal = self.hexagon.get_side_normal(bar.side_index)
            (x1, y1), (x2, y2) = self.hexagon.get_side_vertices(bar.side_index)

            # Calculate side direction vector
            side_dx = x2 - x1
            side_dy = y2 - y1
            side_length = math.sqrt(side_dx ** 2 + side_dy ** 2)
            side_dx /= side_length
            side_dy /= side_length

            color = BLOCK_COLORS[bar.color_index]

            for block_data in bar.blocks:
                # Position along the side
                offset_distance = block_data['offset']

                # Calculate position at current distance
                base_x = (x1 + x2) / 2 + side_dx * offset_distance
                base_y = (y1 + y2) / 2 + side_dy * offset_distance

                # Move outward by current distance
                block_x = base_x + normal[0] * bar.distance
                block_y = base_y + normal[1] * bar.distance

                # Draw block
                block_rect = pygame.Rect(
                    block_x - block_data['width'] / 2,
                    block_y - block_data['height'] / 2,
                    block_data['width'],
                    block_data['height']
                )
                pygame.draw.rect(self.screen, color, block_rect)

    def draw_limit_line(self):
        """Draw the limit line indicator."""
        # Draw a faint circle indicating the danger zone
        limit_radius = HEXAGON_RADIUS + MAX_STACK_HEIGHT * (BLOCK_HEIGHT + 4)
        pygame.draw.circle(
            self.screen,
            COLOR_LIMIT_LINE,
            (self.center_x, self.center_y),
            limit_radius,
            1
        )

    def draw_ui(self):
        """Draw user interface elements."""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Speed indicator
        speed_text = self.font_small.render(
            f"Speed: {self.fall_speed:.1f}x",
            True,
            COLOR_TEXT
        )
        self.screen.blit(speed_text, (10, 40))

        # Stack height indicator
        max_height = self.hexagon.get_max_stack_height()
        height_color = COLOR_TEXT if max_height < MAX_STACK_HEIGHT * 0.7 else COLOR_LIMIT_LINE
        height_text = self.font_small.render(
            f"Stack: {max_height}/{MAX_STACK_HEIGHT}",
            True,
            height_color
        )
        self.screen.blit(height_text, (10, 60))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, COLOR_GAME_OVER)
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        restart_text = self.font_small.render("Press R to restart or Q to quit", True, COLOR_TEXT)

        game_over_rect = game_over_text.get_rect(center=(self.center_x, self.center_y - 50))
        score_rect = score_text.get_rect(center=(self.center_x, self.center_y + 10))
        restart_rect = restart_text.get_rect(center=(self.center_x, self.center_y + 60))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def render(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        if not self.game_over:
            self.draw_limit_line()
            self.draw_hexagon()
            self.draw_stacked_blocks()
            self.draw_falling_bars()
            self.draw_ui()
        else:
            self.draw_hexagon()
            self.draw_stacked_blocks()
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
