"""
Vector Frenzy: Fruit Ninja Lite

A simplified 2D physics-based slicing game. Slice falling fruits while avoiding bombs.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
SLICE_TRAIL_COLOR = (255, 255, 100)

# Fruit colors
FRUIT_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 200, 100),  # Orange
    (255, 100, 255),  # Purple
    (100, 255, 255),  # Cyan
]

BOMB_COLOR = (255, 50, 50)
BOMB_SPIKE_COLOR = (200, 0, 0)

# Game settings
FRUIT_RADIUS = 30
BOMB_RADIUS = 35
GRAVITY = 0.15
SLICE_THRESHOLD = 0.02  # Minimum speed to count as a slice

# Scoring
FRUIT_SCORE = 10
MISS_PENALTY = -5
BOMB_PENALTY = "Game Over"


class TrailPoint:
    """A point in the slice trail."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.life = 1.0  # Life from 1.0 to 0.0

    def update(self) -> bool:
        """Update trail point life. Returns False when dead."""
        self.life -= 0.05
        return self.life > 0


class GameObject:
    """Base class for falling objects."""

    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.alive = True
        self.sliced = False

    def update(self) -> bool:
        """Update position. Returns False when off screen."""
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY

        # Check if off screen (bottom)
        if self.y - self.radius > SCREEN_HEIGHT:
            return False

        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object."""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def contains_point(self, px: float, py: float) -> bool:
        """Check if point is inside this object."""
        dx = self.x - px
        dy = self.y - py
        return dx * dx + dy * dy <= self.radius * self.radius


class Fruit(GameObject):
    """A sliceable fruit."""

    def __init__(self, x: float, y: float, vx: float, vy: float):
        color = random.choice(FRUIT_COLORS)
        super().__init__(x, y, vx, vy, FRUIT_RADIUS, color)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the fruit with a simple outline."""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)

    def slice(self) -> Tuple['FruitHalf', 'FruitHalf']:
        """Slice the fruit into two halves."""
        self.sliced = True
        self.alive = False

        # Create two halves moving apart
        dx = self.vx
        dy = self.vy
        perp_x = -dy * 0.5
        perp_y = dx * 0.5

        half1 = FruitHalf(
            self.x - perp_x, self.y - perp_y,
            self.vx + perp_x * 0.1, self.vy + perp_y * 0.1,
            self.color, -1
        )
        half2 = FruitHalf(
            self.x + perp_x, self.y + perp_y,
            self.vx - perp_x * 0.1, self.vy - perp_y * 0.1,
            self.color, 1
        )
        return half1, half2


class FruitHalf(GameObject):
    """A half of a sliced fruit."""

    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], direction: int):
        super().__init__(x, y, vx, vy, FRUIT_RADIUS * 0.7, color)
        self.direction = direction  # -1 or 1
        self.rotation = 0

    def update(self) -> bool:
        self.rotation += self.direction * 5
        return super().update()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the half fruit."""
        # Draw a semicircle
        rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2)
        )

        start_angle = self.rotation
        end_angle = self.rotation + 180

        pygame.draw.arc(surface, self.color, rect, math.radians(start_angle), math.radians(end_angle), int(self.radius))
        # Draw outline
        pygame.draw.arc(surface, (255, 255, 255), rect, math.radians(start_angle), math.radians(end_angle), 2)


class Bomb(GameObject):
    """A dangerous bomb."""

    def __init__(self, x: float, y: float, vx: float, vy: float):
        super().__init__(x, y, vx, vy, BOMB_RADIUS, BOMB_COLOR)
        self.pulse = 0

    def update(self) -> bool:
        self.pulse = (self.pulse + 0.1) % (math.pi * 2)
        return super().update()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bomb with spikes."""
        # Main circle with pulsing effect
        pulse_radius = self.radius + math.sin(self.pulse) * 3
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(pulse_radius))

        # Draw spikes
        num_spikes = 8
        for i in range(num_spikes):
            angle = (i / num_spikes) * 2 * math.pi
            spike_x = self.x + math.cos(angle) * (self.radius + 10)
            spike_y = self.y + math.sin(angle) * (self.radius + 10)

            # Draw spike
            inner_x = self.x + math.cos(angle) * self.radius * 0.7
            inner_y = self.y + math.sin(angle) * self.radius * 0.7

            pygame.draw.line(surface, BOMB_SPIKE_COLOR, (inner_x, inner_y), (spike_x, spike_y), 3)

        # Draw warning symbol
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), 8)
        pygame.draw.circle(surface, BOMB_SPIKE_COLOR, (int(self.x), int(self.y)), 6)


class Particle:
    """A particle for visual effects."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 1.0
        self.radius = random.uniform(2, 5)

    def update(self) -> bool:
        """Update particle. Returns False when dead."""
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.5
        self.life -= 0.02
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the particle."""
        alpha = int(self.life * 255)
        if alpha > 0:
            color = (*self.color, alpha)
            # Create a surface for alpha blending
            s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frenzy: Fruit Ninja Lite")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

        self.reset()

    def reset(self) -> None:
        """Reset the game state."""
        self.objects: List[GameObject] = []
        self.halves: List[FruitHalf] = []
        self.particles: List[Particle] = []
        self.trail: List[TrailPoint] = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.spawn_timer = 0
        self.difficulty = 1.0
        self.last_mouse_pos = None
        self.mouse_speed = 0

    def spawn_object(self) -> None:
        """Spawn a new fruit or bomb."""
        # Spawn position from bottom
        x = random.uniform(100, SCREEN_WIDTH - 100)
        y = SCREEN_HEIGHT + 50

        # Velocity towards top with some randomness
        vx = random.uniform(-3, 3)
        vy = random.uniform(-12, -8)

        # 20% chance of bomb, increases with difficulty
        bomb_chance = 0.2 + (self.difficulty - 1.0) * 0.1
        if random.random() < bomb_chance:
            obj = Bomb(x, y, vx, vy)
        else:
            obj = Fruit(x, y, vx, vy)

        self.objects.append(obj)

    def create_slice_particles(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """Create particles when slicing."""
        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def check_collisions(self, mouse_pos: Tuple[int, int], mouse_speed: float) -> bool:
        """Check collisions with mouse slice. Returns True if bomb hit."""
        mx, my = mouse_pos

        for obj in self.objects[:]:
            if obj.contains_point(mx, my) and not obj.sliced:
                if isinstance(obj, Bomb):
                    obj.sliced = True
                    self.create_slice_particles(obj.x, obj.y, BOMB_COLOR)
                    return True  # Bomb hit!
                elif isinstance(obj, Fruit):
                    half1, half2 = obj.slice()
                    self.halves.extend([half1, half2])
                    self.score += FRUIT_SCORE
                    self.create_slice_particles(obj.x, obj.y, obj.color)

        return False

    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            return

        # Update difficulty
        self.difficulty = 1.0 + self.score * 0.005

        # Spawn objects
        self.spawn_timer += 1
        spawn_rate = max(20, 60 - int(self.score * 0.1))
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            self.spawn_object()

        # Update objects
        for obj in self.objects[:]:
            if not obj.update():
                self.objects.remove(obj)
                if isinstance(obj, Fruit) and not obj.sliced:
                    # Missed a fruit
                    self.score += MISS_PENALTY
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True

        # Update halves
        for half in self.halves[:]:
            if not half.update():
                self.halves.remove(half)

        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

        # Update trail
        for point in self.trail[:]:
            if not point.update():
                self.trail.remove(point)

        # Add current mouse position to trail if moving fast enough
        if self.mouse_speed > SLICE_THRESHOLD * 100:
            mx, my = pygame.mouse.get_pos()
            self.trail.append(TrailPoint(mx, my))

    def draw(self) -> None:
        """Draw everything."""
        self.screen.fill(BACKGROUND)

        # Draw trail
        for i, point in enumerate(self.trail):
            alpha = int(point.life * 150)
            if alpha > 0:
                s = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(s, (*SLICE_TRAIL_COLOR, alpha), (5, 5), 3)
                self.screen.blit(s, (int(point.x) - 5, int(point.y) - 5))

        # Draw objects
        for obj in self.objects:
            obj.draw(self.screen)

        # Draw halves
        for half in self.halves:
            half.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (20, 70))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, TEXT_COLOR)

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True

        while running:
            # Calculate mouse speed
            mouse_pos = pygame.mouse.get_pos()
            if self.last_mouse_pos:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                self.mouse_speed = math.sqrt(dx * dx + dy * dy)
            self.last_mouse_pos = mouse_pos

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset()

            # Check collisions if mouse is moving fast enough
            if not self.game_over and self.mouse_speed > SLICE_THRESHOLD * 100:
                bomb_hit = self.check_collisions(mouse_pos, self.mouse_speed)
                if bomb_hit:
                    self.game_over = True

            # Update and draw
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main() -> None:
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
