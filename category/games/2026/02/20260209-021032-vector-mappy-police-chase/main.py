"""
Vector Mappy Police Chase
A 2D side-scrolling platformer inspired by the classic arcade game Mappy.
Navigate a multi-story mansion as a police mouse to retrieve stolen goods while avoiding agile cats.
"""

import pygame
import sys
import random
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (30, 30, 40)
COLOR_FLOOR = (70, 70, 80)
COLOR_FLOOR_EDGE = (90, 90, 100)
COLOR_WALL = (50, 50, 60)
COLOR_PLAYER = (50, 180, 255)
COLOR_PLAYER_EARS = (30, 140, 200)
COLOR_CAT = (255, 100, 80)
COLOR_CAT_EARS = (200, 60, 40)
COLOR_ITEM = (255, 215, 0)
COLOR_TRAMPOLINE = (100, 200, 100)
COLOR_TRAMPOLINE_DAMAGED = (200, 100, 100)
COLOR_DOOR = (139, 90, 43)
COLOR_DOOR_OPEN = (100, 60, 30)
COLOR_TEXT = (255, 255, 255)

# Game physics
PLAYER_SPEED = 5
JUMP_FORCE = -12
GRAVITY = 0.6
CAT_SPEED = 2
CAT_CHASE_SPEED = 3
TRAMPOLINE_BOUNCE_FORCE = -15
MAX_TRAMPOLINE_JUMPS = 3

# Level settings
NUM_FLOORS = 6
FLOOR_HEIGHT = 15
FLOOR_Y_START = 150
FLOOR_Y_SPACING = 75
DOOR_WIDTH = 35
DOOR_HEIGHT = 50
TRAMPOLINE_WIDTH = 50
TRAMPOLINE_HEIGHT = 15
ITEM_SIZE = 20


class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    VICTORY = 2
    LEVEL_TRANSITION = 3


class TrampolineState(Enum):
    NORMAL = 0
    WARNING = 1
    BROKEN = 2


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


class Trampoline:
    def __init__(self, x, floor_y):
        self.x = x
        self.y = floor_y - TRAMPOLINE_HEIGHT
        self.width = TRAMPOLINE_WIDTH
        self.height = TRAMPOLINE_HEIGHT
        self.jumps_used = 0
        self.state = TrampolineState.NORMAL
        self.warning_timer = 0

    def update(self):
        if self.jumps_used >= MAX_TRAMPOLINE_JUMPS - 1:
            self.state = TrampolineState.WARNING
        if self.jumps_used >= MAX_TRAMPOLINE_JUMPS:
            self.state = TrampolineState.BROKEN

        if self.state == TrampolineState.WARNING:
            self.warning_timer += 1

    def draw(self, surface):
        if self.state == TrampolineState.BROKEN:
            color = COLOR_TRAMPOLINE_DAMAGED
            # Draw broken trampoline
            pygame.draw.line(surface, color, (self.x, self.y + self.height // 2),
                           (self.x + self.width // 2, self.y + self.height), 3)
            pygame.draw.line(surface, color, (self.x + self.width // 2, self.y + self.height),
                           (self.x + self.width, self.y + self.height // 2), 3)
            return

        # Flash warning
        if self.state == TrampolineState.WARNING and (self.warning_timer // 5) % 2 == 0:
            color = COLOR_TRAMPOLINE_DAMAGED
        else:
            color = COLOR_TRAMPOLINE

        # Trampoline base
        pygame.draw.ellipse(surface, color, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(surface, (80, 160, 80), (self.x, self.y, self.width, self.height), 2)

        # Springs
        for i in range(5):
            spring_x = self.x + 8 + i * 9
            pygame.draw.line(surface, (60, 60, 60),
                           (spring_x, self.y + self.height // 2),
                           (spring_x, self.y + self.height), 2)

        # Jump counter
        jumps_left = MAX_TRAMPOLINE_JUMPS - self.jumps_used
        if jumps_left > 0:
            for i in range(jumps_left):
                dot_x = self.x + 10 + i * 8
                pygame.draw.circle(surface, (255, 255, 255), (dot_x, self.y - 8), 3)


class Door:
    def __init__(self, x, floor_y):
        self.x = x
        self.y = floor_y - DOOR_HEIGHT
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.is_open = False
        self.close_timer = 0

    def draw(self, surface):
        color = COLOR_DOOR_OPEN if self.is_open else COLOR_DOOR

        # Door frame
        pygame.draw.rect(surface, (80, 50, 20), (self.x - 3, self.y - 3, self.width + 6, self.height + 6))

        if self.is_open:
            # Dark opening
            pygame.draw.rect(surface, (20, 15, 10), (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        else:
            # Door
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (100, 65, 30), (self.x, self.y, self.width, self.height), 2)
            # Handle
            pygame.draw.circle(surface, (200, 200, 200), (self.x + self.width - 8, self.y + self.height // 2), 3)

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.close_timer = 120  # Auto-close after 2 seconds

    def update(self):
        if self.is_open and self.close_timer > 0:
            self.close_timer -= 1
            if self.close_timer == 0:
                self.is_open = False


class Item:
    def __init__(self, x, floor_y):
        self.x = x
        self.y = floor_y - ITEM_SIZE - 5
        self.width = ITEM_SIZE
        self.height = ITEM_SIZE
        self.collected = False
        self.bob_offset = random.random() * 6.28
        self.value = random.choice([100, 200, 300, 500])

    def update(self):
        self.bob_offset += 0.1

    def draw(self, surface):
        if self.collected:
            return

        bob_y = self.y + int(pygame.math.sin(self.bob_offset) * 3)

        # Glow effect
        glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, 50), (self.width // 2 + 5, self.height // 2 + 5), self.width // 2 + 3)
        surface.blit(glow_surface, (self.x - 5, bob_y - 5))

        # Item (treasure chest appearance)
        pygame.draw.rect(surface, COLOR_ITEM, (self.x, bob_y, self.width, self.height))
        pygame.draw.rect(surface, (200, 160, 0), (self.x, bob_y, self.width, self.height), 2)
        # Lid line
        pygame.draw.line(surface, (200, 160, 0), (self.x, bob_y + self.height // 3),
                        (self.x + self.width, bob_y + self.height // 3), 2)
        # Lock
        pygame.draw.circle(surface, (200, 160, 0), (self.x + self.width // 2, bob_y + self.height // 2 + 3), 3)

    def get_rect(self):
        bob_y = self.y + int(pygame.math.sin(self.bob_offset) * 3)
        return pygame.Rect(self.x, bob_y, self.width, self.height)


class Cat:
    def __init__(self, x, floor_index):
        self.start_x = x
        self.x = x
        self.floor_index = floor_index
        self.y = FLOOR_Y_START + floor_index * FLOOR_Y_SPACING - 35
        self.width = 35
        self.height = 35
        self.speed = CAT_SPEED
        self.direction = random.choice([Direction.LEFT, Direction.RIGHT])
        self.patrol_range = 100
        self.state = "patrol"  # patrol, chase, stunned
        self.stun_timer = 0
        self.jump_vel_y = 0
        self.on_trampoline = None
        self.trampoline_jumps = 0

    def update(self, player, floors, doors, trampolines):
        if self.state == "stunned":
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "patrol"
            return

        # Check if on same floor as player for chase
        player_floor = -1
        for i, floor_y in enumerate(floors):
            if abs(player.y - floor_y) < 50:
                player_floor = i
                break

        # Check for line of sight
        can_see_player = False
        if player_floor == self.floor_index:
            dx = player.x - self.x
            if (self.direction == Direction.RIGHT and dx > 0) or (self.direction == Direction.LEFT and dx < 0):
                # Check if doors are blocking
                blocked = False
                for door in doors:
                    if door.is_open:
                        continue
                    door_x = door.x + door.width // 2
                    if min(self.x, player.x) < door_x < max(self.x, player.x):
                        blocked = True
                        break
                if not blocked and abs(dx) < 250:
                    can_see_player = True

        if can_see_player and self.state != "chase":
            self.state = "chase"
        elif not can_see_player and self.state == "chase":
            self.state = "patrol"

        target_speed = CAT_CHASE_SPEED if self.state == "chase" else CAT_SPEED

        # Horizontal movement
        if self.state == "chase":
            if player.x > self.x:
                self.direction = Direction.RIGHT
                self.x += target_speed
            else:
                self.direction = Direction.LEFT
                self.x -= target_speed
        else:
            # Patrol
            self.x += target_speed * self.direction.value
            if self.x > self.start_x + self.patrol_range:
                self.direction = Direction.LEFT
            elif self.x < self.start_x - self.patrol_range:
                self.direction = Direction.RIGHT

        # Keep in bounds
        self.x = max(50, min(self.x, SCREEN_WIDTH - 50))

        # Update floor position
        self.y = FLOOR_Y_START + self.floor_index * FLOOR_Y_SPACING - 35

        # Check trampoline
        self.on_trampoline = None
        for trampoline in trampolines:
            if trampoline.state != TrampolineState.BROKEN:
                tramp_rect = pygame.Rect(trampoline.x, trampoline.y, trampoline.width, trampoline.height)
                cat_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if tramp_rect.colliderect(cat_rect):
                    self.on_trampoline = trampoline
                    # Auto bounce on trampoline
                    self.floor_index = max(0, self.floor_index - 1)
                    self.trampoline_jumps += 1
                    if self.trampoline_jumps >= MAX_TRAMPOLINE_JUMPS:
                        trampoline.jumps_used = MAX_TRAMPOLINE_JUMPS
                    break

        # Check door collision (stun if hit by closing door)
        cat_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for door in doors:
            if not door.is_open:
                door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
                if door_rect.colliderect(cat_rect):
                    self.state = "stunned"
                    self.stun_timer = 120

    def draw(self, surface):
        if self.state == "stunned":
            # Stunned appearance (dizzy)
            pygame.draw.circle(surface, COLOR_CAT, (int(self.x + self.width // 2), int(self.y + self.height // 2)), 15)
            # Stars
            for i in range(3):
                angle = (self.stun_timer // 10 + i * 120) * 3.14159 / 180
                star_x = self.x + self.width // 2 + int(25 * pygame.math.cos(angle))
                star_y = self.y + self.height // 2 - 15 + int(25 * pygame.math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 100), (star_x, star_y), 3)
            return

        # Body
        body_color = (220, 80, 60) if self.state == "chase" else COLOR_CAT
        pygame.draw.ellipse(surface, body_color, (self.x, self.y + 10, self.width, self.height - 10))

        # Head
        pygame.draw.circle(surface, body_color, (int(self.x + self.width // 2), int(self.y + 12)), 12)

        # Ears
        ear_color = COLOR_CAT_EARS if self.state != "chase" else (180, 50, 30)
        pygame.draw.polygon(surface, ear_color, [
            (self.x + 8, self.y + 8),
            (self.x + 3, self.y - 5),
            (self.x + 13, self.y + 5)
        ])
        pygame.draw.polygon(surface, ear_color, [
            (self.x + self.width - 8, self.y + 8),
            (self.x + self.width - 3, self.y - 5),
            (self.x + self.width - 13, self.y + 5)
        ])

        # Eyes
        eye_offset = 4 if self.direction == Direction.RIGHT else -4
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.width // 2 + eye_offset - 3), int(self.y + 10)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.width // 2 + eye_offset + 3), int(self.y + 10)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 + eye_offset - 3), int(self.y + 10)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 + eye_offset + 3), int(self.y + 10)), 2)

        # Tail
        tail_start = (self.x + self.width // 2, self.y + 25)
        tail_end = (self.x + self.width // 2 + (20 if self.direction == Direction.RIGHT else -20), self.y + 30)
        pygame.draw.line(surface, body_color, tail_start, tail_end, 4)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Player:
    def __init__(self):
        self.width = 30
        self.height = 35
        self.x = 100
        self.y = FLOOR_Y_START - self.height
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.alive = True
        self.score = 0
        self.items_collected = 0
        self.total_items = 0
        self.facing_direction = Direction.RIGHT
        self.current_floor = 0
        self.lives = 3
        self.invincible_timer = 0
        self.on_trampoline = None
        self.trampoline_jumps = 0

    def update(self, keys, floors, doors, items, trampolines):
        if not self.alive:
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing_direction = Direction.LEFT
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing_direction = Direction.RIGHT

        # Apply horizontal movement
        new_x = self.x + self.vel_x
        new_x = max(10, min(new_x, SCREEN_WIDTH - self.width - 10))
        self.x = new_x

        # Check door interaction
        for door in doors:
            door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
            player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

            if door_rect.colliderect(player_rect):
                dist_to_center = abs((door.x + door.width // 2) - (self.x + self.width // 2))
                if dist_to_center < 20:
                    door.toggle()

        # Check trampoline
        self.on_trampoline = None
        for trampoline in trampolines:
            if trampoline.state != TrampolineState.BROKEN:
                tramp_rect = pygame.Rect(trampoline.x, trampoline.y, trampoline.width, trampoline.height)
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

                if tramp_rect.colliderect(player_rect) and self.vel_y >= 0:
                    self.on_trampoline = trampoline
                    # Bounce
                    self.vel_y = TRAMPOLINE_BOUNCE_FORCE
                    self.on_ground = False
                    trampoline.jumps_used += 1
                    self.trampoline_jumps += 1
                    self.score += 10
                    break

        # Gravity
        if not self.on_ground and self.on_trampoline is None:
            self.vel_y += GRAVITY

        # Apply vertical movement
        new_y = self.y + self.vel_y

        # Floor collision
        self.on_ground = False
        for i, floor_y in enumerate(floors):
            floor_rect = pygame.Rect(0, floor_y, SCREEN_WIDTH, FLOOR_HEIGHT)
            player_rect = pygame.Rect(self.x, new_y, self.width, self.height)

            if floor_rect.colliderect(player_rect) and self.vel_y >= 0:
                if self.y + self.height <= floor_y + 20:
                    self.y = floor_y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.current_floor = i
                    self.trampoline_jumps = 0
                    break

        if not self.on_ground and self.on_trampoline is None:
            self.y = new_y

        # Prevent falling below screen
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

        # Update current floor
        for i, floor_y in enumerate(floors):
            if abs(self.y + self.height - floor_y) < 20:
                self.current_floor = i
                break

        # Check item collection
        for item in items:
            if not item.collected:
                if item.get_rect().colliderect(pygame.Rect(self.x, self.y, self.width, self.height)):
                    item.collected = True
                    self.items_collected += 1
                    self.score += item.value

    def draw(self, surface):
        if not self.alive:
            return

        # Flash when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        # Tail
        tail_start = (self.x + self.width // 2, self.y + 28)
        tail_end = (self.x + self.width // 2 + (15 if self.facing_direction == Direction.RIGHT else -15), self.y + 32)
        pygame.draw.line(surface, COLOR_PLAYER_EARS, tail_start, tail_end, 3)

        # Body
        pygame.draw.ellipse(surface, COLOR_PLAYER, (self.x, self.y + 12, self.width, self.height - 12))

        # Head
        pygame.draw.circle(surface, COLOR_PLAYER, (int(self.x + self.width // 2), int(self.y + 12)), 11)

        # Ears (large mouse ears)
        ear_color = COLOR_PLAYER_EARS
        pygame.draw.circle(surface, ear_color, (int(self.x + 6), int(self.y + 6)), 7)
        pygame.draw.circle(surface, ear_color, (int(self.x + self.width - 6), int(self.y + 6)), 7)
        pygame.draw.circle(surface, (200, 230, 255), (int(self.x + 6), int(self.y + 6)), 4)
        pygame.draw.circle(surface, (200, 230, 255), (int(self.x + self.width - 6), int(self.y + 6)), 4)

        # Eyes
        eye_offset = 3 if self.facing_direction == Direction.RIGHT else -3
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.width // 2 + eye_offset - 3), int(self.y + 10)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.width // 2 + eye_offset + 3), int(self.y + 10)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 + eye_offset - 3), int(self.y + 10)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width // 2 + eye_offset + 3), int(self.y + 10)), 1)

        # Nose
        pygame.draw.circle(surface, (255, 150, 180), (int(self.x + self.width // 2 + eye_offset), int(self.y + 15)), 2)

        # Police badge
        pygame.draw.circle(surface, (255, 215, 0), (int(self.x + self.width // 2), int(self.y + 18)), 4)
        pygame.draw.circle(surface, (200, 160, 0), (int(self.x + self.width // 2), int(self.y + 18)), 4, 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Mappy Police Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.floors = [FLOOR_Y_START + i * FLOOR_Y_SPACING for i in range(NUM_FLOORS)]
        self.doors = []
        self.trampolines = []
        self.items = []
        self.cats = []
        self.state = GameState.PLAYING
        self.level = 1
        self.level_timer = 0
        self.transition_timer = 0

        self.create_level()

    def create_level(self):
        self.doors.clear()
        self.trampolines.clear()
        self.items.clear()
        self.cats.clear()
        self.player.total_items = 0
        self.player.items_collected = 0

        # Create doors on each floor (except top)
        for i in range(1, NUM_FLOORS):
            floor_y = self.floors[i]
            num_doors = random.randint(2, 4)
            door_x_positions = random.sample(range(100, SCREEN_WIDTH - 100, 70), num_doors)

            for x in door_x_positions:
                self.doors.append(Door(x, floor_y))

        # Create trampolines on each floor
        for i in range(NUM_FLOORS - 1):
            floor_y = self.floors[i]
            num_trampolines = random.randint(1, 2)
            tramp_x_positions = random.sample(range(120, SCREEN_WIDTH - 120, 80), num_trampolines)

            for x in tramp_x_positions:
                self.trampolines.append(Trampoline(x, floor_y))

        # Create items scattered across floors
        for i in range(NUM_FLOORS):
            floor_y = self.floors[i]
            num_items = random.randint(2, 4)
            item_x_positions = random.sample(range(80, SCREEN_WIDTH - 80, 50), num_items)

            for x in item_x_positions:
                item = Item(x, floor_y)
                self.items.append(item)
                self.player.total_items += 1

        # Create cats (more on higher levels)
        num_cats = 2 + self.level
        for _ in range(num_cats):
            floor = random.randint(1, NUM_FLOORS - 1)
            x = random.randint(150, SCREEN_WIDTH - 150)
            self.cats.append(Cat(x, floor))

        # Ensure player starts with at least 3 items accessible
        while self.player.total_items < 5:
            floor_y = self.floors[random.randint(0, NUM_FLOORS - 1)]
            x = random.randint(100, SCREEN_WIDTH - 100)
            item = Item(x, floor_y)
            self.items.append(item)
            self.player.total_items += 1

        # Reset player position
        self.player.x = 100
        self.player.y = self.floors[0] - self.player.height
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.on_ground = True
        self.player.trampoline_jumps = 0

    def update(self):
        if self.state != GameState.PLAYING:
            if self.state == GameState.LEVEL_TRANSITION:
                self.transition_timer -= 1
                if self.transition_timer <= 0:
                    self.level += 1
                    self.create_level()
                    self.state = GameState.PLAYING
            return

        keys = pygame.key.get_pressed()

        # Update doors
        for door in self.doors:
            door.update()

        # Update trampolines
        for trampoline in self.trampolines:
            trampoline.update()

        # Update items
        for item in self.items:
            item.update()

        # Update player
        self.player.update(keys, self.floors, self.doors, self.items, self.trampolines)

        # Update cats
        for cat in self.cats:
            cat.update(self.player, self.floors, self.doors, self.trampolines)

            # Check collision with player
            if self.player.invincible_timer == 0:
                if cat.get_rect().colliderect(self.player.get_rect()) and cat.state != "stunned":
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.player.alive = False
                        self.state = GameState.GAME_OVER
                    else:
                        # Respawn
                        self.player.x = 100
                        self.player.y = self.floors[0] - self.player.height
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.player.invincible_timer = 120
                        self.player.trampoline_jumps = 0

        # Check win condition (all items collected)
        if self.player.items_collected >= self.player.total_items:
            self.player.score += 1000 + (self.level * 500)
            self.state = GameState.LEVEL_TRANSITION
            self.transition_timer = 120

        self.level_timer += 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if self.state == GameState.GAME_OVER:
                    self.reset_game()
            elif event.key == pygame.K_SPACE and self.player.on_ground and self.player.on_trampoline is None:
                self.player.vel_y = JUMP_FORCE
                self.player.on_ground = False

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw background building elements
        pygame.draw.rect(self.screen, COLOR_WALL, (20, 0, SCREEN_WIDTH - 40, SCREEN_HEIGHT))

        # Draw floors
        for floor_y in self.floors:
            pygame.draw.rect(self.screen, COLOR_FLOOR, (30, floor_y, SCREEN_WIDTH - 60, FLOOR_HEIGHT))
            pygame.draw.line(self.screen, COLOR_FLOOR_EDGE, (30, floor_y), (SCREEN_WIDTH - 30, floor_y), 2)

        # Draw trampolines
        for trampoline in self.trampolines:
            trampoline.draw(self.screen)

        # Draw doors
        for door in self.doors:
            door.draw(self.screen)

        # Draw items
        for item in self.items:
            item.draw(self.screen)

        # Draw cats
        for cat in self.cats:
            cat.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game state messages
        if self.state == GameState.GAME_OVER:
            self.draw_message("GAME OVER", f"Final Score: {self.player.score} - Press R to restart")
        elif self.state == GameState.LEVEL_TRANSITION:
            self.draw_message(f"LEVEL {self.level} COMPLETE!", f"Score: {self.player.score} - Get ready for Level {self.level + 1}!")

        pygame.display.flip()

    def draw_hud(self):
        # Top bar background
        pygame.draw.rect(self.screen, (20, 20, 30), (0, 0, SCREEN_WIDTH, 45))

        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Items
        item_color = (255, 255, 100) if self.player.items_collected >= self.player.total_items else COLOR_TEXT
        items_text = self.small_font.render(
            f"Items: {self.player.items_collected}/{self.player.total_items}",
            True, item_color
        )
        self.screen.blit(items_text, (150, 10))

        # Lives
        lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, (255, 100, 100))
        self.screen.blit(lives_text, (300, 10))

        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (400, 10))

        # Time bonus
        time_bonus = max(0, 3000 - self.level_timer)
        time_text = self.small_font.render(f"Bonus: {time_bonus}", True, (100, 255, 100))
        self.screen.blit(time_text, (500, 10))

        # Controls hint
        hint_text = self.tiny_font.render("Arrows: Move | SPACE: Jump | Near door: Auto-toggle", True, (120, 120, 130))
        self.screen.blit(hint_text, (SCREEN_WIDTH - 380, 12))

    def draw_message(self, title, subtitle):
        title_surface = self.font.render(title, True, COLOR_TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, COLOR_TEXT)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        # Semi-transparent background
        bg_rect = pygame.Rect(0, 0, 550, 100)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(220)
        s.fill((0, 0, 0))
        self.screen.blit(s, bg_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_TEXT, bg_rect, 2)

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_event(event)

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
