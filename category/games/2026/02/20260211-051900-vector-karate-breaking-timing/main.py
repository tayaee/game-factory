"""
Vector Karate Breaking - Timing Game

A precision timing game where the player must strike at the exact moment
a power gauge reaches the target zone to break materials.
"""

import pygame
import sys
import math
from dataclasses import dataclass
from typing import List, Tuple


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (30, 30, 35)
COLOR_FG = (220, 220, 220)
COLOR_GAUGE_BG = (50, 50, 60)
COLOR_GAUGE_FILL = (70, 180, 255)
COLOR_TARGET_ZONE = (255, 80, 80)
COLOR_MARKER = (255, 255, 255)
COLOR_TEXT = (255, 255, 255)

# Material definitions
MATERIALS = [
    {"name": "Thin Wood", "color": (180, 140, 80), "threshold": 85, "zone_width": 15},
    {"name": "Thick Wood", "color": (160, 120, 60), "threshold": 88, "zone_width": 12},
    {"name": "Stone", "color": (120, 120, 130), "threshold": 90, "zone_width": 10},
    {"name": "Ice", "color": (150, 200, 255), "threshold": 92, "zone_width": 8},
    {"name": "Diamond", "color": (200, 230, 255), "threshold": 95, "zone_width": 6},
]

# Gauge settings
GAUGE_X = 500
GAUGE_Y = 100
GAUGE_WIDTH = 40
GAUGE_HEIGHT = 400
GAUGE_MIN_SPEED = 2.0
GAUGE_MAX_SPEED = 8.0


@dataclass
class GameState:
    score: int = 0
    lives: int = 3
    material_index: int = 0
    gauge_position: float = 0.0  # 0-100
    gauge_direction: int = 1  # 1 or -1
    gauge_speed: float = GAUGE_MIN_SPEED
    broken: bool = False
    missed: bool = False
    game_over: bool = False
    level_complete: bool = False

    @property
    def current_material(self) -> dict:
        return MATERIALS[min(self.material_index, len(MATERIALS) - 1)]

    @property
    def target_zone_min(self) -> float:
        m = self.current_material
        return max(0, m["threshold"] - m["zone_width"] / 2)

    @property
    def target_zone_max(self) -> float:
        m = self.current_material
        return min(100, m["threshold"] + m["zone_width"] / 2)


class KarateGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Karate Breaking - Timing Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.state = GameState()
        self.particles: List[Tuple[int, int, int, int]] = []
        self.shake_offset = [0, 0]
        self.shake_timer = 0

    def reset_block(self):
        """Reset for the next block attempt."""
        self.state.broken = False
        self.state.missed = False
        self.state.gauge_position = 0.0
        self.state.gauge_direction = 1

    def next_level(self):
        """Advance to the next material."""
        self.state.material_index += 1
        self.state.gauge_speed = min(
            GAUGE_MAX_SPEED,
            GAUGE_MIN_SPEED + (self.state.material_index * 0.8)
        )
        if self.state.material_index >= len(MATERIALS):
            self.state.material_index = 0  # Loop back to beginning
            self.state.gauge_speed = GAUGE_MIN_SPEED
        self.reset_block()

    def update_gauge(self):
        """Update the oscillating gauge."""
        if self.state.broken or self.state.missed:
            return

        self.state.gauge_position += self.state.gauge_speed * self.state.gauge_direction

        if self.state.gauge_position >= 100:
            self.state.gauge_position = 100
            self.state.gauge_direction = -1
        elif self.state.gauge_position <= 0:
            self.state.gauge_position = 0
            self.state.gauge_direction = 1

    def strike(self):
        """Attempt to break the block."""
        if self.state.broken or self.state.missed or self.state.game_over:
            return

        pos = self.state.gauge_position
        zone_min = self.state.target_zone_min
        zone_max = self.state.target_zone_max

        if zone_min <= pos <= zone_max:
            # Successful break
            accuracy = (pos - zone_min) / (zone_max - zone_min) if zone_max > zone_min else 1.0
            bonus = int(accuracy * 50)
            self.state.score += 100 + bonus
            self.state.broken = True
            self.create_particles(20)
            self.trigger_shake(10)
            self.state.level_complete = True
        else:
            # Missed
            self.state.lives -= 1
            self.state.missed = True
            self.trigger_shake(5)

            if self.state.lives <= 0:
                self.state.game_over = True

    def create_particles(self, count: int):
        """Create break particles."""
        center_x = 200
        center_y = 350
        material = self.state.current_material
        color = material["color"]

        for _ in range(count):
            import random
            self.particles.append([
                center_x,
                center_y,
                random.uniform(-5, 5),
                random.uniform(-10, -2)
            ])

    def trigger_shake(self, frames: int):
        """Trigger screen shake."""
        self.shake_timer = frames

    def update_particles(self):
        """Update particle positions."""
        new_particles = []
        for p in self.particles:
            x, y, vx, vy = p
            x += vx
            y += vy
            vy += 0.5  # Gravity
            if y < SCREEN_HEIGHT:
                new_particles.append([x, y, vx, vy])
        self.particles = new_particles

    def update_shake(self):
        """Update screen shake effect."""
        if self.shake_timer > 0:
            import random
            self.shake_offset = [random.randint(-4, 4), random.randint(-4, 4)]
            self.shake_timer -= 1
        else:
            self.shake_offset = [0, 0]

    def draw_gauge(self):
        """Draw the power gauge."""
        x = GAUGE_X + self.shake_offset[0]
        y = GAUGE_Y + self.shake_offset[1]

        # Background
        pygame.draw.rect(self.screen, COLOR_GAUGE_BG,
                         (x, y, GAUGE_WIDTH, GAUGE_HEIGHT))

        # Target zone
        zone_min = self.state.target_zone_min
        zone_max = self.state.target_zone_max
        zone_y = y + GAUGE_HEIGHT - (zone_max / 100 * GAUGE_HEIGHT)
        zone_h = (zone_max - zone_min) / 100 * GAUGE_HEIGHT
        pygame.draw.rect(self.screen, COLOR_TARGET_ZONE,
                         (x, zone_y, GAUGE_WIDTH, zone_h))

        # Fill based on current position
        fill_height = (self.state.gauge_position / 100) * GAUGE_HEIGHT
        fill_y = y + GAUGE_HEIGHT - fill_height
        pygame.draw.rect(self.screen, COLOR_GAUGE_FILL,
                         (x + 2, fill_y, GAUGE_WIDTH - 4, fill_height))

        # Border
        pygame.draw.rect(self.screen, COLOR_FG,
                         (x, y, GAUGE_WIDTH, GAUGE_HEIGHT), 2)

        # Current position marker
        marker_y = fill_y
        pygame.draw.line(self.screen, COLOR_MARKER,
                          (x - 5, marker_y), (x + GAUGE_WIDTH + 5, marker_y), 3)

        # Labels
        label = self.font_small.render("POWER", True, COLOR_TEXT)
        self.screen.blit(label, (x + GAUGE_WIDTH // 2 - label.get_width() // 2, y - 25))

    def draw_block(self):
        """Draw the material block to break."""
        if self.state.broken and len(self.particles) == 0:
            return

        x = 150 + self.shake_offset[0]
        y = 300 + self.shake_offset[1]
        width = 100
        height = 100

        if self.state.broken:
            # Draw particles only
            return

        material = self.state.current_material
        color = material["color"]

        # Draw block layers
        layers = 1 + self.state.material_index
        for i in range(layers):
            layer_y = y - i * 5
            pygame.draw.rect(self.screen, color,
                             (x, layer_y, width, height))
            pygame.draw.rect(self.screen, (min(color[0] + 30, 255),
                                            min(color[1] + 30, 255),
                                            min(color[2] + 30, 255)),
                             (x, layer_y, width, height), 2)

        # Draw karate figure (simplified)
        # Body
        pygame.draw.line(self.screen, COLOR_FG, (280, 350), (280, 280), 3)
        # Head
        pygame.draw.circle(self.screen, COLOR_FG, (280, 265), 15, 2)
        # Arms
        pygame.draw.line(self.screen, COLOR_FG, (280, 290), (260, 320), 3)
        pygame.draw.line(self.screen, COLOR_FG, (280, 290), (300, 280), 3)
        # Legs
        pygame.draw.line(self.screen, COLOR_FG, (280, 350), (270, 400), 3)
        pygame.draw.line(self.screen, COLOR_FG, (280, 350), (290, 400), 3)

    def draw_particles(self):
        """Draw break particles."""
        material = self.state.current_material
        color = material["color"]

        for p in self.particles:
            x, y, vx, vy = p
            pygame.draw.circle(self.screen, color,
                             (int(x + self.shake_offset[0]),
                              int(y + self.shake_offset[1])), 4)

    def draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.font_medium.render(f"SCORE: {self.state.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Lives
        lives_text = self.font_medium.render(f"LIVES: {self.state.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (20, 55))

        # Material
        material = self.state.current_material
        mat_text = self.font_medium.render(material["name"], True, COLOR_TEXT)
        self.screen.blit(mat_text, (20, 90))

        # Instructions
        if not self.state.broken and not self.state.missed:
            inst_text = self.font_small.render("Press SPACE to strike!", True, (150, 150, 150))
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 40))

        # Result messages
        if self.state.broken:
            result_text = self.font_large.render("BROKEN!", True, (100, 255, 100))
            self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 150))
            cont_text = self.font_small.render("Press SPACE for next block", True, COLOR_TEXT)
            self.screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, 200))

        elif self.state.missed:
            result_text = self.font_large.render("MISSED!", True, (255, 100, 100))
            self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 150))
            cont_text = self.font_small.render("Press SPACE to try again", True, COLOR_TEXT)
            self.screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, 200))

        if self.state.game_over:
            over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            final_text = self.font_medium.render(f"Final Score: {self.state.score}", True, COLOR_TEXT)
            self.screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            restart_text = self.font_small.render("Press R to restart or ESC to quit", True, COLOR_TEXT)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def draw(self):
        """Main draw function."""
        self.screen.fill(COLOR_BG)

        # Title
        title = self.font_large.render("KARATE BREAKING", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        self.draw_gauge()
        self.draw_block()
        self.draw_particles()
        self.draw_ui()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        if self.state.game_over:
                            continue
                        elif self.state.broken:
                            self.next_level()
                        elif self.state.missed:
                            if self.state.lives > 0:
                                self.reset_block()
                            else:
                                self.state.game_over = True
                        else:
                            self.strike()
                    elif event.key == pygame.K_r and self.state.game_over:
                        # Restart game
                        self.state = GameState()

            # Update
            self.update_gauge()
            self.update_particles()
            self.update_shake()

            # Draw
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = KarateGame()
    game.run()
