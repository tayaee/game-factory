import pygame
import math
from config import TOWER_SIZE, TOWER_TYPES, PROJECTILE_SPEED, PROJECTILE_SIZE


class Projectile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = PROJECTILE_SPEED
        self.active = True

    def update(self):
        if not self.target.alive:
            self.active = False
            return

        tx, ty = self.target.get_position()
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < self.speed:
            self.x = tx
            self.y = ty
            self.target.take_damage(self.damage)
            self.active = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(self.y)), PROJECTILE_SIZE)


class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type_id = tower_type
        self.config = TOWER_TYPES[tower_type]
        self.cooldown = 0
        self.max_cooldown = self.config["fire_rate"]
        self.angle = 0

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1

        target = self._find_target(enemies)
        if target:
            tx, ty = target.get_position()
            self.angle = math.degrees(math.atan2(ty - self.y, tx - self.x))

            if self.cooldown <= 0:
                return self._shoot(target)
        return None

    def _find_target(self, enemies):
        closest = None
        closest_dist = self.config["range"]

        for enemy in enemies:
            if not enemy.alive:
                continue
            ex, ey = enemy.get_position()
            dist = math.sqrt((ex - self.x)**2 + (ey - self.y)**2)
            if dist < closest_dist:
                closest = enemy
                closest_dist = dist

        return closest

    def _shoot(self, target):
        self.cooldown = self.max_cooldown
        return Projectile(self.x, self.y, target, self.config["damage"])

    def draw(self, screen):
        color = self.config["color"]

        # Base
        pygame.draw.circle(screen, (50, 50, 60), (int(self.x), int(self.y)), TOWER_SIZE // 2 + 3)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), TOWER_SIZE // 2)

        # Turret
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * (TOWER_SIZE // 2)
        end_y = self.y + math.sin(angle_rad) * (TOWER_SIZE // 2)
        pygame.draw.line(screen, (30, 30, 30), (self.x, self.y), (end_x, end_y), 4)

        # Center
        pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), 5)

    def get_rect(self):
        return pygame.Rect(self.x - TOWER_SIZE // 2, self.y - TOWER_SIZE // 2, TOWER_SIZE, TOWER_SIZE)

    def draw_range(self, screen):
        pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.config["range"], 1)
