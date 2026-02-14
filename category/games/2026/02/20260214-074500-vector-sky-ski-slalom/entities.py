"""Game entities for Vector Sky Ski Slalom."""

import random
import pygame
from config import *


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = PLAYER_START_X
        self.y = PLAYER_START_Y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.alive = True

    def update(self, dt, inputs):
        if not self.alive:
            return

        if inputs['left']:
            self.x -= PLAYER_SPEED * dt
        if inputs['right']:
            self.x += PLAYER_SPEED * dt

        # Keep player in bounds
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def collides_with(self, rect):
        return self.get_rect().colliderect(rect)


class Obstacle:
    def __init__(self, scroll_speed):
        self.y = -50
        self.obstacle_type = random.choice(['tree', 'snowmobile'])
        self.passed = False

        if self.obstacle_type == 'tree':
            self.width = TREE_WIDTH
            self.height = TREE_HEIGHT
            self.x = random.randint(self.width, SCREEN_WIDTH - self.width)
            self.speed = 0
        else:  # snowmobile
            self.width = SNOWMOBILE_WIDTH
            self.height = SNOWMOBILE_HEIGHT
            direction = random.choice([-1, 1])
            if direction == -1:
                self.x = SCREEN_WIDTH + self.width // 2
            else:
                self.x = -self.width // 2
            self.speed = SNOWMOBILE_SPEED * direction

    def update(self, dt, scroll_speed):
        self.y += scroll_speed * dt
        if self.obstacle_type == 'snowmobile':
            self.x += self.speed * dt

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 100 or \
               self.x < -100 or self.x > SCREEN_WIDTH + 100


class Gate:
    def __init__(self):
        self.y = -50
        self.height = GATE_POLE_HEIGHT
        self.passed = False

        gap = random.randint(GATE_GAP_MIN, GATE_GAP_MAX)
        center_x = random.randint(gap, SCREEN_WIDTH - gap)
        self.left_pole_x = center_x - gap // 2
        self.right_pole_x = center_x + gap // 2

    def update(self, dt, scroll_speed):
        self.y += scroll_speed * dt

    def get_left_pole_rect(self):
        return pygame.Rect(
            self.left_pole_x - GATE_POLE_WIDTH // 2,
            self.y - self.height // 2,
            GATE_POLE_WIDTH,
            self.height
        )

    def get_right_pole_rect(self):
        return pygame.Rect(
            self.right_pole_x - GATE_POLE_WIDTH // 2,
            self.y - self.height // 2,
            GATE_POLE_WIDTH,
            self.height
        )

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 100

    def check_gate_pass(self, player_rect, previous_y):
        if self.passed:
            return False

        current_y = self.y
        if previous_y > self.height // 2 and current_y <= self.height // 2:
            # Check if player is between the poles
            center_x = player_rect.centerx
            if self.left_pole_x < center_x < self.right_pole_x:
                self.passed = True
                return True
        return False
