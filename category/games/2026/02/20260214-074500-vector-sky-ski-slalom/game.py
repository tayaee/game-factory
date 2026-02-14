"""Game logic for Vector Sky Ski Slalom."""

import random
import pygame
from config import *
from entities import Player, Obstacle, Gate


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.gates = []
        self.scroll_speed = BASE_SCROLL_SPEED
        self.distance = 0
        self.score = 0
        self.game_over = False
        self.time_elapsed = 0
        self.spawn_timer = 0
        self.next_spawn_interval = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
        self.gate_spawn_timer = 0
        self.previous_gate_y = 0

    def update(self, dt, inputs):
        if self.game_over:
            return

        self.time_elapsed += dt

        # Increase difficulty over time
        self.scroll_speed = min(
            MAX_SCROLL_SPEED,
            BASE_SCROLL_SPEED + self.time_elapsed * SPEED_INCREASE_RATE
        )

        # Update player
        self.player.update(dt, inputs)

        # Spawn new objects
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_interval:
            self.spawn_object()
            self.spawn_timer = 0
            self.next_spawn_interval = random.uniform(
                SPAWN_INTERVAL_MIN,
                max(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX - self.time_elapsed * 0.05)
            )

        # Update obstacles
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles[:]:
            obstacle.update(dt, self.scroll_speed)

            if self.player.collides_with(obstacle.get_rect()):
                self.game_over = True
                self.player.alive = False

            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)

        # Update gates
        for gate in self.gates[:]:
            prev_y = self.previous_gate_y
            self.previous_gate_y = gate.y
            gate.update(dt, self.scroll_speed)

            # Check collision with poles
            if self.player.collides_with(gate.get_left_pole_rect()) or \
               self.player.collides_with(gate.get_right_pole_rect()):
                self.game_over = True
                self.player.alive = False

            # Check gate pass for bonus
            if gate.check_gate_pass(player_rect, prev_y):
                self.score += GATE_BONUS

            if gate.is_off_screen():
                self.gates.remove(gate)

        # Update distance and score
        self.distance += self.scroll_speed * dt
        self.score = int(self.distance // SCORE_MULTIPLIER * SCORE_PER_DISTANCE)

        # Spawn gates periodically
        self.gate_spawn_timer += dt
        if self.gate_spawn_timer >= 5.0:  # Every 5 seconds try to spawn a gate
            if random.random() < 0.6:  # 60% chance
                self.gates.append(Gate())
            self.gate_spawn_timer = 0

    def spawn_object(self):
        # Decide between obstacle or gate
        if len(self.gates) == 0 and random.random() < 0.2:
            self.gates.append(Gate())
        else:
            self.obstacles.append(Obstacle(self.scroll_speed))
