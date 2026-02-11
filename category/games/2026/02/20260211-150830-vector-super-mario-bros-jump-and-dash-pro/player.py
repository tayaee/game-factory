import pygame
from config import *


class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True

        # Dash mechanics
        self.dash_charges = MAX_DASH_CHARGES
        self.dash_cooldown = 0
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_refill_timer = 0

        # Jump mechanics - variable height
        self.jump_held = False
        self.jump_held_time = 0
        self.max_jump_hold_time = 12  # frames

    def start_jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.jump_held = True
            self.jump_held_time = 0

    def release_jump(self):
        self.jump_held = False

    def dash(self, direction):
        if self.dash_charges > 0 and self.dash_cooldown == 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = DASH_DURATION
            self.dash_charges -= 1
            self.dash_cooldown = DASH_COOLDOWN
            self.vx = direction * DASH_SPEED
            # Brief invulnerability and gravity reduction during dash
            return True
        return False

    def update(self, keys_pressed, platforms):
        # Handle dash state
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.vx *= 0.5  # Slow down after dash
        else:
            # Horizontal movement
            target_vx = 0
            if keys_pressed[pygame.K_LEFT]:
                target_vx = -MOVE_SPEED
                self.facing_right = False
            if keys_pressed[pygame.K_RIGHT]:
                target_vx = MOVE_SPEED
                self.facing_right = True

            # Apply acceleration and friction
            if target_vx != 0:
                self.vx += (target_vx - self.vx) * ACCELERATION
            else:
                self.vx *= FRICTION

        # Apply gravity (reduced during dash)
        if not self.is_dashing or self.vy > 0:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED

        # Variable jump height - reduce upward velocity if jump released early
        if self.jump_held and not self.on_ground:
            self.jump_held_time += 1
            if self.jump_held_time > self.max_jump_hold_time:
                self.jump_held = False

        if not self.jump_held and self.vy < -3:
            self.vy *= 0.85

        # Apply cooldowns
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Refill dash charges over time
        self.dash_refill_timer += 1
        if self.dash_refill_timer >= DASH_REFILL_RATE:
            self.dash_refill_timer = 0
            if self.dash_charges < MAX_DASH_CHARGES:
                self.dash_charges += 1

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Platform collision
        self.on_ground = False
        player_rect = self.get_rect()

        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Check if landing on top
                if self.vy > 0 and player_rect.bottom <= platform.rect.bottom:
                    # Only land if we were above the platform
                    prev_y = self.y - self.vy
                    prev_bottom = prev_y + PLAYER_HEIGHT
                    if prev_bottom <= platform.rect.top + 10:
                        self.y = platform.rect.top - PLAYER_HEIGHT
                        self.vy = 0
                        self.on_ground = True
                        self.is_dashing = False

    def get_rect(self):
        return pygame.Rect(
            self.x + 4,
            self.y + 4,
            PLAYER_WIDTH - 8,
            PLAYER_HEIGHT - 8
        )

    def draw(self, screen, camera_x):
        draw_x = self.x - camera_x
        draw_y = self.y

        # Main body
        body_rect = pygame.Rect(draw_x, draw_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(screen, PLAYER_COLOR, body_rect, border_radius=4)

        # Accent (hat-like top)
        pygame.draw.rect(
            screen,
            PLAYER_ACCENT_COLOR,
            (draw_x, draw_y, PLAYER_WIDTH, 12),
            border_top_left_radius=4,
            border_top_right_radius=4
        )

        # Eyes
        eye_x = draw_x + (20 if self.facing_right else 6)
        pygame.draw.rect(screen, (255, 255, 255), (eye_x, draw_y + 14, 6, 6))
        pygame.draw.rect(screen, (0, 0, 0), (eye_x + (2 if self.facing_right else 1), draw_y + 15, 3, 3))

        # Dash trail effect
        if self.is_dashing:
            for i in range(3):
                offset = (i + 1) * 8
                alpha = 100 - i * 30
                trail_rect = pygame.Rect(
                    draw_x - (offset if self.vx > 0 else -offset),
                    draw_y + 5,
                    PLAYER_WIDTH - 10,
                    PLAYER_HEIGHT - 10
                )
                trail_surface = pygame.Surface((trail_rect.width, trail_rect.height), pygame.SRCALPHA)
                trail_surface.fill((*PLAYER_COLOR, alpha))
                screen.blit(trail_surface, trail_rect.topleft)

    def is_off_screen(self, camera_x):
        return self.y > MAX_FALL_Y

    def set_checkpoint(self, x, y):
        self.start_x = x
        self.start_y = y
