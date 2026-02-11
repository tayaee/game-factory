"""
Vector Super Mario Bros Springboard Physics
A physics-based platformer focusing on springboard jump mechanics.
"""

import pygame
import sys
import math
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics constants
GRAVITY = 0.8
NORMAL_JUMP_VELOCITY = -12
SPRING_BOOST_MULTIPLIER = 2.5
PASSIVE_BOUNCE_MULTIPLIER = 1.2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 180, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
BROWN = (139, 90, 43)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (135, 206, 235)
DARK_GREEN = (34, 100, 34)


class Player:
    """Player character with physics-based movement."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.on_spring = False
        self.spring_contact_time = 0

    def update(self, keys: pygame.key.ScancodeWrapper, platforms: List['Platform']):
        """Update player physics and movement."""
        # Horizontal movement
        speed = 5.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = speed
            self.facing_right = True
        else:
            self.vx *= 0.8  # Friction
            if abs(self.vx) < 0.1:
                self.vx = 0

        # Apply gravity
        self.vy += GRAVITY

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Screen boundaries
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.collides_with_platform(platform):
                # Landing on top of platform
                if self.vy > 0:
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True

        # Check if fell below screen
        if self.y > SCREEN_HEIGHT + 100:
            return False  # Game over

        return True

    def collides_with_platform(self, platform: 'Platform') -> bool:
        """Check AABB collision with a platform."""
        player_bottom = self.y + self.height
        player_right = self.x + self.width
        platform_bottom = platform.y + platform.height
        platform_right = platform.x + platform.width

        return (self.x < platform_right and
                player_right > platform.x and
                self.y < platform_bottom and
                player_bottom > platform.y and
                self.vy > 0 and
                player_bottom - self.vy <= platform.y + 5)

    def jump(self):
        """Perform a normal jump."""
        if self.on_ground:
            self.vy = NORMAL_JUMP_VELOCITY
            self.on_ground = False

    def spring_jump(self, boost: bool):
        """Perform a spring jump with variable boost."""
        if boost:
            self.vy = NORMAL_JUMP_VELOCITY * SPRING_BOOST_MULTIPLIER
        else:
            self.vy = NORMAL_JUMP_VELOCITY * PASSIVE_BOUNCE_MULTIPLIER

    def get_rect(self) -> pygame.Rect:
        """Get player bounding box."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen: pygame.Surface):
        """Draw the player character."""
        # Body
        body_rect = pygame.Rect(self.x + 4, self.y + 16, self.width - 8, self.height - 16)
        pygame.draw.rect(screen, RED, body_rect)

        # Head
        head_rect = pygame.Rect(self.x + 4, self.y, self.width - 8, 20)
        pygame.draw.rect(screen, (255, 200, 150), head_rect)

        # Hat
        hat_rect = pygame.Rect(self.x, self.y - 4, self.width, 8)
        pygame.draw.rect(screen, RED, hat_rect)

        # Eyes
        eye_x = self.x + 20 if self.facing_right else self.x + 8
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(self.y + 8)), 3)

        # Legs
        leg_y = self.y + self.height - 8
        pygame.draw.rect(screen, BLUE, (self.x + 6, leg_y, 8, 8))
        pygame.draw.rect(screen, BLUE, (self.x + 18, leg_y, 8, 8))


class Springboard:
    """Springboard that provides variable jump boost based on timing."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 16
        self.compressed = False
        self.compression_timer = 0
        self.compression_duration = 15  # frames

    def update(self):
        """Update springboard animation state."""
        if self.compressed:
            self.compression_timer += 1
            if self.compression_timer >= self.compression_duration:
                self.compressed = False
                self.compression_timer = 0

    def compress(self):
        """Compress the springboard."""
        self.compressed = True
        self.compression_timer = 0

    def is_timed_jump(self) -> bool:
        """Check if current timing qualifies for boosted jump."""
        return self.compressed and self.compression_timer < 8

    def get_rect(self) -> pygame.Rect:
        """Get springboard bounding box."""
        height = 8 if self.compressed else self.height
        return pygame.Rect(self.x, self.y + (self.height - height), self.width, height)

    def draw(self, screen: pygame.Surface):
        """Draw the springboard."""
        height = 8 if self.compressed else self.height
        y_offset = self.height - height

        # Base
        pygame.draw.rect(screen, DARK_GRAY,
                        (self.x, self.y + self.height - 4, self.width, 4))

        # Spring coil
        coil_color = ORANGE
        for i in range(3):
            coil_y = self.y + y_offset + 4 + i * (height // 4)
            pygame.draw.rect(screen, coil_color,
                           (self.x + 4, coil_y, self.width - 8, 4))

        # Top pad
        pygame.draw.rect(screen, RED,
                        (self.x, self.y + y_offset, self.width, 6))


class Platform:
    """Static platform for the player to stand on."""

    def __init__(self, x: float, y: float, width: float, height: float = 20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_rect(self) -> pygame.Rect:
        """Get platform bounding box."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen: pygame.Surface):
        """Draw the platform."""
        # Top surface (grass)
        pygame.draw.rect(screen, GREEN,
                        (self.x, self.y, self.width, 6))

        # Body (dirt)
        pygame.draw.rect(screen, BROWN,
                        (self.x, self.y + 6, self.width, self.height - 6))

        # Texture lines
        for i in range(int(self.width // 20)):
            line_x = self.x + 10 + i * 20
            if line_x < self.x + self.width - 10:
                pygame.draw.line(screen, DARK_GRAY,
                               (line_x, self.y + 8),
                               (line_x, self.y + self.height - 2), 1)


class Coin:
    """Collectible coin."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.animation_frame = 0
        self.animation_speed = 0.15

    def update(self):
        """Update coin animation."""
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def check_collection(self, player: Player) -> bool:
        """Check if player collected this coin."""
        if self.collected:
            return False

        coin_center_x = self.x
        coin_center_y = self.y
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        distance = math.sqrt((coin_center_x - player_center_x) ** 2 +
                            (coin_center_y - player_center_y) ** 2)

        if distance < self.radius + 20:
            self.collected = True
            return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the coin with animation."""
        if self.collected:
            return

        # Pulsing animation
        scale = 0.9 + 0.1 * math.sin(self.animation_frame * math.pi / 2)
        radius = int(self.radius * scale)

        # Outer ring
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), radius)
        # Inner circle
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), radius - 3)
        # Shine
        pygame.draw.circle(screen, WHITE, (int(self.x - 3), int(self.y - 3)), 3)


class Game:
    """Main game class managing all game logic."""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros - Springboard Physics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset game state for a new game."""
        # Create player
        self.player = Player(100, SCREEN_HEIGHT - 150)

        # Create platforms
        self.platforms: List[Platform] = [
            # Ground
            Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 60),
            # Low platforms
            Platform(50, SCREEN_HEIGHT - 150, 120),
            Platform(630, SCREEN_HEIGHT - 150, 120),
            # Medium platforms
            Platform(200, SCREEN_HEIGHT - 260, 150),
            Platform(500, SCREEN_HEIGHT - 260, 150),
            # High platforms
            Platform(100, SCREEN_HEIGHT - 370, 120),
            Platform(350, SCREEN_HEIGHT - 370, 100),
            Platform(580, SCREEN_HEIGHT - 370, 120),
            # Highest platforms
            Platform(250, SCREEN_HEIGHT - 480, 100),
            Platform(450, SCREEN_HEIGHT - 480, 100),
            # Top platform (bonus)
            Platform(330, SCREEN_HEIGHT - 560, 140),
        ]

        # Create springboards
        self.springboards: List[Springboard] = [
            Springboard(180, SCREEN_HEIGHT - 56),
            Springboard(340, SCREEN_HEIGHT - 56),
            Springboard(540, SCREEN_HEIGHT - 56),
            Springboard(200, SCREEN_HEIGHT - 276),
            Springboard(510, SCREEN_HEIGHT - 276),
            Springboard(380, SCREEN_HEIGHT - 396),
        ]

        # Create coins
        self.coins: List[Coin] = [
            # Ground level coins
            Coin(250, SCREEN_HEIGHT - 80),
            Coin(400, SCREEN_HEIGHT - 80),
            Coin(550, SCREEN_HEIGHT - 80),
            # Low platform coins
            Coin(100, SCREEN_HEIGHT - 190),
            Coin(700, SCREEN_HEIGHT - 190),
            # Medium platform coins
            Coin(270, SCREEN_HEIGHT - 300),
            Coin(570, SCREEN_HEIGHT - 300),
            # High platform coins
            Coin(160, SCREEN_HEIGHT - 410),
            Coin(640, SCREEN_HEIGHT - 410),
            # Top bonus coin
            Coin(400, SCREEN_HEIGHT - 600),
        ]

        self.total_coins = len(self.coins)
        self.collected_coins = 0
        self.game_won = False
        self.game_over = False
        self.reached_top_bonus = False
        self.space_pressed = False
        self.previous_space = False

    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.reset_game()

        # Track space key for edge detection
        keys = pygame.key.get_pressed()
        self.space_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        return True

    def update(self):
        """Update game state."""
        if self.game_won or self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Check springboard collision before player update
        spring_collided = None
        for springboard in self.springboards:
            springboard.update()
            if self.player.vy > 0:
                spring_rect = springboard.get_rect()
                player_rect = pygame.Rect(self.player.x, self.player.y,
                                         self.player.width, self.player.height)

                if player_rect.colliderect(spring_rect):
                    # Landing on spring
                    spring_collided = springboard
                    springboard.compress()
                    self.player.y = spring_rect.top - self.player.height

        # Handle spring jump
        if spring_collided:
            # Check for timed jump (space pressed during compression window)
            if self.space_pressed and not self.previous_space:
                # Fresh press during compression - boosted jump
                spring_collided.compress()
                self.player.spring_jump(boost=spring_collided.is_timed_jump())
            elif spring_collided.compressed:
                # Already compressed - passive bounce
                self.player.spring_jump(boost=spring_collided.is_timed_jump())
            else:
                # Default passive bounce
                self.player.spring_jump(boost=False)
        elif self.space_pressed and not self.previous_space:
            # Normal jump
            self.player.jump()

        self.previous_space = self.space_pressed

        # Update player
        if not self.player.update(keys, self.platforms):
            self.game_over = True

        # Check coin collection
        for coin in self.coins:
            coin.update()
            if coin.check_collection(self.player):
                self.player.score += 100
                self.collected_coins += 1

        # Check for top platform bonus
        top_platform = self.platforms[-1]  # Last platform is top
        if (not self.reached_top_bonus and
            self.player.x + self.player.width > top_platform.x and
            self.player.x < top_platform.x + top_platform.width and
            abs(self.player.y + self.player.height - top_platform.y) < 10):
            self.reached_top_bonus = True
            self.player.score += 500

        # Check win condition
        if self.collected_coins >= self.total_coins:
            self.game_won = True

    def draw(self):
        """Draw all game elements."""
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(135 * (1 - ratio) + 50 * ratio)
            g = int(206 * (1 - ratio) + 50 * ratio)
            b = int(235 * (1 - ratio) + 100 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw springboards
        for springboard in self.springboards:
            springboard.draw(self.screen)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        self.draw_ui()

        # Draw game over or win screen
        if self.game_won:
            self.draw_win_screen()
        elif self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_ui(self):
        """Draw user interface elements."""
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Coins
        coins_text = self.font.render(
            f"Coins: {self.collected_coins}/{self.total_coins}", True, YELLOW)
        self.screen.blit(coins_text, (10, 45))

        # Instructions
        instructions = [
            "Arrow Keys: Move | Space: Jump",
            "Land on spring + Space = Super Jump!",
            "Press R to restart | ESC to quit"
        ]
        for i, text in enumerate(instructions):
            inst_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(inst_text, (SCREEN_WIDTH - inst_text.get_width() - 10, 10 + i * 20))

        # Bonus indicator
        if self.reached_top_bonus:
            bonus_text = self.small_font.render("TOP BONUS: +500!", True, YELLOW)
            self.screen.blit(bonus_text, (SCREEN_WIDTH // 2 - 60, 10))

    def draw_win_screen(self):
        """Draw win screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        win_text = self.font.render("CONGRATULATIONS!", True, YELLOW)
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        restart_text = self.small_font.render("Press R to play again", True, WHITE)

        self.screen.blit(win_text,
                        (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(score_text,
                        (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def draw_game_over_screen(self):
        """Draw game over screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        coins_text = self.small_font.render(
            f"Coins: {self.collected_coins}/{self.total_coins}", True, YELLOW)
        restart_text = self.small_font.render("Press R to try again", True, WHITE)

        self.screen.blit(game_over_text,
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(score_text,
                        (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(coins_text,
                        (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
