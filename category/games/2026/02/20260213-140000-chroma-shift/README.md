# Chroma Shift

Match colors before they shift in this minimalist color perception puzzle.

## Description

A grid of colored tiles appears at the center of the screen. Each tile slowly shifts its hue over time, creating a continuously changing color palette. The player must click tiles that match the target color shown at the top of the screen. As the game progresses, colors shift faster and the matching tolerance becomes tighter.

## Rationale

This game tests color perception, pattern recognition, and reaction speed under time pressure. The continuously shifting colors challenge players to make quick visual classification decisions. It targets players interested in cognitive training and reflex improvement, as well as AI agents learning to process visual color information with time-sensitive decision making.

## Details

The game area is an 800x700 window with a 4x4 grid of colored tiles.

**Core Mechanics:**
- Target color displayed as a banner at the top
- Each tile's hue continuously shifts over time
- Tiles that match the target are highlighted with a white border
- Click matching tiles to score points
- Matching tiles are replaced with new random colors
- A new target color is selected after each successful match

**Scoring:**
- Base 10 points per correct match
- Combo multiplier increases with consecutive matches
- Wrong clicks or empty-space clicks reduce lives
- 3 lives total

**Difficulty Progression:**
- Color shift speed increases every 50 points
- Match tolerance decreases as game progresses
- Combo resets on any mistake

**Game Over:**
- Game ends when lives reach zero
- Final score displayed
- Press R to restart, ESC to quit

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

Match the target color by clicking tiles before they drift too far.

**Controls:**
- **Mouse Left Click** - Click tile
- **ESC** - Quit game
- **R** - Restart (when game over)

**Strategy:**
- Watch for white-bordered tiles that match the target
- Click quickly before colors shift away from target
- Build combos by making consecutive correct matches
- Avoid clicking empty space or wrong colors

## AI Agent Input

For RL agent control:

**Observation Space:**
- 800x700 pixel array or normalized state:
  - Grid of tile hues (4x4 values 0-1)
  - Target hue (single value 0-1)
  - Current score
  - Lives remaining
  - Combo count
  - Shift speed
  - Match tolerance

**Action Space:**
- Discrete: [CLICK_TILE_0, CLICK_TILE_1, ..., CLICK_TILE_15]
- Or Continuous: (x, y) click position

**Reward Structure:**
- +10 for correct base match
- +(combo * 5) additional points for combo
- -5 for wrong tile click
- -5 for empty space click
- Game ends at 0 lives

**Optimal Strategy:**
Prioritize tiles currently matching the target (white border). Track hue shift direction to predict which tiles will become matches next. Maintain combo by avoiding mistakes.

## Project Structure

```
category/games/2026/02/20260213-140000-chroma-shift/
├── main.py          - Entry point and game logic
├── pyproject.toml   - Dependencies
├── appinfo.json     - App metadata
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x700
- **Frame Rate**: 60 FPS
- **Input Type**: Mouse (click)
- **Language**: Python 3.12+
- **Library**: pygame-ce
- **Grid Size**: 4x4 tiles
