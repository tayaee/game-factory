"""Level management for map tiles and collision."""

import pygame
from config import *


class Level:
    """Manages the game map and tile-based collision."""

    def __init__(self):
        """Initialize level with default map."""
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.tiles = [[TILE_AIR for _ in range(self.height)] for _ in range(self.width)]
        self.entry_pos = (5, 5)
        self.exit_pos = (self.width - 5, self.height - 10)
        self.load_default_level()

    def load_default_level(self):
        """Create the default level layout."""
        # Clear map
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x][y] = TILE_AIR

        # Create ground at bottom
        for x in range(self.width):
            for y in range(self.height - 3, self.height):
                self.tiles[x][y] = TILE_GROUND

        # Create a platform at entry level
        for x in range(2, 15):
            self.tiles[x][10] = TILE_GROUND

        # Set entry point
        self.entry_pos = (3, 9)
        self.tiles[self.entry_pos[0]][self.entry_pos[1]] = TILE_ENTRY

        # Create middle obstacles requiring bridge building
        # A gap that needs bridging
        for y in range(15, 25):
            self.tiles[18][y] = TILE_GROUND
            self.tiles[19][y] = TILE_GROUND

        # Platform after the gap
        for x in range(20, 30):
            self.tiles[x][25] = TILE_GROUND

        # Vertical wall requiring bashing
        for y in range(20, 28):
            self.tiles[30][y] = TILE_GROUND

        # Platform before exit
        for x in range(31, self.width - 5):
            self.tiles[x][28] = TILE_GROUND

        # Create exit
        self.exit_pos = (self.width - 8, 27)
        for ex in range(self.exit_pos[0], self.exit_pos[0] + 3):
            for ey in range(self.exit_pos[1], self.exit_pos[1] + 2):
                self.tiles[ex][ey] = TILE_EXIT

        # Add some hazards (pits)
        for x in range(25, 28):
            self.tiles[x][self.height - 1] = TILE_HAZARD

    def get_tile(self, x, y):
        """Get tile at grid position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return TILE_GROUND  # Out of bounds is solid

    def set_tile(self, x, y, tile_type):
        """Set tile at grid position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[x][y] = tile_type

    def is_solid(self, x, y):
        """Check if tile at position is solid."""
        tile = self.get_tile(x, y)
        return tile in (TILE_GROUND, TILE_BRIDGE)

    def is_hazard(self, x, y):
        """Check if tile at position is a hazard."""
        return self.get_tile(x, y) == TILE_HAZARD

    def is_exit(self, x, y):
        """Check if tile at position is the exit."""
        return self.get_tile(x, y) == TILE_EXIT

    def remove_tile(self, x, y):
        """Remove a tile (bash through it)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.tiles[x][y] == TILE_GROUND:
                self.tiles[x][y] = TILE_AIR
                return True
        return False

    def build_bridge(self, start_x, start_y, direction):
        """Build a diagonal bridge starting from position."""
        bridge_tiles = []
        for i in range(BRIDGE_LENGTH):
            # Calculate bridge position (rises 5 units over 10 horizontal)
            bx = start_x + i * direction
            by = start_y - (i * BRIDGE_HEIGHT) // BRIDGE_LENGTH

            if 0 <= bx < self.width and 0 <= by < self.height:
                if self.tiles[bx][by] == TILE_AIR:
                    self.tiles[bx][by] = TILE_BRIDGE
                    bridge_tiles.append((bx, by))
                else:
                    break  # Hit something
            else:
                break
        return bridge_tiles

    def get_entry_pixel_pos(self):
        """Get entry position in pixels."""
        return (self.entry_pos[0] * TILE_SIZE, self.entry_pos[1] * TILE_SIZE)

    def get_exit_rect(self):
        """Get exit area as a rect in pixels."""
        return pygame.Rect(
            self.exit_pos[0] * TILE_SIZE,
            self.exit_pos[1] * TILE_SIZE,
            3 * TILE_SIZE,
            2 * TILE_SIZE
        )

    def pixel_to_grid(self, px, py):
        """Convert pixel coordinates to grid coordinates."""
        return int(px // TILE_SIZE), int(py // TILE_SIZE)

    def grid_to_pixel(self, gx, gy):
        """Convert grid coordinates to pixel coordinates."""
        return gx * TILE_SIZE, gy * TILE_SIZE

    def draw(self, surface):
        """Draw the level to a surface."""
        surface.fill(SKY_BLUE)

        for x in range(self.width):
            for y in range(self.height):
                tile = self.tiles[x][y]
                if tile == TILE_AIR:
                    continue

                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                if tile == TILE_GROUND:
                    pygame.draw.rect(surface, GROUND_BROWN, rect)
                    pygame.draw.rect(surface, (100, 60, 30), rect, 1)
                elif tile == TILE_BRIDGE:
                    pygame.draw.rect(surface, (139, 100, 60), rect)
                    pygame.draw.line(
                        surface,
                        (100, 70, 40),
                        rect.topleft,
                        rect.bottomright,
                        2
                    )
                elif tile == TILE_EXIT:
                    pygame.draw.rect(surface, EXIT_PURPLE, rect)
                    # Draw portal effect
                    center = rect.center
                    pygame.draw.circle(surface, WHITE, center, 4, 1)
                elif tile == TILE_HAZARD:
                    pygame.draw.rect(surface, HAZARD_RED, rect)
                    # Draw X pattern
                    pygame.draw.line(surface, BLACK, rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(surface, BLACK, rect.topright, rect.bottomleft, 2)
                elif tile == TILE_ENTRY:
                    pygame.draw.rect(surface, GOLD, rect)
                    pygame.draw.circle(surface, WHITE, rect.center, 3)
