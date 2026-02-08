"""Game board logic and state management."""

import random
import array
from config import TILE_COLORS, FLASH_COLORS, TONE_FREQUENCIES


class Tile:
    """Represents a single tile in the game."""

    def __init__(self, index, x, y, size):
        self.index = index
        self.rect = [x, y, size, size]
        self.base_color = TILE_COLORS[index]
        self.flash_color = FLASH_COLORS[index]
        self.frequency = TONE_FREQUENCIES[index]
        self.is_lit = False
        self.flash_timer = 0


class GameBoard:
    """Manages game logic, state, and tiles."""

    def __init__(self, board_x, board_y, tile_size, gap):
        self.tiles = []
        self.sequence = []
        self.player_index = 0
        self.score = 0
        self.game_state = "ready"  # ready, playing, showing_sequence, game_over
        self.flash_queue = []
        self.flash_timer = 0
        self.between_flashes_timer = 0
        self.last_reward = 0.0

        # Calculate tile positions
        # Top-left: index 0
        self.tiles.append(Tile(0, board_x, board_y, tile_size))
        # Top-right: index 1
        self.tiles.append(Tile(1, board_x + tile_size + gap, board_y, tile_size))
        # Bottom-left: index 2
        self.tiles.append(Tile(2, board_x, board_y + tile_size + gap, tile_size))
        # Bottom-right: index 3
        self.tiles.append(Tile(3, board_x + tile_size + gap, board_y + tile_size + gap, tile_size))

    def start_new_round(self):
        """Start a new round by adding a new tile to the sequence."""
        new_tile = random.randint(0, 3)
        self.sequence.append(new_tile)
        self.player_index = 0
        self.game_state = "showing_sequence"
        self.flash_queue = self.sequence.copy()
        self.between_flashes_timer = 0

    def reset_game(self):
        """Reset the game to initial state."""
        self.sequence = []
        self.player_index = 0
        self.score = 0
        self.game_state = "ready"
        self.flash_queue = []
        self.last_reward = 0.0

    def handle_tile_click(self, pos):
        """Handle a click on a tile. Returns reward for AI training."""
        if self.game_state != "playing" or not self.sequence:
            return 0.0

        for tile in self.tiles:
            if self._point_in_rect(pos, tile.rect):
                correct_tile = self.sequence[self.player_index]

                if tile.index == correct_tile:
                    # Correct click
                    self.player_index += 1
                    tile.is_lit = True
                    tile.flash_timer = 10  # Short flash for player input

                    if self.player_index >= len(self.sequence):
                        # Round complete
                        self.score += 1
                        self.last_reward = 1.0
                        self.game_state = "showing_sequence"
                        self.flash_queue = self.sequence.copy()
                        self.between_flashes_timer = 0
                        return 1.0
                    else:
                        self.last_reward = 0.1
                        return 0.1
                else:
                    # Wrong tile - game over
                    self.game_state = "game_over"
                    self.last_reward = -1.0
                    tile.is_lit = True
                    tile.flash_timer = 30  # Longer flash to show error
                    return -1.0

        return 0.0

    def update(self):
        """Update game state."""
        # Update tile flash timers
        for tile in self.tiles:
            if tile.flash_timer > 0:
                tile.flash_timer -= 1
                if tile.flash_timer <= 0:
                    tile.is_lit = False

        # Handle sequence showing
        if self.game_state == "showing_sequence":
            if self.between_flashes_timer > 0:
                self.between_flashes_timer -= 1
            elif self.flash_queue:
                tile_index = self.flash_queue.pop(0)
                self.tiles[tile_index].is_lit = True
                self.tiles[tile_index].flash_timer = 18  # Flash duration
                self.between_flashes_timer = 6  # Pause between flashes
            else:
                # Sequence complete, player's turn
                self.game_state = "playing"

    def get_observation(self):
        """Get current observation for AI agents."""
        return {
            "sequence": self.sequence.copy(),
            "player_index": self.player_index,
            "score": self.score,
            "game_state": self.game_state,
            "tiles_lit": [tile.is_lit for tile in self.tiles]
        }

    def get_valid_actions(self):
        """Get list of valid actions (tile indices 0-3)."""
        return [0, 1, 2, 3]

    def step_ai(self, action):
        """Step the game forward with an AI action."""
        if self.game_state == "ready":
            self.start_new_round()
            return self.get_observation(), 0.0, False

        reward = self.handle_tile_click((0, 0))  # Position doesn't matter for AI
        # Directly set the clicked tile
        if 0 <= action <= 3 and self.game_state == "playing":
            self.tiles[action].is_lit = True
            self.tiles[action].flash_timer = 10

        done = self.game_state == "game_over"
        return self.get_observation(), reward, done

    def _point_in_rect(self, point, rect):
        """Check if a point is inside a rectangle."""
        x, y = point
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh
