import pygame
import random
from config import *


class Platform:
    def __init__(self, x, y, width, has_spike=False, moving=False, move_range=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.rect = pygame.Rect(x, y, width, self.height)
        self.has_spike = has_spike
        self.moving = moving
        self.move_start = x
        self.move_range = move_range
        self.move_speed = 2
        self.move_direction = 1

        # Generate coins for this platform
        self.coins = []
        if not has_spike:
            self._generate_coins()

    def _generate_coins(self):
        num_coins = random.randint(1, COINS_PER_PLATFORM)
        for i in range(num_coins):
            coin_x = self.x + 20 + (i * (self.width - 40) // max(1, num_coins - 1)) if num_coins > 1 else self.x + self.width // 2
            self.coins.append(pygame.Rect(coin_x - COIN_SIZE // 2, self.y - COIN_SIZE - 8, COIN_SIZE, COIN_SIZE))

    def update(self):
        if self.moving:
            self.x += self.move_speed * self.move_direction
            if self.x > self.move_start + self.move_range or self.x < self.move_start:
                self.move_direction *= -1
            self.rect.x = int(self.x)

    def draw(self, screen, camera_x):
        draw_x = self.x - camera_x

        # Draw platform
        platform_rect = pygame.Rect(draw_x, self.y, self.width, self.height)
        pygame.draw.rect(screen, PLATFORM_COLOR, platform_rect, border_radius=3)
        pygame.draw.rect(screen, PLATFORM_BORDER_COLOR, platform_rect, 2, border_radius=3)

        # Draw spike if present
        if self.has_spike:
            spike_count = self.width // 20
            for i in range(spike_count):
                spike_x = draw_x + i * 20 + 10
                spike_points = [
                    (spike_x, self.y),
                    (spike_x - 8, self.y + self.height),
                    (spike_x + 8, self.y + self.height)
                ]
                pygame.draw.polygon(screen, SPIKE_COLOR, spike_points)
                pygame.draw.polygon(screen, (100, 100, 100), spike_points, 1)

        # Draw coins
        for coin in self.coins:
            coin_draw_x = coin.x - camera_x
            pygame.draw.circle(screen, COIN_COLOR, (coin_draw_x + COIN_SIZE // 2, coin.y + COIN_SIZE // 2), COIN_SIZE // 2)
            pygame.draw.circle(screen, (200, 150, 0), (coin_draw_x + COIN_SIZE // 2, coin.y + COIN_SIZE // 2), COIN_SIZE // 2 - 2)

    def collect_coins(self, player_rect):
        collected = 0
        remaining_coins = []
        for coin in self.coins:
            if player_rect.colliderect(coin):
                collected += 1
            else:
                remaining_coins.append(coin)
        self.coins = remaining_coins
        return collected


class Level:
    def __init__(self):
        self.platforms = []
        self.checkpoints = []
        self.goal_x = 0
        self._generate_level()

    def _generate_level(self):
        # Starting platform
        start_platform = Platform(50, SCREEN_HEIGHT - 150, 200)
        self.platforms.append(start_platform)

        current_x = 250
        current_y = SCREEN_HEIGHT - 150
        last_checkpoint_x = 50

        # Generate main level
        for i in range(50):
            # Calculate gap and width
            gap = random.randint(PLATFORM_GAP_MIN, PLATFORM_GAP_MAX)
            width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)

            # Calculate new Y position
            y_change = random.randint(-PLATFORM_Y_VARIANCE, PLATFORM_Y_VARIANCE)
            new_y = max(150, min(SCREEN_HEIGHT - 100, current_y + y_change))

            # Add features
            has_spike = random.random() < 0.15 and i > 3
            moving = random.random() < 0.2 and i > 3
            move_range = random.randint(50, 100) if moving else 0

            platform = Platform(current_x + gap, new_y, width, has_spike, moving, move_range)
            self.platforms.append(platform)

            current_x += gap + width
            current_y = new_y

            # Add checkpoint every interval
            if current_x - last_checkpoint_x >= CHECKPOINT_INTERVAL:
                self.checkpoints.append((current_x, new_y))
                last_checkpoint_x = current_x

        # Final goal platform
        self.goal_x = current_x + 100
        goal_platform = Platform(current_x + 50, SCREEN_HEIGHT - 200, 300)
        self.platforms.append(goal_platform)

    def update(self):
        for platform in self.platforms:
            platform.update()

    def draw(self, screen, camera_x):
        for platform in self.platforms:
            platform.draw(screen, camera_x)

        # Draw goal flag
        if self.goal_x - camera_x < SCREEN_WIDTH:
            goal_draw_x = self.goal_x - camera_x
            pygame.draw.rect(screen, GOAL_COLOR, (goal_draw_x, SCREEN_HEIGHT - 350, 5, 150))
            pygame.draw.polygon(screen, GOAL_COLOR, [
                (goal_draw_x + 5, SCREEN_HEIGHT - 350),
                (goal_draw_x + 60, SCREEN_HEIGHT - 325),
                (goal_draw_x + 5, SCREEN_HEIGHT - 300)
            ])
