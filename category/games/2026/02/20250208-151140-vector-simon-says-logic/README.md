# Vector Simon Says Logic

**Category:** Games

**Description:** Master your memory with a high-speed, logic-driven sequence challenge.

## Rationale

Memory games provide a clear baseline for AI agent training in sequential data processing and pattern recognition. This app targets puzzle enthusiasts and developers looking for a clean, logic-heavy environment for reinforcement learning.

## Details

The game features a 2x2 grid of distinct colored panels: Red (Top-Left), Blue (Top-Right), Green (Bottom-Left), and Yellow (Bottom-Right). The game begins by flashing a sequence of colors. The user or agent must replicate the sequence exactly. Each round, the sequence length increases by one. If a wrong panel is selected, the game resets.

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

## Controls

- **Q** - Red panel (Top-Left)
- **W** - Blue panel (Top-Right)
- **A** - Green panel (Bottom-Left)
- **S** - Yellow panel (Bottom-Right)
- **Mouse** - Click panels directly
- **SPACE** - Start game / Restart after game over
- **ESC** - Quit

## How to Play

1. Press SPACE to start the game
2. Watch the sequence of flashing colors
3. Repeat the sequence by clicking panels or using keyboard keys
4. Each successful round adds one more color to remember
5. Score increases by 10 points for each completed round
6. You have 3 seconds to input the sequence
7. Game ends if you press the wrong panel

## AI Integration

AI agents can interact with the game through the `Game` class:

### Reward Structure

- Correct input: +10
- Round complete: +20
- Wrong input: -10 (game over)

### Observation Space

```python
{
    "sequence": [int, ...],         # The sequence to replicate (0-3 for panels)
    "sequence_length": int,         # Current sequence length
    "player_progress": int,         # How many inputs player has made
    "state": str,                   # Current game state
    "lit_panel": int,              # Currently lit panel (-1 if none)
    "score": int,
    "round": int
}
```

### Action Space

- 0: Red panel
- 1: Blue panel
- 2: Green panel
- 3: Yellow panel

```python
# Example AI interaction
game = Game()
obs, reward, done = game.step_ai(action)  # action: 0-3
```

## How to Stop

Press ESC key or close the game window. For automation:

```bash
pkill -f main.py
```

## How to Cleanup

```bash
rm -rf .venv && rm uv.lock
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Resolution:** 800x700
- **Input:** Keyboard (Q,W,A,S), Mouse, or Action space (for AI)
