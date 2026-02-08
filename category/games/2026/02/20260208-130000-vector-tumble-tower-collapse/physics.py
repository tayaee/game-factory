"""Physics simulation for block tower."""

import math
from typing import List, Tuple, Optional
from config import *


class Block:
    """Represents a single tower block with physics properties."""

    def __init__(self, x: float, y: float, layer: int, position: int,
                 horizontal: bool = True):
        """
        Initialize a block.

        Args:
            x: Center X position
            y: Center Y position
            layer: Tower layer (0 = bottom)
            position: Position within layer (0, 1, 2)
            horizontal: True if block is horizontal
        """
        self.x = x
        self.y = y
        self.layer = layer
        self.position = position
        self.horizontal = horizontal
        self.rotation = 0.0  # In radians

        self.vx = 0.0
        self.vy = 0.0
        self.angular_velocity = 0.0

        self.is_dragging = False
        self.is_removed = False
        self.is_collapsed = False

        # Calculate dimensions based on orientation
        if self.horizontal:
            self.width = BLOCK_WIDTH * 3
            self.height = BLOCK_HEIGHT
        else:
            self.width = BLOCK_WIDTH
            self.height = BLOCK_HEIGHT

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Get bounding box (left, top, width, height)."""
        return (self.x - self.width / 2,
                self.y - self.height / 2,
                self.width, self.height)

    def get_corners(self) -> List[Tuple[float, float]]:
        """Get the four corners of the rotated block."""
        cos_a = math.cos(self.rotation)
        sin_a = math.sin(self.rotation)

        hw = self.width / 2
        hh = self.height / 2

        corners = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
        ]

        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + self.x
            ry = cx * sin_a + cy * cos_a + self.y
            rotated.append((rx, ry))

        return rotated

    def contains_point(self, px: float, py: float) -> bool:
        """Check if point is inside the block (accounting for rotation)."""
        # Transform point to local coordinates
        cos_a = math.cos(-self.rotation)
        sin_a = math.sin(-self.rotation)

        dx = px - self.x
        dy = py - self.y

        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a

        return (abs(local_x) <= self.width / 2 and
                abs(local_y) <= self.height / 2)

    def update(self, dt: float):
        """Update physics for non-dragging blocks."""
        if self.is_dragging or self.is_removed:
            return

        # Apply gravity
        self.vy += GRAVITY * dt

        # Apply friction
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.angular_velocity *= FRICTION

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.angular_velocity * dt

        # Ground collision
        if self.y + self.height / 2 > GROUND_Y:
            self.y = GROUND_Y - self.height / 2
            self.vy *= -RESTITUTION
            self.vx *= FRICTION
            if abs(self.vy) < 10:
                self.vy = 0


class PhysicsEngine:
    """Manages physics simulation for the tower."""

    def __init__(self):
        """Initialize the physics engine."""
        self.blocks: List[Block] = []
        self.collapsed = False
        self.stability_score = 1.0

    def add_block(self, block: Block):
        """Add a block to the simulation."""
        self.blocks.append(block)

    def remove_block(self, block: Block):
        """Remove a block from tower (being moved by player)."""
        if block in self.blocks:
            block.is_removed = True

    def calculate_center_of_mass(self) -> Tuple[float, float]:
        """Calculate the center of mass of all non-removed blocks."""
        total_mass = 0.0
        weighted_x = 0.0
        weighted_y = 0.0

        for block in self.blocks:
            if not block.is_removed:
                weighted_x += block.x * BLOCK_MASS
                weighted_y += block.y * BLOCK_MASS
                total_mass += BLOCK_MASS

        if total_mass == 0:
            return TOWER_CENTER_X, TOWER_BASE_Y

        return weighted_x / total_mass, weighted_y / total_mass

    def calculate_tilt(self) -> float:
        """Calculate tower tilt angle based on center of mass offset."""
        com_x, com_y = self.calculate_center_of_mass()

        # Find base blocks (layer 0, not removed)
        base_blocks = [b for b in self.blocks if b.layer == 0 and not b.is_removed]
        if not base_blocks:
            return 0.0

        # Calculate base center
        base_x = sum(b.x for b in base_blocks) / len(base_blocks)

        # Tilt is proportional to offset from base
        offset = com_x - base_x
        return abs(offset) / TOWER_CENTER_X

    def check_stability(self) -> Tuple[bool, float]:
        """Check if tower is stable."""
        tilt = self.calculate_tilt()
        self.stability_score = max(0.0, 1.0 - tilt / COLLAPSE_THRESHOLD)
        is_stable = tilt < STABILITY_THRESHOLD
        return is_stable, tilt

    def check_collapse(self) -> bool:
        """Check if tower has collapsed."""
        if self.collapsed:
            return True

        # Check for blocks touching ground (except during drag)
        for block in self.blocks:
            if block.is_removed or block.is_dragging:
                continue
            if block.layer > 0:  # Not base layer
                if block.y + block.height / 2 >= GROUND_Y - 5:
                    self.collapsed = True
                    block.is_collapsed = True
                    return True

        # Check tilt threshold
        _, tilt = self.check_stability()
        if tilt >= COLLAPSE_THRESHOLD:
            self.collapsed = True
            return True

        return False

    def apply_block_support(self, dt: float):
        """Apply support forces from blocks below."""
        for block in self.blocks:
            if block.is_dragging or block.is_removed:
                continue

            # Find blocks below that could support this one
            supporting = []
            for other in self.blocks:
                if other is block or other.is_removed or other.is_dragging:
                    continue

                # Check if other is below this block
                if other.y > block.y:
                    continue

                # Check vertical proximity
                vertical_dist = block.y - other.y
                if vertical_dist > BLOCK_HEIGHT * 1.5:
                    continue

                # Check horizontal overlap
                dx = abs(block.x - other.x)
                if dx < (block.width + other.width) / 2:
                    supporting.append((other, vertical_dist))

            if supporting:
                # Apply support force
                block.vy *= 0.9  # Damping
                for support, dist in supporting:
                    if dist < BLOCK_HEIGHT * 1.2:
                        # Direct contact support
                        if block.y - support.y < BLOCK_HEIGHT:
                            block.y = support.y - BLOCK_HEIGHT
                            block.vy = 0

    def resolve_overlaps(self):
        """Resolve block overlaps."""
        for i, block_a in enumerate(self.blocks):
            if block_a.is_dragging or block_a.is_removed:
                continue

            for block_b in self.blocks[i + 1:]:
                if block_b.is_dragging or block_b.is_removed:
                    continue

                # Simple AABB check
                a_rect = block_a.get_rect()
                b_rect = block_b.get_rect()

                if (a_rect[0] < b_rect[0] + b_rect[2] and
                    a_rect[0] + a_rect[2] > b_rect[0] and
                    a_rect[1] < b_rect[1] + b_rect[3] and
                    a_rect[1] + a_rect[3] > b_rect[1]):

                    # Calculate overlap
                    overlap_x = min(a_rect[0] + a_rect[2] - b_rect[0],
                                    b_rect[0] + b_rect[2] - a_rect[0])
                    overlap_y = min(a_rect[1] + a_rect[3] - b_rect[1],
                                    b_rect[1] + b_rect[3] - a_rect[1])

                    # Separate along smallest axis
                    if overlap_x < overlap_y:
                        if block_a.x < block_b.x:
                            block_a.x -= overlap_x / 2
                            block_b.x += overlap_x / 2
                        else:
                            block_a.x += overlap_x / 2
                            block_b.x -= overlap_x / 2
                    else:
                        if block_a.y < block_b.y:
                            block_a.y -= overlap_y / 2
                            block_b.y += overlap_y / 2
                        else:
                            block_a.y += overlap_y / 2
                            block_b.y -= overlap_y / 2

    def update(self, dt: float):
        """Update physics simulation."""
        if self.collapsed:
            # Apply gravity to all blocks
            for block in self.blocks:
                if not block.is_dragging:
                    block.vy += GRAVITY * dt
                    block.x += block.vx * dt
                    block.y += block.vy * dt
                    block.rotation += block.angular_velocity * dt

                    # Ground collision
                    if block.y + block.height / 2 > GROUND_Y:
                        block.y = GROUND_Y - block.height / 2
                        block.vy *= -0.3
                        block.vx *= 0.8
                        block.angular_velocity *= 0.8
                        if abs(block.vy) < 5:
                            block.vy = 0
            return

        # Apply support forces
        self.apply_block_support(dt)

        # Update individual blocks
        for block in self.blocks:
            block.update(dt)

        # Resolve overlaps
        self.resolve_overlaps()

        # Check for collapse
        self.check_collapse()
