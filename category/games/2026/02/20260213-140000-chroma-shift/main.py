"""Chroma Shift - Color matching puzzle game."""

import pygame
import random
import math
import colorsys
from typing import List, Tuple, Optional


class Tile:
    """A colored tile that shifts hue over time."""

    def __init__(self, x: int, y: int, size: int, hue: float):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_hue = hue
        self.current_hue = hue
        self.size = size
        self.scale_phase = random.random() * math.pi * 2

    def update(self, dt: float, shift_speed: float):
        """Update the tile's hue and pulsing animation."""
        self.current_hue = (self.current_hue + shift_speed * dt) % 1.0
        self.scale_phase += dt * 2

    def get_color(self) -> Tuple[int, int, int]:
        """Get current RGB color from hue."""
        r, g, b = colorsys.hsv_to_rgb(self.current_hue, 0.8, 0.9)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_scale(self) -> float:
        """Get pulsing scale factor."""
        return 0.9 + 0.1 * math.sin(self.scale_phase)

    def hue_distance(self, target_hue: float) -> float:
        """Calculate circular distance between hues (0 to 0.5)."""
        diff = abs(self.current_hue - target_hue)
        return min(diff, 1 - diff)


class Particle:
    """Visual feedback particle."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        angle = random.random() * math.pi * 2
        speed = random.random() * 100 + 50
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.random() * 2 + 1

    def update(self, dt: float) -> bool:
        """Update particle, return False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        """Draw the particle."""
        if self.life > 0:
            alpha = int(self.life * 255)
            size = int(4 * self.life)
            if size > 0:
                color = (*self.color[:3], alpha)
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                surface.blit(surf, (int(self.x) - size, int(self.y) - size))


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chroma Shift")

        self.width = 800
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Game settings
        self.grid_size = 4
        self.tile_size = 80
        self.grid_offset_x = (self.width - self.grid_size * self.tile_size) // 2
        self.grid_offset_y = 200

        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.lives = 3
        self.combo = 0

        # Color matching
        self.target_hue = 0.0
        self.match_tolerance = 0.08
        self.shift_speed = 0.02
        self.new_target_delay = 0.0

        # Tiles and particles
        self.tiles: List[Tile] = []
        self.particles: List[Particle] = []

        # Colors
        self.bg_color = (20, 20, 30)
        self.text_color = (220, 220, 220)
        self.accent_color = (100, 200, 255)

        # Initialize
        self.init_grid()
        self.new_target()

    def init_grid(self):
        """Create initial grid of tiles."""
        self.tiles = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = self.grid_offset_x + col * self.tile_size
                y = self.grid_offset_y + row * self.tile_size
                hue = random.random()
                self.tiles.append(Tile(x, y, self.tile_size, hue))

    def new_target(self):
        """Set a new target hue based on current tiles."""
        if self.tiles:
            # Pick a tile near center of screen to be the target
            center_idx = len(self.tiles) // 2 + random.randint(-2, 2)
            center_idx = max(0, min(center_idx, len(self.tiles) - 1))
            self.target_hue = self.tiles[center_idx].current_hue

    def get_target_color(self) -> Tuple[int, int, int]:
        """Get RGB color for target hue."""
        r, g, b = colorsys.hsv_to_rgb(self.target_hue, 0.9, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    def check_match(self, tile: Tile) -> bool:
        """Check if tile matches target color."""
        return tile.hue_distance(self.target_hue) <= self.match_tolerance

    def spawn_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
        """Spawn particle effects."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on tiles."""
        if self.game_over:
            return

        clicked = False
        for tile in self.tiles:
            if tile.rect.collidepoint(pos):
                clicked = True
                if self.check_match(tile):
                    # Success!
                    points = 10 + self.combo * 5
                    self.score += points
                    self.combo += 1

                    # Particle effect
                    center_x = tile.rect.centerx
                    center_y = tile.rect.centery
                    self.spawn_particles(center_x, center_y, tile.get_color(), 15)

                    # Replace tile with new random hue
                    tile.base_hue = random.random()
                    tile.current_hue = tile.base_hue

                    # New target
                    self.new_target()

                    # Increase difficulty
                    if self.score % 50 == 0:
                        self.shift_speed += 0.005
                        self.match_tolerance = max(0.05, self.match_tolerance - 0.003)
                else:
                    # Wrong tile
                    self.combo = 0
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Miss particles
                        center_x = tile.rect.centerx
                        center_y = tile.rect.centery
                        self.spawn_particles(center_x, center_y, (200, 50, 50), 8)
                break

        # Clicked empty space
        if not clicked:
            self.combo = 0
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True

    def reset(self):
        """Reset the game."""
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.shift_speed = 0.02
        self.match_tolerance = 0.08
        self.game_over = False
        self.particles.clear()
        self.init_grid()
        self.new_target()

    def update(self, dt: float):
        """Update game state."""
        if self.game_over:
            return

        # Update tiles
        for tile in self.tiles:
            tile.update(dt, self.shift_speed)

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self):
        """Draw the game."""
        self.screen.fill(self.bg_color)

        # Draw title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("CHROMA SHIFT", True, self.accent_color)
        title_rect = title.get_rect(centerx=self.width // 2, y=30)
        self.screen.blit(title, title_rect)

        # Draw target color indicator
        target_color = self.get_target_color()
        target_rect = pygame.Rect(0, 100, self.width, 60)
        pygame.draw.rect(self.screen, target_color, target_rect)

        # Draw target label
        font = pygame.font.Font(None, 32)
        label = font.render("TARGET COLOR", True, (0, 0, 0))
        label_rect = label.get_rect(centerx=self.width // 2, y=115)
        self.screen.blit(label, label_rect)

        # Draw tiles
        for tile in self.tiles:
            scale = tile.get_scale()
            color = tile.get_color()
            scaled_size = int(tile.size * scale)
            scaled_rect = pygame.Rect(
                tile.rect.centerx - scaled_size // 2,
                tile.rect.centery - scaled_size // 2,
                scaled_size,
                scaled_size
            )
            pygame.draw.rect(self.screen, color, scaled_rect, border_radius=8)

            # Highlight if matches target
            if self.check_match(tile):
                pygame.draw.rect(self.screen, (255, 255, 255), scaled_rect, 3, border_radius=8)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw HUD
        hud_font = pygame.font.Font(None, 28)
        score_text = hud_font.render(f"Score: {self.score}", True, self.text_color)
        self.screen.blit(score_text, (20, 20))

        # Draw lives
        lives_text = hud_font.render(f"Lives: {self.lives}", True, self.text_color)
        self.screen.blit(lives_text, (self.width - 120, 20))

        # Draw combo
        if self.combo > 0:
            combo_text = hud_font.render(f"Combo: x{self.combo}", True, (255, 200, 100))
            self.screen.blit(combo_text, (self.width // 2 - 50, 20))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            go_font = pygame.font.Font(None, 64)
            go_text = go_font.render("GAME OVER", True, (255, 100, 100))
            go_rect = go_text.get_rect(centerx=self.width // 2, y=self.height // 2 - 50)
            self.screen.blit(go_text, go_rect)

            final_score = hud_font.render(f"Final Score: {self.score}", True, self.text_color)
            score_rect = final_score.get_rect(centerx=self.width // 2, y=self.height // 2 + 20)
            self.screen.blit(final_score, score_rect)

            restart_font = pygame.font.Font(None, 32)
            restart = restart_font.render("Press R to restart or ESC to quit", True, (150, 150, 150))
            restart_rect = restart.get_rect(centerx=self.width // 2, y=self.height // 2 + 70)
            self.screen.blit(restart, restart_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)

            self.update(dt)
            self.draw()

        pygame.quit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
