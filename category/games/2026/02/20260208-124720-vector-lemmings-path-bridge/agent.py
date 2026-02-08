"""Agent (lemming) class for autonomous explorers."""

import pygame
from config import *


class Agent:
    """Autonomous explorer that walks, falls, and can be assigned skills."""

    def __init__(self, x, y, agent_id):
        """Initialize agent at position."""
        self.x = x
        self.y = y
        self.vx = WALK_SPEED
        self.vy = 0
        self.id = agent_id
        self.alive = True
        self.saved = False
        self.state = "falling"  # falling, walking, blocked, building, bashing
        self.skill = SKILL_NONE
        self.skill_timer = 0
        self.fall_distance = 0
        self.animation_frame = 0
        self.blocker_radius = BLOCKER_RADIUS
        self.bridge_direction = 1  # 1 = right, -1 = left

    def update(self, level, blockers):
        """Update agent physics and AI behavior."""
        if not self.alive or self.saved:
            return

        self.animation_frame = (self.animation_frame + 1) % 20

        if self.state == "blocked":
            return  # Blockers don't move

        if self.state == "building":
            self._update_building(level)
            return

        if self.state == "bashing":
            self._update_bashing(level)
            return

        # Apply gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # Check for blockers ahead
        if self.state == "walking":
            for blocker in blockers:
                if blocker == self:
                    continue
                dist = ((self.x - blocker.x) ** 2 + (self.y - blocker.y) ** 2) ** 0.5
                if dist < blocker.blocker_radius:
                    # Turn around
                    self.vx = -self.vx
                    self.bridge_direction = -self.vx / WALK_SPEED
                    break

        # Move and check collisions
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        # Convert to grid coordinates
        grid_x = int(new_x // TILE_SIZE)
        grid_y = int(new_y // TILE_SIZE)

        # Check hazard collision
        if level.is_hazard(grid_x, grid_y):
            self.alive = False
            return

        # Check exit
        if level.is_exit(grid_x, grid_y):
            self.saved = True
            return

        # Ground collision
        ground_y = int((new_y + AGENT_HEIGHT) // TILE_SIZE)
        if level.is_solid(grid_x, ground_y):
            if self.vy > 0:
                # Landed
                if self.fall_distance > TILE_SIZE * 4:
                    # Fell too far
                    self.alive = False
                    return
                self.y = ground_y * TILE_SIZE - AGENT_HEIGHT
                self.vy = 0
                self.state = "walking"
                self.fall_distance = 0
        else:
            self.state = "falling"
            self.fall_distance += abs(self.vy)

        # Wall collision
        if self.vx > 0:  # Moving right
            wall_x = int((new_x + AGENT_WIDTH) // TILE_SIZE)
            check_y = int(self.y // TILE_SIZE)
            if level.is_solid(wall_x, check_y):
                self.x = wall_x * TILE_SIZE - AGENT_WIDTH - 1
                self.vx = -WALK_SPEED
                self.bridge_direction = 1
                new_x = self.x
        else:  # Moving left
            wall_x = int(new_x // TILE_SIZE)
            check_y = int(self.y // TILE_SIZE)
            if level.is_solid(wall_x, check_y):
                self.x = (wall_x + 1) * TILE_SIZE
                self.vx = WALK_SPEED
                self.bridge_direction = -1
                new_x = self.x

        # Screen bounds
        if new_x < 0 or new_x > SCREEN_WIDTH:
            self.alive = False
            return

        self.x = new_x
        self.y = new_y

    def _update_building(self, level):
        """Update bridge building state."""
        self.skill_timer += 1
        if self.skill_timer >= 5:  # Build every 5 frames
            self.skill_timer = 0
            grid_x, grid_y = level.pixel_to_grid(self.x, self.y)
            level.build_bridge(grid_x, grid_y - 1, self.bridge_direction)
            self.state = "walking"

    def _update_bashing(self, level):
        """Update wall bashing state."""
        self.skill_timer += 1
        if self.skill_timer >= 10:  # Bash every 10 frames
            bash_x = int((self.x + AGENT_WIDTH // 2) // TILE_SIZE)
            if self.vx > 0:
                bash_x += 1
            bash_y = int((self.y + AGENT_HEIGHT // 2) // TILE_SIZE)

            if level.remove_tile(bash_x, bash_y):
                self.skill_timer = 0
            else:
                # Done bashing (no more wall)
                self.state = "walking"

    def assign_skill(self, skill):
        """Assign a skill to this agent."""
        if self.state in ("blocked", "building", "bashing"):
            return False

        if skill == SKILL_BLOCKER:
            self.state = "blocked"
        elif skill == SKILL_BUILDER:
            self.state = "building"
            self.skill_timer = 0
        elif skill == SKILL_BASHER:
            self.state = "bashing"
            self.skill_timer = 0

        self.skill = skill
        return True

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(int(self.x), int(self.y), AGENT_WIDTH, AGENT_HEIGHT)

    def draw(self, surface):
        """Draw the agent."""
        if not self.alive:
            return

        if self.saved:
            # Draw faded
            alpha = 100
        else:
            alpha = 255

        rect = self.get_rect()

        if self.state == "blocked":
            # Draw blocker as larger circle
            pygame.draw.circle(surface, HAZARD_RED, rect.center, 10)
            pygame.draw.circle(surface, BLACK, rect.center, 10, 2)
        elif self.state == "building":
            # Draw builder with hammer
            pygame.draw.rect(surface, GRASS_GREEN, rect)
            # Draw hammer
            hammer_end = (rect.centerx + 8 * self.bridge_direction, rect.centery - 8)
            pygame.draw.line(surface, BLACK, rect.center, hammer_end, 3)
        elif self.state == "bashing":
            # Draw basher with pickaxe
            pygame.draw.rect(surface, GOLD, rect)
            # Draw pickaxe
            pick_end = (rect.centerx + 10 * (1 if self.vx > 0 else -1), rect.centery)
            pygame.draw.line(surface, BLACK, rect.center, pick_end, 3)
        else:
            # Draw normal agent
            # Body
            color = WHITE
            if self.state == "falling":
                color = (200, 200, 255)
            elif self.state == "walking":
                # Waddle animation
                offset = 2 if (self.animation_frame // 5) % 2 == 0 else 0
                pygame.draw.circle(surface, color, (rect.centerx, rect.bottom - 3 - offset), 4)

            pygame.draw.rect(surface, color, rect)

            # Eyes
            eye_x = rect.right - 5 if self.vx > 0 else rect.left + 3
            pygame.draw.circle(surface, BLACK, (eye_x, rect.top + 4), 2)

        pygame.draw.rect(surface, BLACK, rect, 1)
