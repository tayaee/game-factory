"""Game entities for Road Fighter Racing."""

import pygame
import random
from typing import Optional
from config import *


class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 150
        self.velocity = 0.0
        self.lateral_velocity = 0.0
        self.distance = 0.0
        self.fuel = INITIAL_FUEL
        self.lane = 1  # 0-3, starting in lane 1
        self.target_x = self._get_lane_center(1)
        self.invincible = 0
        self.crashing = False
        self.crash_timer = 0

    def _get_lane_center(self, lane: int) -> float:
        return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - PLAYER_WIDTH // 2,
            self.y - PLAYER_HEIGHT // 2,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

    def accelerate(self):
        if self.velocity < PLAYER_MAX_SPEED:
            self.velocity += PLAYER_ACCELERATION

    def brake(self):
        if self.velocity > PLAYER_MIN_SPEED:
            self.velocity -= PLAYER_BRAKING

    def change_lane(self, direction: int):
        if self.crashing:
            return
        new_lane = self.lane + direction
        if 0 <= new_lane < NUM_LANES:
            self.lane = new_lane
            self.target_x = self._get_lane_center(new_lane)

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1

        if self.crashing:
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashing = False
            return

        # Smooth lateral movement
        dx = self.target_x - self.x
        if abs(dx) > 1:
            self.x += dx * 0.2
        else:
            self.x = self.target_x

        # Apply friction
        self.velocity *= PLAYER_FRICTION
        if self.velocity < PLAYER_MIN_SPEED:
            self.velocity = PLAYER_MIN_SPEED

        # Consume fuel based on speed
        fuel_cost = FUEL_CONSUMPTION_RATE * (self.velocity / PLAYER_MIN_SPEED)
        self.fuel -= fuel_cost
        if self.fuel < 0:
            self.fuel = 0

        # Update distance
        self.distance += self.velocity

    def crash(self):
        if self.invincible > 0:
            return False
        self.crashing = True
        self.crash_timer = 30
        self.invincible = 60
        self.velocity *= 0.3
        self.fuel -= 50
        if self.fuel < 0:
            self.fuel = 0
        return True


class Enemy:
    def __init__(self, distance: float, erratic: bool = False):
        self.distance = distance
        self.lane = random.randint(0, NUM_LANES - 1)
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.erratic = erratic
        self.change_lane_timer = random.randint(60, 180)
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT

    def get_screen_y(self, player_distance: float) -> float:
        relative_distance = self.distance - player_distance
        screen_y = WINDOW_HEIGHT - 100 - relative_distance
        return screen_y

    def get_screen_x(self) -> float:
        return ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def get_rect(self, player_distance: float) -> pygame.Rect:
        y = self.get_screen_y(player_distance)
        x = self.get_screen_x()
        return pygame.Rect(
            x - self.width // 2,
            y - self.height // 2,
            self.width,
            self.height
        )

    def update(self):
        self.distance -= self.speed

        if self.erratic:
            self.change_lane_timer -= 1
            if self.change_lane_timer <= 0:
                direction = random.choice([-1, 1])
                new_lane = self.lane + direction
                if 0 <= new_lane < NUM_LANES:
                    self.lane = new_lane
                self.change_lane_timer = random.randint(60, 180)

    def is_visible(self, player_distance: float) -> bool:
        y = self.get_screen_y(player_distance)
        return -50 < y < WINDOW_HEIGHT + 50


class FuelTank:
    def __init__(self, distance: float):
        self.distance = distance
        self.lane = random.randint(0, NUM_LANES - 1)
        self.width = FUEL_WIDTH
        self.height = FUEL_HEIGHT
        self.collected = False

    def get_screen_y(self, player_distance: float) -> float:
        relative_distance = self.distance - player_distance
        screen_y = WINDOW_HEIGHT - 100 - relative_distance
        return screen_y

    def get_screen_x(self) -> float:
        return ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def get_rect(self, player_distance: float) -> pygame.Rect:
        y = self.get_screen_y(player_distance)
        x = self.get_screen_x()
        return pygame.Rect(
            x - self.width // 2,
            y - self.height // 2,
            self.width,
            self.height
        )

    def is_visible(self, player_distance: float) -> bool:
        y = self.get_screen_y(player_distance)
        return -50 < y < WINDOW_HEIGHT + 50
