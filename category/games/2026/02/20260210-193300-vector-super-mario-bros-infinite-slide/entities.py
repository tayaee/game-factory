"""Game entities for the infinite slide game."""

import random
from typing import List, Optional, Tuple
from config import *


class Player:
    """The player character with icy momentum physics."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = False
        self.alive = True
        self.distance_traveled = 0.0
        self.coins_collected = 0

    def update(self, keys: Tuple[bool, bool, bool], platforms: List, spikes: List) -> None:
        """Update player physics and input."""
        if not self.alive:
            return

        # Horizontal input with low acceleration (icy feel)
        if keys[0]:  # Left
            self.vx -= ACCELERATION
        if keys[1]:  # Right
            self.vx += ACCELERATION

        # Apply very low friction (icy surface)
        self.vx *= (1 - FRICTION)

        # Clamp velocity
        self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))

        # Apply gravity
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPEED)

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Track distance
        if self.x > self.distance_traveled:
            self.distance_traveled = self.x

        # Check death (fell off screen)
        if self.y > SCREEN_HEIGHT + 50 or self.x < -50:
            self.alive = False

        # Check collisions
        self._check_platform_collisions(platforms)
        self._check_spike_collisions(spikes)

    def jump(self) -> None:
        """Jump if on ground."""
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False

    def _check_platform_collisions(self, platforms: List) -> None:
        """Check and resolve platform collisions."""
        self.on_ground = False

        for platform in platforms:
            if self._collides_with(platform):
                # Landing on top
                if self.vy > 0 and self.y + self.height - self.vy <= platform.y + 8:
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True

    def _check_spike_collisions(self, spikes: List) -> None:
        """Check if player hit a spike."""
        player_rect = self._get_rect()
        for spike in spikes:
            if spike.check_collision(player_rect):
                self.alive = False

    def _collides_with(self, platform) -> bool:
        """Check if colliding with platform."""
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)

    def _get_rect(self) -> Tuple[float, float, float, float]:
        """Get collision rect."""
        return (self.x, self.y, self.width, self.height)

    def draw(self, surface) -> None:
        """Draw the player."""
        import pygame
        screen_x = int(self.x)
        screen_y = int(self.y)

        # Body with rounded corners
        pygame.draw.rect(surface, COLOR_PLAYER, (screen_x, screen_y, self.width, self.height), border_radius=4)

        # Eye (indicates facing direction)
        eye_x = screen_x + (20 if self.vx >= 0 else 4)
        pygame.draw.circle(surface, COLOR_PLAYER_EYE, (eye_x, screen_y + 12), 5)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, screen_y + 12), 2)

        # Subtle highlight for icy feel
        highlight_x = screen_x + 5 if self.vx >= 0 else screen_x + self.width - 10
        pygame.draw.line(surface, (255, 150, 150), (highlight_x, screen_y + 5), (highlight_x, screen_y + 15), 2)


class Platform:
    """An icy platform."""

    def __init__(self, x: int, y: int, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT

    def draw(self, surface) -> None:
        """Draw the icy platform."""
        import pygame
        screen_x = int(self.x)
        screen_y = int(self.y)

        # Main platform body (icy blue)
        pygame.draw.rect(surface, COLOR_PLATFORM, (screen_x, screen_y, self.width, self.height), border_radius=3)

        # Shiny top edge (ice reflection)
        pygame.draw.rect(surface, COLOR_PLATFORM_TOP, (screen_x, screen_y, self.width, 4))

        # Ice sparkle marks
        for i in range(0, self.width, 30):
            sparkle_x = screen_x + i + random.randint(-5, 5)
            if sparkle_x < screen_x + self.width:
                pygame.draw.line(surface, (255, 255, 255), (sparkle_x, screen_y + 2), (sparkle_x + 8, screen_y + 6), 1)


class Spike:
    """A spike obstacle."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = SPIKE_WIDTH
        self.height = SPIKE_HEIGHT

    def check_collision(self, player_rect: Tuple[float, float, float, float]) -> bool:
        """Check if player rect intersects spike."""
        spike_rect = (self.x + 5, self.y, self.width - 10, self.height)
        return not (player_rect[0] + player_rect[2] < spike_rect[0] or
                    player_rect[0] > spike_rect[0] + spike_rect[2] or
                    player_rect[1] + player_rect[3] < spike_rect[1] or
                    player_rect[1] > spike_rect[1] + spike_rect[3])

    def draw(self, surface) -> None:
        """Draw the spike."""
        import pygame
        screen_x = int(self.x)
        screen_y = int(self.y)

        # Triangular spike
        points = [
            (screen_x, screen_y + self.height),
            (screen_x + self.width // 2, screen_y),
            (screen_x + self.width, screen_y + self.height)
        ]
        pygame.draw.polygon(surface, COLOR_SPIKE, points)
        pygame.draw.polygon(surface, (100, 100, 110), points, 1)


class Coin:
    """A collectible coin."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.base_y = y
        self.y = y
        self.size = COIN_SIZE
        self.collected = False
        self.bounce_phase = random.random() * 6.28

    def update(self) -> None:
        """Update coin animation."""
        self.bounce_phase += COIN_BOUNCE_SPEED
        self.y = self.base_y + (self.bounce_phase % 6.28) * COIN_BOUNCE_HEIGHT

    def check_collection(self, player: Player) -> bool:
        """Check if player collected the coin."""
        if self.collected:
            return False

        player_center = (player.x + player.width / 2, player.y + player.height / 2)
        coin_center = (self.x + self.size / 2, self.y + self.size / 2)
        distance = ((player_center[0] - coin_center[0])**2 + (player_center[1] - coin_center[1])**2)**0.5

        if distance < (player.width / 2 + self.size / 2):
            self.collected = True
            return True
        return False

    def draw(self, surface) -> None:
        """Draw the coin."""
        if self.collected:
            return

        import pygame
        screen_x = int(self.x)
        screen_y = int(self.y)

        # Coin body
        pygame.draw.circle(surface, COLOR_COIN, (screen_x + self.size // 2, screen_y + self.size // 2), self.size // 2)
        pygame.draw.circle(surface, COLOR_COIN_OUTLINE, (screen_x + self.size // 2, screen_y + self.size // 2), self.size // 2, 2)

        # Dollar sign
        font = pygame.font.Font(None, 16)
        text = font.render("$", True, COLOR_COIN_OUTLINE)
        surface.blit(text, (screen_x + self.size // 2 - text.get_width() // 2, screen_y + self.size // 2 - text.get_height() // 2))


class LevelGenerator:
    """Generates endless icy platforms."""

    def __init__(self):
        self.last_platform_x = 0
        self.current_y = SCREEN_HEIGHT - 100
        self.platforms = []
        self.spikes = []
        self.coins = []
        self._init_start_area()

    def _init_start_area(self) -> None:
        """Create the starting platform."""
        start_platform = Platform(0, self.current_y, 400)
        self.platforms.append(start_platform)
        self.last_platform_x = 400

        # Add some starting coins
        for i in range(5):
            self.coins.append(Coin(150 + i * 50, self.current_y - 30))

    def generate(self, player_x: float, scroll_x: float) -> None:
        """Generate new platforms as player progresses."""
        # Generate ahead of player
        target_x = player_x + GENERATION_BUFFER

        while self.last_platform_x < target_x:
            self._create_next_platform()

        # Clean up old objects
        self._cleanup_old(scroll_x)

    def _create_next_platform(self) -> None:
        """Create the next platform with gap."""
        # Calculate gap
        gap_width = random.randint(MIN_GAP_WIDTH, MAX_GAP_WIDTH)
        platform_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)

        # Calculate Y position (vary height)
        y_change = random.randint(-Y_VARIANCE, Y_VARIANCE)
        new_y = max(150, min(SCREEN_HEIGHT - 80, self.current_y + y_change))

        # Position after gap
        platform_x = self.last_platform_x + gap_width

        # Create platform
        platform = Platform(platform_x, new_y, platform_width)
        self.platforms.append(platform)

        # Maybe add spikes
        if random.random() < 0.3 and platform_width > SPIKE_WIDTH * 2:
            num_spikes = random.randint(SPIKE_COUNT_MIN, SPIKE_COUNT_MAX)
            spike_x = platform_x + random.randint(20, platform_width - num_spikes * SPIKE_WIDTH - 20)
            for i in range(num_spikes):
                self.spikes.append(Spike(spike_x + i * SPIKE_WIDTH, new_y - SPIKE_HEIGHT))

        # Add coins above platform
        if random.random() < 0.7:
            num_coins = random.randint(1, 4)
            coin_start_x = platform_x + random.randint(10, platform_width - num_coins * 20 - 10)
            for i in range(num_coins):
                self.coins.append(Coin(coin_start_x + i * 25, new_y - 40))

        # Update state
        self.last_platform_x = platform_x + platform_width
        self.current_y = new_y

    def _cleanup_old(self, scroll_x: float) -> None:
        """Remove objects that are off screen."""
        cleanup_threshold = scroll_x - 200

        self.platforms = [p for p in self.platforms if p.x + p.width > cleanup_threshold]
        self.spikes = [s for s in self.spikes if s.x > cleanup_threshold]
        self.coins = [c for c in self.coins if c.x > cleanup_threshold]

    def reset(self) -> None:
        """Reset the generator."""
        self.platforms = []
        self.spikes = []
        self.coins = []
        self.last_platform_x = 0
        self.current_y = SCREEN_HEIGHT - 100
        self._init_start_area()


class GameState:
    """Manages game state."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset game state."""
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.level_gen = LevelGenerator()
        self.scroll_x = 0.0
        self.scroll_speed = INITIAL_SCROLL_SPEED
        self.game_over = False
        self.waiting_start = True
        self.score = 0
        self.high_score = 0

    def update(self, keys: Tuple[bool, bool, bool]) -> None:
        """Update game state."""
        if self.waiting_start:
            if keys[2]:  # Jump to start
                self.waiting_start = False
            return

        if self.game_over:
            return

        # Update player
        self.player.update(keys, self.level_gen.platforms, self.level_gen.spikes)

        # Update coins
        for coin in self.level_gen.coins:
            coin.update()
            if coin.check_collection(self.player):
                self.player.coins_collected += 1

        # Generate new level content
        self.level_gen.generate(self.player.x, self.scroll_x)

        # Update scroll (increases over time)
        self.scroll_speed = min(MAX_SCROLL_SPEED, self.scroll_speed + SCROLL_ACCELERATION)
        self.scroll_x += self.scroll_speed

        # Check if player is pushed off screen
        if self.player.x < self.scroll_x - DANGER_ZONE_WIDTH:
            self.player.alive = False

        # Check game over
        if not self.player.alive:
            self.game_over = True
            self.score = int(self.player.distance_traveled) + self.player.coins_collected * POINTS_PER_COIN
            if self.score > self.high_score:
                self.high_score = self.score

    def handle_jump(self) -> None:
        """Handle jump input."""
        if self.waiting_start:
            self.waiting_start = False
        else:
            self.player.jump()
