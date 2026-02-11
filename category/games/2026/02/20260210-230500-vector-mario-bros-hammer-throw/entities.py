"""Game entities for Vector Mario Bros Hammer Throw."""

import math
from config import *


class Hammer:
    """Projectile thrown by the player."""

    def __init__(self, x, y, angle, power):
        self.x = x
        self.y = y
        angle_rad = math.radians(angle)
        self.vx = math.cos(angle_rad) * power
        self.vy = -math.sin(angle_rad) * power
        self.active = True
        self.rotation = 0
        self.rot_speed = 10

    def update(self, dt):
        """Update hammer position."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += GRAVITY * dt
        self.vx *= AIR_RESISTANCE
        self.rotation += self.rot_speed

        # Check bounds
        if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
            self.y > SCREEN_HEIGHT + 50):
            self.active = False
            return "miss"
        return None

    def get_hitbox(self):
        """Return circular hitbox."""
        return {
            "type": "circle",
            "x": self.x,
            "y": self.y,
            "radius": HAMMER_RADIUS
        }

    def draw(self, surface):
        """Draw the hammer."""
        import pygame

        # Handle position (handle)
        handle_color = COLOR_HAMMER
        head_color = COLOR_HAMMER_HEAD

        # Simple hammer shape
        handle_rect = pygame.Rect(0, 0, 16, 6)
        handle_rect.center = (self.x, self.y)

        # Head
        head_rect = pygame.Rect(0, 0, HAMMER_HEAD_SIZE, HAMMER_HEAD_SIZE + 4)
        head_rect.midleft = (self.x + 8, self.y)

        pygame.draw.rect(surface, handle_color, handle_rect)
        pygame.draw.rect(surface, head_color, head_rect)


class Enemy:
    """Base enemy class."""

    def __init__(self, x, y, platform_y, enemy_type="koopa"):
        self.x = x
        self.y = y
        self.platform_y = platform_y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.type = enemy_type
        self.direction = 1
        self.speed = KOOPA_SPEED if enemy_type == "koopa" else GOOMBA_SPEED
        self.alive = True
        self.frame = 0
        self.frame_timer = 0

    def update(self, dt):
        """Update enemy position."""
        self.x += self.speed * self.direction * dt

        # Bounce at screen edges
        if self.x <= 50:
            self.direction = 1
        elif self.x >= SCREEN_WIDTH - 50:
            self.direction = -1

        # Animation
        self.frame_timer += dt
        if self.frame_timer > 0.2:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 2

    def get_hitbox(self):
        """Return rectangular hitbox."""
        return {
            "type": "rect",
            "x": self.x - self.width // 2,
            "y": self.y - self.height,
            "width": self.width,
            "height": self.height
        }

    def draw(self, surface):
        """Draw the enemy."""
        import pygame

        if self.type == "koopa":
            color = COLOR_KOOPA
            # Shell
            shell_rect = pygame.Rect(
                self.x - self.width // 2,
                self.y - self.height,
                self.width,
                self.height - 8
            )
            pygame.draw.ellipse(surface, color, shell_rect)

            # Head
            head_y = self.y - self.height - 8
            pygame.draw.circle(surface, (200, 220, 200), (int(self.x), int(head_y)), 8)

            # Eyes
            eye_offset = 3 if self.direction > 0 else -3
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + eye_offset), int(head_y - 2)), 2)

        else:  # goomba
            color = COLOR_GOOMBA
            # Body (mushroom shape)
            body_rect = pygame.Rect(
                self.x - self.width // 2,
                self.y - self.height,
                self.width,
                self.height - 6
            )
            pygame.draw.ellipse(surface, color, body_rect)

            # Stem/feet
            feet_width = self.width // 2 + 4
            feet_rect = pygame.Rect(
                self.x - feet_width // 2,
                self.y - 8,
                feet_width,
                8
            )
            pygame.draw.ellipse(surface, (180, 140, 100), feet_rect)

            # Eyes
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 5), int(self.y - 22)), 4)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 5), int(self.y - 22)), 4)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x - 5), int(self.y - 22)), 2)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 5), int(self.y - 22)), 2)


class Player:
    """Player character."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.angle = 45
        self.power = 0
        self.charging = False
        self.hammers_left = MAX_HAMMERS
        self.frame = 0
        self.frame_timer = 0
        self.throwing = False
        self.throw_timer = 0

    def update(self, dt):
        """Update player state."""
        if self.throwing:
            self.throw_timer += dt
            if self.throw_timer > 0.2:
                self.throwing = False
                self.throw_timer = 0

        # Animation
        self.frame_timer += dt
        if self.frame_timer > 0.15:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 4

    def adjust_angle(self, delta):
        """Adjust throw angle."""
        self.angle = max(MIN_ANGLE, min(MAX_ANGLE, self.angle + delta))

    def start_charge(self):
        """Start charging power."""
        if not self.charging and self.hammers_left > 0:
            self.charging = True
            self.power = MIN_POWER

    def update_charge(self, dt):
        """Update charging power."""
        if self.charging:
            self.power = min(MAX_POWER, self.power + CHARGE_RATE * dt)

    def release_throw(self):
        """Release the throw."""
        if self.charging and self.hammers_left > 0:
            self.charging = False
            self.hammers_left -= 1
            self.throwing = True
            return Hammer(self.x + self.width, self.y - 10, self.angle, self.power)
        return None

    def get_hitbox(self):
        """Return rectangular hitbox."""
        return {
            "type": "rect",
            "x": self.x,
            "y": self.y - self.height,
            "width": self.width,
            "height": self.height
        }

    def draw(self, surface):
        """Draw the player."""
        import pygame

        # Body
        body_rect = pygame.Rect(
            self.x + 5,
            self.y - self.height + 15,
            self.width - 10,
            self.height - 15
        )
        pygame.draw.rect(surface, COLOR_PLAYER_OVERALLS, body_rect)

        # Head
        head_y = self.y - self.height + 5
        pygame.draw.circle(surface, COLOR_PLAYER, (int(self.x + self.width // 2), int(head_y)), 10)

        # Hat
        hat_rect = pygame.Rect(self.x, self.y - self.height, self.width, 8)
        pygame.draw.rect(surface, (200, 0, 0), hat_rect)

        # Eyes
        eye_y = head_y - 2
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 - 4), int(eye_y)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 + 4), int(eye_y)), 2)

        # Arm and hammer when charging/throwing
        if self.charging or self.throwing:
            arm_end_x = self.x + self.width + 15
            arm_end_y = self.y - 15
            pygame.draw.line(surface, COLOR_PLAYER,
                           (self.x + self.width - 5, self.y - 20),
                           (arm_end_x, arm_end_y), 4)


class Platform:
    """Platform for player to stand on."""

    def __init__(self, y, width=SCREEN_WIDTH):
        self.y = y
        self.width = width
        self.height = 20
        self.x = (SCREEN_WIDTH - width) // 2

    def draw(self, surface):
        """Draw the platform."""
        import pygame

        # Top surface
        top_rect = pygame.Rect(self.x, self.y, self.width, 5)
        pygame.draw.rect(surface, COLOR_PLATFORM_TOP, top_rect)

        # Body
        body_rect = pygame.Rect(self.x, self.y + 5, self.width, self.height - 5)
        pygame.draw.rect(surface, COLOR_PLATFORM, body_rect)

        # Brick pattern
        for i in range(0, self.width, 40):
            pygame.draw.line(surface, (120, 60, 20),
                           (self.x + i, self.y + 5),
                           (self.x + i, self.y + self.height), 2)
