"""Game entities for Vector Hextris."""

import math
import pygame
from config import (
    HEXAGON_RADIUS,
    HEXAGON_SIDES,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
    BLOCKS_PER_ROW,
    BLOCK_COLORS,
)


class Block:
    """A single colored block in the game."""

    def __init__(self, color_index, side_index, position_on_side):
        self.color_index = color_index
        self.side_index = side_index
        self.position_on_side = position_on_side
        self.color = BLOCK_COLORS[color_index]
        self.marked_for_clear = False


class FallingBar:
    """A falling bar consisting of multiple blocks."""

    def __init__(self, side_index, color_index):
        self.side_index = side_index
        self.color_index = color_index
        self.distance = 350  # Starting distance from center
        self.blocks = []
        # Create blocks for the bar
        for i in range(BLOCKS_PER_ROW):
            offset = (i - BLOCKS_PER_ROW // 2) * (BLOCK_WIDTH + 2)
            self.blocks.append({
                'color_index': color_index,
                'offset': offset,
                'width': BLOCK_WIDTH,
                'height': BLOCK_HEIGHT
            })


class Hexagon:
    """The central hexagon that holds stacked blocks."""

    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.rotation = 0  # Current rotation in degrees
        self.sides = [[] for _ in range(HEXAGON_SIDES)]  # Each side holds blocks

    def rotate(self, direction):
        """Rotate the hexagon. Direction: -1 for left, 1 for right."""
        self.rotation = (self.rotation + direction * 60) % 360

    def add_block_to_side(self, side_index, block):
        """Add a block to the specified side."""
        self.sides[side_index].append(block)

    def get_side_vertices(self, side_index):
        """Get the vertices for a specific side of the hexagon."""
        angle_start = math.radians(self.rotation + side_index * 60 - 30)
        angle_end = math.radians(self.rotation + (side_index + 1) * 60 - 30)

        x1 = self.center_x + HEXAGON_RADIUS * math.cos(angle_start)
        y1 = self.center_y + HEXAGON_RADIUS * math.sin(angle_start)
        x2 = self.center_x + HEXAGON_RADIUS * math.cos(angle_end)
        y2 = self.center_y + HEXAGON_RADIUS * math.sin(angle_end)

        return (x1, y1), (x2, y2)

    def get_side_normal(self, side_index):
        """Get the normal vector (pointing inward) for a side."""
        angle = math.radians(self.rotation + side_index * 60)
        return math.cos(angle), math.sin(angle)

    def get_side_center(self, side_index):
        """Get the center point of a side."""
        (x1, y1), (x2, y2) = self.get_side_vertices(side_index)
        return (x1 + x2) / 2, (y1 + y2) / 2

    def get_hexagon_vertices(self):
        """Get all vertices of the hexagon for drawing."""
        vertices = []
        for i in range(HEXAGON_SIDES):
            angle = math.radians(self.rotation + i * 60 - 30)
            x = self.center_x + HEXAGON_RADIUS * math.cos(angle)
            y = self.center_y + HEXAGON_RADIUS * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def check_matches(self):
        """Check for matching blocks on all sides and return matches found."""
        matches = []

        # Check each side for consecutive blocks of same color
        for side_idx, blocks in enumerate(self.sides):
            if len(blocks) < 3:
                continue

            # Check for runs of same color
            i = 0
            while i < len(blocks):
                color = blocks[i].color_index
                count = 1
                j = i + 1

                while j < len(blocks) and blocks[j].color_index == color:
                    count += 1
                    j += 1

                if count >= 3:
                    match_blocks = []
                    for k in range(i, j):
                        match_blocks.append((side_idx, k))
                    matches.append(match_blocks)

                i = j

        return matches

    def get_max_stack_height(self):
        """Get the maximum stack height across all sides."""
        return max(len(side) for side in self.sides)
