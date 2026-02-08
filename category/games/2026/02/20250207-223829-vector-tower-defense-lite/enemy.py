import pygame
from config import ENEMY_SIZE, ENEMY_BASE_SPEED


class Enemy:
    def __init__(self, path, wave_multiplier=1.0):
        self.path = path
        self.distance = 0
        self.speed = ENEMY_BASE_SPEED * wave_multiplier
        self.max_health = 30 * wave_multiplier
        self.health = self.max_health
        self.value = int(10 * wave_multiplier)
        self.alive = True
        self.reached_end = False

    def update(self):
        if not self.alive:
            return

        self.distance += self.speed

        if self.distance >= self.path.get_total_length():
            self.reached_end = True
            self.alive = False

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return self.value
        return 0

    def get_position(self):
        return self.path.get_position_at_distance(self.distance)

    def get_rect(self):
        x, y = self.get_position()
        return pygame.Rect(x - ENEMY_SIZE // 2, y - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)

    def draw(self, screen):
        if not self.alive:
            return

        x, y = self.get_position()

        # Body
        color_intensity = int(255 * (self.health / self.max_health))
        color = (255, max(50, color_intensity), 50)
        pygame.draw.circle(screen, color, (int(x), int(y)), ENEMY_SIZE // 2)

        # Outline
        pygame.draw.circle(screen, (200, 50, 50), (int(x), int(y)), ENEMY_SIZE // 2, 2)

        # Health bar
        bar_width = ENEMY_SIZE
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y - ENEMY_SIZE // 2 - 8

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = (50, 200, 50) if self.health > self.max_health * 0.3 else (200, 50, 50)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
