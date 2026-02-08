# Vector Puyo Chain Reaction

Chain matching blobs to create massive explosive combos in this physics-lite puzzle classic.

## Overview

This is a Puyo Puyo-style tile-matching puzzle game where colored blobs fall from the top of a 6x12 grid. Players must strategically place and rotate pairs of blobs to create groups of four or more same-colored blobs, which then disappear and trigger chain reactions.

## How to Play

1. Use **Left/Right Arrow** keys to move the falling pair horizontally
2. Use **Up Arrow** to rotate the pair clockwise
3. Use **Down Arrow** for soft drop (faster fall)
4. Use **Space** for hard drop (instant drop)
5. Press **ESC** to quit
6. Press **R** to restart when game over

### Scoring

- Match 4+ same-colored blobs to score points
- Chain reactions multiply your score exponentially: `10 * 2^chain_length`
- The game gets faster as you create more chains

### Game Over

The game ends if new pairs cannot spawn at the top of the grid.

## Technical Details

- **Grid Size:** 6 columns x 12 rows
- **Colors:** Red, Blue, Green, Yellow
- **FPS:** 60
- **Resolution:** 360x480 (grid) + 120 (sidebar)

## RL Integration

### Observation Space
12x6 grid state with color IDs (0-4), current falling pair position and colors, next pair preview.

### Action Space
- 0: Move Left
- 1: Move Right
- 2: Rotate
- 3: Soft Drop
- 4: Hard Drop

## Installation & Running

```bash
# Install dependencies
uv venv
uv pip install pygame

# Run the game
uv run main.py
```

## Cleanup

```bash
rm -rf .venv
find . -type d -name '__pycache__' -exec rm -rf {} +
```
