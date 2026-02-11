import pygame
import sys
import random
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ObjectType(Enum):
    LOG = "log"
    TURTLE = "turtle"
    CROCODILE = "crocodile"


@dataclass
class Lane:
    y: int
    speed: float
    direction: int  # -1 for left, 1 for right
    obj_type: ObjectType
    obj_width: int
    obj_count: int
    spacing: int


class GameObject:
    def __init__(self, x: int, y: int, width: int, height: int, obj_type: ObjectType):
        self.rect = pygame.Rect(x, y, width, height)
        self.obj_type = obj_type
        self.turtle_state = 0  # 0 = visible, 1 = submerged
        self.turtle_timer = random.uniform(0, 3)

    def update(self, dt: float):
        if self.obj_type == ObjectType.TURTLE:
            self.turtle_timer += dt
            if self.turtle_timer >= 3:
                self.turtle_state = 1 - self.turtle_state  # Toggle
                self.turtle_timer = 0

    def is_safe(self) -> bool:
        if self.obj_type == ObjectType.LOG:
            return True
        elif self.obj_type == ObjectType.TURTLE:
            return self.turtle_state == 0  # Safe when visible
        elif self.obj_type == ObjectType.CROCODILE:
            return True  # Safe if on back (not mouth)


class Game:
    GRID_SIZE = 20
    GRID_W = 20
    GRID_H = 20
    CELL_SIZE = 30
    SCREEN_W = GRID_W * CELL_SIZE
    SCREEN_H = GRID_H * CELL_SIZE

    COLORS = {
        "water": (30, 100, 180),
        "frog": (50, 200, 50),
        "log": (139, 90, 43),
        "turtle": (100, 200, 100),
        "turtle_submerged": (50, 100, 80),
        "crocodile": (70, 180, 70),
        "crocodile_mouth": (200, 50, 50),
        "lilypad": (60, 180, 60),
        "safe_zone": (50, 150, 50),
        "text": (255, 255, 255),
        "bg": (20, 20, 20),
    }

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption("Vector Frogger - Crocodile Marsh")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.frog_x = self.GRID_W // 2
        self.frog_y = self.GRID_H - 1
        self.frog_on_object: Optional[GameObject] = None
        self.frog_offset = 0.0

        self.lives = 3
        self.score = 0
        self.time_left = 60.0
        self.game_over = False
        self.won = False

        self.goal_lilypads = [False] * 5
        self.lilypad_positions = [
            2, 6, 10, 14, 18  # Grid positions for 5 lilypads
        ]

        self._init_lanes()

    def _init_lanes(self):
        self.lanes: List[Lane] = []
        self.objects: List[List[GameObject]] = []

        # River lanes (rows 2-7, 6 lanes)
        # Lane configuration: y position, speed, direction, object type, width, count, spacing
        lane_configs = [
            # Top river lane - Crocodiles (fast)
            Lane(2, 2.5, 1, ObjectType.CROCODILE, 4, 2, 10),
            # Turtles (submerging)
            Lane(3, 1.0, -1, ObjectType.TURTLE, 2, 4, 6),
            # Logs (slow)
            Lane(4, 0.8, 1, ObjectType.LOG, 5, 2, 12),
            # Turtles (medium)
            Lane(5, 1.5, -1, ObjectType.TURTLE, 3, 3, 8),
            # Logs (fast)
            Lane(6, 2.0, 1, ObjectType.LOG, 4, 2, 10),
            # Crocodiles (medium)
            Lane(7, 1.8, -1, ObjectType.CROCODILE, 3, 3, 9),
        ]

        for lane in lane_configs:
            self.lanes.append(lane)
            lane_objects = []
            for i in range(lane.obj_count):
                x = i * lane.spacing
                obj = GameObject(x, lane.y * self.CELL_SIZE,
                               lane.obj_width * self.CELL_SIZE, self.CELL_SIZE,
                               lane.obj_type)
                lane_objects.append(obj)
            self.objects.append(lane_objects)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_ESCAPE:
                        return False

                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                        self.score += 10
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1

                    if dx != 0 or dy != 0:
                        new_x = self.frog_x + dx
                        new_y = self.frog_y + dy

                        if 0 <= new_x < self.GRID_W and 0 <= new_y < self.GRID_H:
                            self.frog_x = new_x
                            self.frog_y = new_y
                            self.frog_offset = 0
                            self.frog_on_object = None

                            # Check goal reached
                            if self.frog_y == 0:
                                for i, lx in enumerate(self.lilypad_positions):
                                    if abs(self.frog_x - lx) <= 1 and not self.goal_lilypads[i]:
                                        self.goal_lilypads[i] = True
                                        self.score += 1000
                                        self._reset_frog_position()

                                        if all(self.goal_lilypads):
                                            self.won = True
                                        break

        return True

    def _reset_frog_position(self):
        self.frog_x = self.GRID_W // 2
        self.frog_y = self.GRID_H - 1
        self.frog_on_object = None
        self.frog_offset = 0

    def update(self, dt: float):
        if self.game_over or self.won:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self._lose_life()
            self.time_left = 60.0

        # Update objects and check collisions
        frog_rect = pygame.Rect(
            self.frog_x * self.CELL_SIZE + 5,
            self.frog_y * self.CELL_SIZE + 5,
            self.CELL_SIZE - 10,
            self.CELL_SIZE - 10
        )

        in_river = 2 <= self.frog_y <= 7

        for lane_idx, lane in enumerate(self.lanes):
            for obj in self.objects[lane_idx]:
                obj.update(dt)

                # Move object
                obj.rect.x += lane.speed * lane.direction * dt * 60

                # Wrap around
                if lane.direction == 1 and obj.rect.x > self.SCREEN_W:
                    obj.rect.x = -obj.rect.width
                elif lane.direction == -1 and obj.rect.right < 0:
                    obj.rect.x = self.SCREEN_W

                # Check if frog is on this lane
                if self.frog_y == lane.y:
                    obj_hitbox = obj.rect.copy()

                    if obj.obj_type == ObjectType.CROCODILE:
                        # Right 1/3 is mouth (dangerous)
                        mouth_width = obj.rect.width // 3
                        obj_hitbox.width = obj.rect.width - mouth_width

                    if frog_rect.colliderect(obj_hitbox):
                        self.frog_on_object = obj
                        self.frog_offset = (obj.rect.centerx - frog_rect.centerx) / self.CELL_SIZE

        if in_river:
            if self.frog_on_object is None:
                self._lose_life()
            elif not self._is_on_object_safe():
                self._lose_life()
            else:
                # Move with object
                lane_idx = self.frog_y - 2
                lane = self.lanes[lane_idx]
                self.frog_x += (lane.speed * lane.direction * dt * 60) / self.CELL_SIZE

                # Check bounds
                if self.frog_x < 0 or self.frog_x >= self.GRID_W:
                    self._lose_life()
        else:
            self.frog_on_object = None

    def _is_on_object_safe(self) -> bool:
        if self.frog_on_object is None:
            return False

        obj = self.frog_on_object

        if obj.obj_type == ObjectType.TURTLE:
            return obj.turtle_state == 0  # Safe when visible (not submerged)

        if obj.obj_type == ObjectType.CROCODILE:
            # Check if near the mouth (right side)
            frog_pixel_x = self.frog_x * self.CELL_SIZE + self.CELL_SIZE // 2
            obj_pixel_x = obj.rect.x

            rel_x = frog_pixel_x - obj_pixel_x
            mouth_threshold = obj.rect.width * 2 / 3

            return rel_x < mouth_threshold  # Safe if not near mouth

        return True  # Logs are always safe

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self._reset_frog_position()
            self.time_left = min(self.time_left + 10, 60)

    def draw(self):
        self.screen.fill(self.COLORS["bg"])

        # Draw water area
        water_rect = pygame.Rect(0, 2 * self.CELL_SIZE, self.SCREEN_W, 6 * self.CELL_SIZE)
        pygame.draw.rect(self.screen, self.COLORS["water"], water_rect)

        # Draw goal lilypads
        for i, (filled, x) in enumerate(zip(self.goal_lilypads, self.lilypad_positions)):
            color = self.COLORS["safe_zone"] if filled else self.COLORS["lilypad"]
            pygame.draw.ellipse(self.screen, color,
                              (x * self.CELL_SIZE, 0, 2 * self.CELL_SIZE, self.CELL_SIZE))

        # Draw safe zones
        pygame.draw.rect(self.screen, self.COLORS["safe_zone"],
                        (0, 1 * self.CELL_SIZE, self.SCREEN_W, self.CELL_SIZE))
        pygame.draw.rect(self.screen, self.COLORS["safe_zone"],
                        (0, 8 * self.CELL_SIZE, self.SCREEN_W, 12 * self.CELL_SIZE))

        # Draw objects
        for lane_idx, lane in enumerate(self.lanes):
            for obj in self.objects[lane_idx]:
                if obj.obj_type == ObjectType.LOG:
                    pygame.draw.rect(self.screen, self.COLORS["log"], obj.rect, border_radius=5)

                elif obj.obj_type == ObjectType.TURTLE:
                    if obj.turtle_state == 0:  # Visible
                        pygame.draw.ellipse(self.screen, self.COLORS["turtle"], obj.rect)
                    else:  # Submerged
                        pygame.draw.ellipse(self.screen, self.COLORS["turtle_submerged"], obj.rect)

                elif obj.obj_type == ObjectType.CROCODILE:
                    # Body (safe - back area)
                    safe_width = obj.rect.width * 2 // 3
                    safe_rect = pygame.Rect(obj.rect.x, obj.rect.y, safe_width, obj.rect.height)
                    pygame.draw.ellipse(self.screen, self.COLORS["crocodile"], safe_rect)

                    # Mouth (dangerous)
                    mouth_rect = pygame.Rect(obj.rect.x + safe_width, obj.rect.y + 5,
                                           obj.rect.width - safe_width, obj.rect.height - 10)
                    pygame.draw.ellipse(self.screen, self.COLORS["crocodile_mouth"], mouth_rect)

        # Draw frog
        frog_color = self.COLORS["frog"]
        frog_rect = pygame.Rect(
            int(self.frog_x * self.CELL_SIZE + 5),
            self.frog_y * self.CELL_SIZE + 5,
            self.CELL_SIZE - 10,
            self.CELL_SIZE - 10
        )
        pygame.draw.ellipse(self.screen, frog_color, frog_rect)

        # Draw eyes on frog
        eye_radius = 3
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (frog_rect.x + 8, frog_rect.y + 5), eye_radius)
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (frog_rect.right - 8, frog_rect.y + 5), eye_radius)
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (frog_rect.x + 8, frog_rect.y + 5), eye_radius // 2)
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (frog_rect.right - 8, frog_rect.y + 5), eye_radius // 2)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, self.COLORS["text"])
        lives_text = self.font.render(f"Lives: {self.lives}", True, self.COLORS["text"])
        time_text = self.font.render(f"Time: {int(self.time_left)}", True, self.COLORS["text"])

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (self.SCREEN_W // 2 - 40, 10))
        self.screen.blit(time_text, (self.SCREEN_W - 100, 10))

        # Draw game over / win screen
        if self.game_over:
            self._draw_overlay("GAME OVER", f"Final Score: {self.score}", "Press SPACE to restart")
        elif self.won:
            self._draw_overlay("YOU WIN!", f"Final Score: {self.score + int(self.time_left) * 10}", "Press SPACE to play again")

        pygame.display.flip()

    def _draw_overlay(self, title: str, subtitle: str, instruction: str):
        overlay = pygame.Surface((self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render(title, True, self.COLORS["text"])
        subtitle_text = self.font.render(subtitle, True, self.COLORS["text"])
        instr_text = self.font.render(instruction, True, (150, 150, 150))

        title_rect = title_text.get_rect(center=(self.SCREEN_W // 2, self.SCREEN_H // 2 - 40))
        subtitle_rect = subtitle_text.get_rect(center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 10))
        instr_rect = instr_text.get_rect(center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 50))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(instr_text, instr_rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            running = self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
