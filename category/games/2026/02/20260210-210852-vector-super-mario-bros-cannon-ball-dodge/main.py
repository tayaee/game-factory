"""
Vector Super Mario Bros Cannon Ball Dodge
A high-speed projectile dodging game with moving platforms.
"""
import pygame
import sys
import random
from typing import List, Tuple
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors - Monochrome high-contrast palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)

# Game settings
GRAVITY = 0.5
JUMP_VELOCITY = -10
MOVE_SPEED = 5
CANNONBALL_BASE_SPEED = 6
CANNONBALL_SPEED_INCREMENT = 0.5
BASE_SHOT_INTERVAL = 180  # frames (3 seconds at 60 FPS)
SHOT_INTERVAL_DECREMENT = 10  # Reduce interval by this many frames per level
MIN_SHOT_INTERVAL = 60  # Minimum 1 second between shots

PLATFORM_HEIGHT = 20
PLATFORM_Y_POSITIONS = [500, 350, 200]  # Bottom, middle, top

# Scoring
POINTS_PER_PROJECTILE = 10


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    NONE = 0


class Platform:
    """A horizontal platform that can move."""

    def __init__(self, x: int, y: int, width: int, moving: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.moving = moving
        self.move_speed = 1.5 if moving else 0
        self.move_direction = Direction.RIGHT
        self.start_x = x

    def update(self):
        """Update platform position if moving."""
        if not self.moving:
            return

        self.x += self.move_speed * self.move_direction.value

        # Bounce off edges with margin
        if self.x <= 50 or self.x + self.width >= SCREEN_WIDTH - 50:
            self.move_direction = Direction.LEFT if self.move_direction == Direction.RIGHT else Direction.RIGHT

    def get_rect(self) -> pygame.Rect:
        """Get platform collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface):
        """Draw the platform."""
        rect = self.get_rect()
        pygame.draw.rect(surface, DARK_GRAY, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)


class Player:
    """The player character (Mario)."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.jump_pressed = False

    def update(self, platforms: List[Platform]):
        """Update player physics."""
        # Apply gravity
        self.velocity_y += GRAVITY

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Keep on screen
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

        # Check platform collisions
        self.on_ground = False
        player_rect = self.get_rect()

        for platform in platforms:
            if player_rect.colliderect(platform.get_rect()):
                # Only collide if falling onto the platform
                if self.velocity_y > 0 and self.y + self.height - self.velocity_y <= platform.y:
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True

        # Move with platform if standing on one
        if self.on_ground:
            for platform in platforms:
                if player_rect.colliderect(platform.get_rect()) and platform.moving:
                    self.x += platform.move_speed * platform.move_direction.value

    def jump(self):
        """Jump if on ground."""
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            return True
        return False

    def move(self, direction: Direction):
        """Move horizontally."""
        self.velocity_x = MOVE_SPEED * direction.value

    def stop(self):
        """Stop horizontal movement."""
        self.velocity_x = 0

    def get_rect(self) -> pygame.Rect:
        """Get player collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def is_off_screen(self) -> bool:
        """Check if player fell off screen."""
        return self.y > SCREEN_HEIGHT

    def draw(self, surface: pygame.Surface):
        """Draw the player (Mario sprite)."""
        rect = self.get_rect()

        # Simple vector Mario: body
        pygame.draw.rect(surface, RED, (rect.x + 5, rect.y + 15, 20, 25))

        # Head
        pygame.draw.circle(surface, RED, (rect.centerx, rect.y + 12), 12)
        pygame.draw.circle(surface, WHITE, (rect.centerx, rect.y + 12), 12, 2)

        # Hat
        pygame.draw.rect(surface, RED, (rect.x + 2, rect.y, 26, 8))

        # M emblem
        pygame.draw.line(surface, WHITE, (rect.centerx - 4, rect.y + 10), (rect.centerx, rect.y + 6), 2)
        pygame.draw.line(surface, WHITE, (rect.centerx, rect.y + 6), (rect.centerx + 4, rect.y + 10), 2)

        # Eyes
        pygame.draw.circle(surface, WHITE, (rect.centerx - 4, rect.y + 10), 3)
        pygame.draw.circle(surface, WHITE, (rect.centerx + 4, rect.y + 10), 3)
        pygame.draw.circle(surface, BLACK, (rect.centerx - 4, rect.y + 10), 1)
        pygame.draw.circle(surface, BLACK, (rect.centerx + 4, rect.y + 10), 1)


class Cannon:
    """A Bill Blaster cannon that fires projectiles."""

    def __init__(self, x: int, y: int, direction: Direction):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.direction = direction

    def get_position(self) -> Tuple[int, int]:
        """Get firing position."""
        if self.direction == Direction.RIGHT:
            return (self.x + self.width, self.y + self.height // 2)
        else:
            return (self.x, self.y + self.height // 2)

    def draw(self, surface: pygame.Surface):
        """Draw the cannon (Bill Blaster)."""
        # Cannon body
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, DARK_GRAY, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)

        # Cannon opening
        if self.direction == Direction.RIGHT:
            opening = pygame.Rect(self.x + self.width - 5, self.y + 5, 8, self.height - 10)
        else:
            opening = pygame.Rect(self.x - 3, self.y + 5, 8, self.height - 10)

        pygame.draw.rect(surface, BLACK, opening)
        pygame.draw.rect(surface, WHITE, opening, 1)


class Cannonball:
    """A Bullet Bill projectile fired from cannons."""

    def __init__(self, x: int, y: int, direction: Direction, speed: float):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 18
        self.direction = direction
        self.speed = speed
        self.active = True
        self.scored = False  # Track if points awarded for this projectile

    def update(self):
        """Update projectile position."""
        self.x += self.speed * self.direction.value

        # Check if off screen
        if (self.direction == Direction.RIGHT and self.x > SCREEN_WIDTH + 50) or \
           (self.direction == Direction.LEFT and self.x < -50):
            self.active = False

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface):
        """Draw the cannonball (Bullet Bill)."""
        rect = self.get_rect()

        # Main body
        pygame.draw.ellipse(surface, BLACK, rect)
        pygame.draw.ellipse(surface, WHITE, rect, 2)

        # Eyes
        eye_y = rect.centery
        if self.direction == Direction.RIGHT:
            eye_x = rect.x + 20
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y - 3), 4)
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y + 3), 4)
            pygame.draw.circle(surface, BLACK, (eye_x + 1, eye_y - 3), 2)
            pygame.draw.circle(surface, BLACK, (eye_x + 1, eye_y + 3), 2)

            # Angry eyebrow
            pygame.draw.line(surface, WHITE, (eye_x - 4, eye_y - 8), (eye_x + 2, eye_y - 5), 2)
            pygame.draw.line(surface, WHITE, (eye_x - 4, eye_y + 8), (eye_x + 2, eye_y + 5), 2)
        else:
            eye_x = rect.x + 10
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y - 3), 4)
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y + 3), 4)
            pygame.draw.circle(surface, BLACK, (eye_x - 1, eye_y - 3), 2)
            pygame.draw.circle(surface, BLACK, (eye_x - 1, eye_y + 3), 2)

            # Angry eyebrow
            pygame.draw.line(surface, WHITE, (eye_x + 4, eye_y - 8), (eye_x - 2, eye_y - 5), 2)
            pygame.draw.line(surface, WHITE, (eye_x + 4, eye_y + 8), (eye_x - 2, eye_y + 5), 2)


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Cannon Ball Dodge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 64)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        # Create platforms
        self.platforms = [
            Platform(100, PLATFORM_Y_POSITIONS[0], 600, moving=False),  # Bottom - stationary
            Platform(50, PLATFORM_Y_POSITIONS[1], 500, moving=True),    # Middle - moving
            Platform(150, PLATFORM_Y_POSITIONS[2], 500, moving=True),   # Top - moving
        ]

        # Create player on middle platform
        self.player = Player(SCREEN_WIDTH // 2 - 15, PLATFORM_Y_POSITIONS[1] - 40)

        # Create cannons on left and right edges at varying heights
        self.cannons = [
            Cannon(0, PLATFORM_Y_POSITIONS[0] - 40, Direction.RIGHT),  # Left, low
            Cannon(0, PLATFORM_Y_POSITIONS[2] - 50, Direction.RIGHT),  # Left, high
            Cannon(SCREEN_WIDTH - 40, PLATFORM_Y_POSITIONS[1] - 45, Direction.LEFT),  # Right, middle
        ]

        self.cannonballs: List[Cannonball] = []
        self.score = 0
        self.level = 1
        self.shot_timer = 0
        self.shot_interval = BASE_SHOT_INTERVAL
        self.cannonball_speed = CANNONBALL_BASE_SPEED
        self.game_over = False
        self.high_score = 0

    def get_current_cannon_count(self) -> int:
        """Get number of active cannons based on level."""
        return min(2 + self.level, len(self.cannons))

    def fire_cannonball(self, cannon: Cannon):
        """Fire a projectile from the given cannon."""
        x, y = cannon.get_position()
        speed = self.cannonball_speed
        self.cannonballs.append(Cannonball(x, y, cannon.direction, speed))

    def get_cannon_to_fire(self) -> Cannon:
        """Get which cannon should fire next."""
        active_count = self.get_current_cannon_count()
        # Pick random cannon from active ones
        return random.choice(self.cannons[:active_count])

    def handle_input(self) -> bool:
        """Handle player input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_over:
                    if self.score > self.high_score:
                        self.high_score = self.score
                    self.reset_game()
                elif not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_LEFT:
                        self.player.move(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(Direction.RIGHT)
            elif event.type == pygame.KEYUP:
                if not self.game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.player.stop()
        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Update platforms
        for platform in self.platforms:
            platform.update()

        # Update player
        self.player.update(self.platforms)

        # Check if player fell off
        if self.player.is_off_screen():
            self.game_over = True
            return

        # Fire cannonballs
        self.shot_timer += 1
        if self.shot_timer >= self.shot_interval:
            self.shot_timer = 0
            cannon = self.get_cannon_to_fire()
            self.fire_cannonball(cannon)

        # Update cannonballs
        for ball in self.cannonballs[:]:
            ball.update()

            # Check collision with player
            if ball.get_rect().colliderect(self.player.get_rect()):
                self.game_over = True
                return

            # Award points when projectile leaves screen
            if not ball.active and not ball.scored:
                ball.scored = True
                self.score += POINTS_PER_PROJECTILE

                # Level up every 5 projectiles dodged (50 points)
                if self.score % 50 == 0:
                    self.level += 1
                    self.cannonball_speed += CANNONBALL_SPEED_INCREMENT
                    self.shot_interval = max(MIN_SHOT_INTERVAL,
                                             self.shot_interval - SHOT_INTERVAL_DECREMENT)

        # Remove inactive cannonballs
        self.cannonballs = [b for b in self.cannonballs if b.active]

    def draw_background(self):
        """Draw the background."""
        self.screen.fill(BLACK)

        # Draw subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))

    def draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.font.render(f"Level: {self.level}", True, YELLOW)
        self.screen.blit(level_text, (SCREEN_WIDTH - 120, 10))

        # High Score
        high_score_text = self.font.render(f"High Score: {max(self.score, self.high_score)}", True, GREEN)
        self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 80, 10))

        # Controls hint at bottom
        hint_text = self.font.render("ARROWS: Move | SPACE: Jump | R: Restart", True, GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(hint_text, hint_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render("GAME OVER", True, RED)
        subtext = self.font.render(f"Final Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level Reached: {self.level}", True, YELLOW)
        restart_text = self.font.render("Press R to restart", True, GRAY)

        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        subrect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))

        self.screen.blit(text, text_rect)
        self.screen.blit(subtext, subrect)
        self.screen.blit(level_text, level_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Draw everything."""
        self.draw_background()

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw cannons
        for cannon in self.cannons[:self.get_current_cannon_count()]:
            cannon.draw(self.screen)

        # Draw cannonballs
        for ball in self.cannonballs:
            ball.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        self.draw_ui()

        if self.game_over:
            self.draw_game_over()

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
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
