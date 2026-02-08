"""Main game class."""

import pygame
import sys
from typing import Optional, Tuple
from config import *
from physics import PhysicsEngine, Block
from tower import Tower


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        self.tower = Tower()
        self.physics = PhysicsEngine()

        # Add tower blocks to physics
        for block in self.tower.blocks:
            self.physics.add_block(block)

        # Game state
        self.selected_block: Optional[Block] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.score = 0
        self.game_over = False
        self.game_state = "ready"  # ready, playing, game_over, won

        # UI
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)

    def reset_game(self):
        """Reset the game to initial state."""
        self.tower = Tower()
        self.physics = PhysicsEngine()

        for block in self.tower.blocks:
            self.physics.add_block(block)

        self.selected_block = None
        self.score = 0
        self.game_over = False
        self.game_state = "ready"

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_state in ("game_over", "won"):
                        self.reset_game()
                    elif self.game_state == "ready":
                        self.game_state = "playing"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_down(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.handle_mouse_up()

            elif event.type == pygame.MOUSEMOTION:
                if self.selected_block and self.selected_block.is_dragging:
                    self.handle_mouse_drag(event.pos)

    def handle_mouse_down(self, pos: Tuple[int, int]):
        """Handle mouse button down."""
        if self.game_state != "playing":
            if self.game_state in ("ready", "game_over", "won"):
                self.game_state = "playing" if self.game_state == "ready" else "reset"
                if self.game_state == "reset":
                    self.reset_game()
            return

        x, y = pos

        # Check if clicking on a block
        block = self.tower.get_block_at(x, y)

        if block and self.tower.can_select_block(block):
            self.selected_block = block
            block.is_dragging = True
            self.drag_offset_x = block.x - x
            self.drag_offset_y = block.y - y
            self.physics.remove_block(block)

    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse drag."""
        if not self.selected_block:
            return

        x, y = pos
        self.selected_block.x = x + self.drag_offset_x
        self.selected_block.y = y + self.drag_offset_y

    def handle_mouse_up(self):
        """Handle mouse button release."""
        if not self.selected_block:
            return

        block = self.selected_block

        if self.tower.is_in_drop_zone(block.x, block.y):
            # Try to place on top
            if self.tower.place_block_on_top(block, block.x):
                self.score += SCORE_PER_BLOCK
            else:
                # Invalid placement, return block (simplified: just drop it)
                block.is_dragging = False
                block.is_removed = False
        else:
            # Not in drop zone, drop the block (physics will handle it)
            block.is_dragging = False

        self.selected_block = None

    def update(self):
        """Update game state."""
        if self.game_state != "playing":
            return

        dt = 1.0 / FPS

        # Update physics
        self.physics.update(dt)

        # Check for collapse
        if self.physics.check_collapse():
            self.score += PENALTY_COLLAPSE
            self.game_state = "game_over"
            self.game_over = True

    def render(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw drop zone
        self._draw_drop_zone()

        # Draw ground
        pygame.draw.rect(
            self.screen,
            COLOR_GROUND,
            (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)
        )

        # Draw blocks
        self._draw_blocks()

        # Draw UI
        self._draw_ui()

        # Draw game state messages
        if self.game_state == "ready":
            self._draw_centered_message(
                "Vector Tumble Tower Collapse",
                COLOR_BLOCK_SELECTED,
                offset=-50
            )
            self._draw_centered_message(
                "Click blocks to pull, place on top",
                COLOR_TEXT,
                offset=0
            )
            self._draw_centered_message(
                "Click or press SPACE to start",
                COLOR_TEXT,
                offset=40
            )
        elif self.game_state == "game_over":
            self._draw_centered_message(
                "Tower Collapsed!",
                COLOR_TEXT_WARNING,
                offset=-20
            )
            self._draw_centered_message(
                f"Final Score: {self.score}",
                COLOR_TEXT,
                offset=20
            )
            self._draw_centered_message(
                "Press SPACE to restart",
                COLOR_TEXT,
                offset=60
            )

        pygame.display.flip()

    def _draw_drop_zone(self):
        """Draw the drop zone at the top."""
        dz_x, dz_y, dz_w, dz_h = self.tower.get_drop_zone_rect()

        # Create transparent surface
        surface = pygame.Surface((dz_w, dz_h), pygame.SRCALPHA)
        surface.fill(COLOR_DROP_ZONE)
        self.screen.blit(surface, (dz_x, dz_y))

        # Draw border
        pygame.draw.rect(
            self.screen,
            (100, 200, 100),
            (dz_x, dz_y, dz_w, dz_h),
            2
        )

        # Label
        label = self.font.render("DROP ZONE", True, (150, 255, 150))
        label_rect = label.get_rect(center=(dz_x + dz_w / 2, dz_y + dz_h / 2))
        self.screen.blit(label, label_rect)

    def _draw_blocks(self):
        """Draw all blocks."""
        # Sort by layer for proper rendering order
        sorted_blocks = sorted(self.tower.blocks, key=lambda b: b.layer)

        for block in sorted_blocks:
            self._draw_block(block)

    def _draw_block(self, block: Block):
        """Draw a single block."""
        # Determine color
        if block.is_collapsed:
            color = (100, 60, 60)
        elif block == self.selected_block:
            color = COLOR_BLOCK_SELECTED
        elif (self.selected_block is None and
              not block.is_removed and
              self.tower.can_select_block(block)):
            # Check hover
            mx, my = pygame.mouse.get_pos()
            if block.contains_point(mx, my):
                color = COLOR_BLOCK_HOVER
            else:
                color = COLOR_BLOCK_EVEN if block.layer % 2 == 0 else COLOR_BLOCK_ODD
        else:
            color = COLOR_BLOCK_EVEN if block.layer % 2 == 0 else COLOR_BLOCK_ODD

        # Get corners for rotated drawing
        corners = block.get_corners()

        # Draw main block
        pygame.draw.polygon(self.screen, color, corners)
        pygame.draw.polygon(self.screen, (50, 30, 10), corners, 2)

        # Draw 3D effect (simple)
        offset = 3
        corners_3d = [(x + offset, y - offset) for x, y in corners]
        pygame.draw.lines(self.screen, (100, 70, 30), True, corners_3d, 1)

    def _draw_ui(self):
        """Draw UI elements."""
        # UI background
        pygame.draw.rect(
            self.screen,
            COLOR_UI_BG,
            (0, 0, SCREEN_WIDTH, UI_HEIGHT)
        )

        # Score
        score_text = self.title_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 25))

        # Stability indicator
        is_stable, tilt = self.physics.check_stability()
        stability_color = (100, 255, 100) if is_stable else (255, 100, 100)
        stability_text = self.font.render(
            f"Stability: {int(self.physics.stability_score * 100)}%",
            True,
            stability_color
        )
        self.screen.blit(stability_text, (SCREEN_WIDTH - 180, 28))

        # Instructions
        if self.selected_block:
            inst_text = self.font.render(
                "Drag to DROP ZONE at top",
                True,
                COLOR_BLOCK_SELECTED
            )
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - 100, 28))

    def _draw_centered_message(self, message: str, color: Tuple[int, int, int],
                               offset: int = 0):
        """Draw a centered message."""
        text = self.title_font.render(message, True, color)
        rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset)
        )
        self.screen.blit(text, rect)

    def step_ai(self, action: Tuple[int, float, float]) -> Tuple[dict, float, bool]:
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: (block_index, target_x, target_y)

        Returns:
            (observation, reward, done)
        """
        if self.game_state != "playing":
            return self.get_observation(), 0, True

        block_idx, target_x, target_y = action

        reward = 0

        # Select block
        if 0 <= block_idx < len(self.tower.blocks):
            block = self.tower.blocks[block_idx]
            if self.tower.can_select_block(block):
                self.selected_block = block
                block.is_dragging = True
                self.physics.remove_block(block)

                # Move to target
                block.x = target_x * SCREEN_WIDTH
                block.y = target_y * SCREEN_HEIGHT

                # Release
                if self.tower.is_in_drop_zone(block.x, block.y):
                    if self.tower.place_block_on_top(block, block.x):
                        reward += SCORE_PER_BLOCK
                    else:
                        block.is_dragging = False
                        block.is_removed = False
                else:
                    block.is_dragging = False

                self.selected_block = None

        # Update
        self.update()

        # Check rewards
        is_stable, tilt = self.physics.check_stability()
        if is_stable:
            reward += 0.1
        else:
            reward -= 0.5

        if self.physics.collapsed:
            reward += PENALTY_COLLAPSE
            return self.get_observation(), reward, True

        return self.get_observation(), reward, False

    def get_observation(self) -> dict:
        """Get current observation for AI."""
        obs = self.tower.get_observation_data()
        obs["score"] = self.score
        obs["game_state"] = self.game_state

        com_x, com_y = self.physics.calculate_center_of_mass()
        obs["center_of_mass"] = {
            "x": com_x / SCREEN_WIDTH,
            "y": com_y / SCREEN_HEIGHT
        }
        obs["stability_score"] = self.physics.stability_score

        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
