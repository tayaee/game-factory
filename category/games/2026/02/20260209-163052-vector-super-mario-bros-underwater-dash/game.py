"""Game state and underwater physics logic for Vector Super Mario Bros Underwater Dash."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Vec2:
    x: float
    y: float


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)
        self.width = 24
        self.height = 28
        self.facing_right = True
        self.alive = True
        self.finished = False
        self.swim_frame = 0.0
        self.bubbles = []

    def update(self, dt: float, inputs: dict, platforms: List[dict]):
        if not self.alive or self.finished:
            return

        # Underwater physics - high drag, low gravity
        accel = 400.0
        drag = 0.92
        gravity = 300.0
        swim_force = 500.0
        max_speed = 180.0
        max_fall_speed = 100.0

        # Horizontal movement
        if inputs['left']:
            self.vel.x -= accel * dt
            self.facing_right = False
        if inputs['right']:
            self.vel.x += accel * dt
            self.facing_right = True

        # Swimming upward (overcomes gravity)
        if inputs['swim']:
            self.vel.y -= swim_force * dt
            self.swim_frame += dt * 15
            # Add bubbles
            if len(self.bubbles) < 5 and int(self.swim_frame) % 5 == 0:
                self.bubbles.append([self.pos.x + 12, self.pos.y + 28, 0])
        else:
            self.swim_frame += dt * 5

        # Apply drag
        self.vel.x *= drag
        self.vel.y *= drag

        # Clamp velocities
        self.vel.x = max(-max_speed, min(max_speed, self.vel.x))
        self.vel.y = max(-max_speed, min(max_fall_speed, self.vel.y))

        # Apply gravity (slower underwater)
        self.vel.y += gravity * dt

        # Update position
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        # Update bubbles
        for bubble in self.bubbles:
            bubble[1] -= 60 * dt
            bubble[2] += dt

        # Remove old bubbles
        self.bubbles = [b for b in self.bubbles if b[2] < 1.0]

        # Platform collision
        for plat in platforms:
            px, py, pw, ph = plat['x'], plat['y'], plat['w'], plat['h']
            if (self.pos.x + self.width > px and self.pos.x < px + pw and
                self.pos.y + self.height > py and self.pos.y < py + ph):

                # Determine collision side
                overlap_left = (self.pos.x + self.width) - px
                overlap_right = (px + pw) - self.pos.x
                overlap_top = (self.pos.y + self.height) - py
                overlap_bottom = (py + ph) - self.pos.y

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_top:
                    self.pos.y = py - self.height
                    if self.vel.y > 0:
                        self.vel.y = 0
                elif min_overlap == overlap_bottom:
                    self.pos.y = py + ph
                    if self.vel.y < 0:
                        self.vel.y = 0
                elif min_overlap == overlap_left:
                    self.pos.x = px - self.width
                    if self.vel.x > 0:
                        self.vel.x = 0
                else:
                    self.pos.x = px + pw
                    if self.vel.x < 0:
                        self.vel.x = 0

        # Screen bounds
        self.pos.x = max(0, min(self.pos.x, 800 - self.width))
        self.pos.y = max(0, min(self.pos.y, 600 - self.height))


class Blooper:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.start_y = y
        self.vel = Vec2(0.0, -80.0)
        self.width = 32
        self.height = 40
        self.phase = 0.0
        self.alive = True

    def update(self, dt: float):
        if not self.alive:
            return

        self.phase += dt * 2

        # Wavy vertical movement
        self.pos.y = self.start_y + (self.vel.y * dt * 50)
        if abs(self.pos.y - self.start_y) > 100:
            self.vel.y *= -1

        # Slight horizontal drift
        self.pos.x += 30 * dt


class CheepCheep:
    def __init__(self, x: float, y: float, direction: int):
        self.pos = Vec2(x, y)
        self.vel = Vec2(120.0 * direction, 0.0)
        self.width = 28
        self.height = 24
        self.alive = True

    def update(self, dt: float):
        if not self.alive:
            return

        self.pos.x += self.vel.x * dt

        # Gentle wave motion
        self.pos.y += 20 * dt


class Coin:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.radius = 10
        self.collected = False
        self.bob_offset = 0.0


class GameState:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.reset()

    def reset(self):
        self.player = Player(50, 300)
        self.score = 0
        self.game_over = False
        self.win = False
        self.time_elapsed = 0.0

        # Underwater cavern level - platforms
        self.platforms = [
            {'x': 0, 'y': 0, 'w': 800, 'h': 20},         # Ceiling
            {'x': 0, 'y': 580, 'w': 800, 'h': 20},       # Floor
            {'x': 0, 'y': 0, 'w': 20, 'h': 600},         # Left wall
            {'x': 780, 'y': 0, 'w': 20, 'h': 600},       # Right wall

            {'x': 150, 'y': 150, 'w': 100, 'h': 20},     # Upper platform
            {'x': 150, 'y': 430, 'w': 100, 'h': 20},     # Lower platform
            {'x': 300, 'y': 280, 'w': 80, 'h': 20},      # Middle platform
            {'x': 450, 'y': 120, 'w': 120, 'h': 20},     # Upper right
            {'x': 450, 'y': 460, 'w': 120, 'h': 20},     # Lower right
            {'x': 620, 'y': 280, 'w': 80, 'h': 20},      # Far middle
            {'x': 700, 'y': 200, 'w': 60, 'h': 20},      # Far upper
        ]

        # Enemies - Bloopers (vertical patrollers)
        self.bloopers = [
            Blooper(200, 300),
            Blooper(340, 300),
            Blooper(500, 300),
        ]

        # Enemies - Cheep Cheeps (horizontal swimmers)
        self.cheeps = [
            CheepCheep(100, 450, 1),
            CheepCheep(100, 150, 1),
            CheepCheep(600, 400, -1),
            CheepCheep(600, 200, -1),
        ]

        # Coins scattered throughout
        self.coins = [
            Coin(100, 300),
            Coin(200, 120),
            Coin(200, 400),
            Coin(340, 240),
            Coin(340, 320),
            Coin(510, 80),
            Coin(510, 440),
            Coin(660, 240),
            Coin(730, 160),
        ]

        # Goal flag position
        self.flag_x = 750
        self.flag_y = 300

    def update(self, dt: float, inputs: dict):
        if self.game_over:
            return

        self.time_elapsed += dt

        # Update player
        self.player.update(dt, inputs, self.platforms)

        # Update enemies
        for blooper in self.bloopers:
            blooper.update(dt)

        for cheep in self.cheeps:
            cheep.update(dt)
            # Wrap cheeps that go off screen
            if cheep.pos.x < -50:
                cheep.pos.x = 850
            elif cheep.pos.x > 850:
                cheep.pos.x = -50

        # Update coins bobbing animation
        for coin in self.coins:
            coin.bob_offset += dt * 3

        # Enemy collision
        player_rect = (self.player.pos.x, self.player.pos.y,
                       self.player.width, self.player.height)

        # Check Blooper collision
        for blooper in self.bloopers:
            if not blooper.alive:
                continue

            blooper_rect = (blooper.pos.x, blooper.pos.y,
                           blooper.width, blooper.height)

            if self._rects_collide(player_rect, blooper_rect):
                self.player.alive = False
                self.score = 0
                self.game_over = True

        # Check Cheep Cheep collision
        for cheep in self.cheeps:
            if not cheep.alive:
                continue

            cheep_rect = (cheep.pos.x, cheep.pos.y,
                         cheep.width, cheep.height)

            if self._rects_collide(player_rect, cheep_rect):
                self.player.alive = False
                self.score = 0
                self.game_over = True

        # Coin collection
        for coin in self.coins:
            if not coin.collected:
                dx = self.player.pos.x + self.player.width / 2 - coin.pos.x
                dy = (self.player.pos.y + self.player.height / 2 -
                      (coin.pos.y + 3 * (coin.bob_offset % 2 - 1)))
                if (dx * dx + dy * dy) < (coin.radius + 16) ** 2:
                    coin.collected = True
                    self.score += 100

        # Flag goal - reach the right side
        if (self.player.pos.x + self.player.width > self.flag_x and
            not self.player.finished):
            self.player.finished = True
            self.score += 500
            self.win = True
            self.game_over = True

        # Death handling
        if not self.player.alive:
            self.game_over = True

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1])
