"""Tower construction and management."""

from typing import List, Optional, Tuple
from config import *
from physics import Block


class Tower:
    """Manages the tower structure."""

    def __init__(self):
        """Initialize an empty tower."""
        self.blocks: List[Block] = []
        self.top_layer = 0
        self.build_tower()

    def build_tower(self):
        """Build the initial tower."""
        self.blocks.clear()

        for layer in range(TOWER_LAYERS):
            horizontal = layer % 2 == 0
            self.add_layer(layer, horizontal)

        self.top_layer = TOWER_LAYERS - 1

    def add_layer(self, layer: int, horizontal: bool):
        """Add a layer to the tower."""
        y = TOWER_BASE_Y - (layer + 0.5) * LAYER_HEIGHT

        if horizontal:
            # Three blocks side by side
            spacing = BLOCK_WIDTH
            for i in range(BLOCKS_PER_LAYER):
                x = TOWER_CENTER_X + (i - 1) * spacing
                block = Block(x, y, layer, i, horizontal=True)
                block.width = BLOCK_WIDTH
                self.blocks.append(block)
        else:
            # Three blocks perpendicular (visual only, all at same x)
            for i in range(BLOCKS_PER_LAYER):
                x = TOWER_CENTER_X
                y_pos = y + (i - 1) * (BLOCK_WIDTH / 3)
                block = Block(x, y_pos, layer, i, horizontal=False)
                block.height = BLOCK_WIDTH
                self.blocks.append(block)

    def get_top_layer_y(self) -> float:
        """Get the Y position of the top layer."""
        return TOWER_BASE_Y - (TOWER_LAYERS + 0.5) * LAYER_HEIGHT

    def get_drop_zone_rect(self) -> Tuple[float, float, float, float]:
        """Get the drop zone rectangle."""
        top_y = self.get_top_layer_y()
        return (
            TOWER_CENTER_X - BLOCK_WIDTH * 2,
            top_y - DROP_ZONE_HEIGHT,
            BLOCK_WIDTH * 4,
            DROP_ZONE_HEIGHT
        )

    def get_block_at(self, x: float, y: float) -> Optional[Block]:
        """Get block at screen position."""
        # Check in reverse order (top blocks first)
        for block in reversed(self.blocks):
            if block.is_removed:
                continue
            if block.contains_point(x, y):
                return block
        return None

    def can_select_block(self, block: Block) -> bool:
        """Check if block can be selected."""
        if block.is_removed or block.is_collapsed:
            return False
        # Cannot select from top layer
        return block.layer < self.top_layer

    def is_in_drop_zone(self, x: float, y: float) -> bool:
        """Check if position is in drop zone."""
        dz_x, dz_y, dz_w, dz_h = self.get_drop_zone_rect()
        return dz_x <= x <= dz_x + dz_w and dz_y <= y <= dz_y + dz_h

    def get_highest_layer_in_drop_zone(self) -> int:
        """Get the highest layer with blocks in drop zone."""
        highest = TOWER_LAYERS - 1
        for block in self.blocks:
            if block.is_removed and self.is_in_drop_zone(block.x, block.y):
                # Calculate approximate layer based on y position
                layer = int((TOWER_BASE_Y - block.y) / LAYER_HEIGHT)
                highest = max(highest, layer)
        return highest

    def place_block_on_top(self, block: Block, x: float) -> bool:
        """Place block on top of tower."""
        highest = self.get_highest_layer_in_drop_zone()
        new_layer = highest + 1

        # Determine orientation for new layer
        horizontal = new_layer % 2 == 0

        # Calculate position based on placement x
        if horizontal:
            # Find the slot (left, center, right)
            rel_x = x - TOWER_CENTER_X
            if rel_x < -BLOCK_WIDTH / 2:
                slot = 0
            elif rel_x > BLOCK_WIDTH / 2:
                slot = 2
            else:
                slot = 1

            target_x = TOWER_CENTER_X + (slot - 1) * BLOCK_WIDTH
        else:
            # Stack in depth (all at same x visually)
            slot = 0
            target_x = TOWER_CENTER_X

        # Check if slot is occupied
        for b in self.blocks:
            if b.is_removed and b.layer == new_layer:
                if abs(b.x - target_x) < BLOCK_WIDTH / 2:
                    return False  # Slot occupied

        # Place the block
        y = TOWER_BASE_Y - (new_layer + 0.5) * LAYER_HEIGHT
        block.x = target_x
        block.y = y
        block.layer = new_layer
        block.position = slot
        block.horizontal = horizontal
        block.is_removed = False
        block.vx = 0
        block.vy = 0
        block.rotation = 0
        block.angular_velocity = 0

        # Update dimensions
        if horizontal:
            block.width = BLOCK_WIDTH
            block.height = BLOCK_HEIGHT
        else:
            block.width = BLOCK_WIDTH
            block.height = BLOCK_HEIGHT

        self.top_layer = new_layer
        return True

    def get_tower_height(self) -> int:
        """Get current tower height in layers."""
        return self.top_layer + 1

    def get_observation_data(self) -> dict:
        """Get tower state for AI observation."""
        blocks_data = []
        for block in self.blocks:
            blocks_data.append({
                "x": block.x / SCREEN_WIDTH,
                "y": block.y / SCREEN_HEIGHT,
                "rotation": block.rotation,
                "layer": block.layer,
                "removed": block.is_removed
            })

        return {
            "blocks": blocks_data,
            "tower_height": self.get_tower_height(),
            "top_layer_y": self.get_top_layer_y() / SCREEN_HEIGHT
        }
