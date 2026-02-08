# Vector Memory Pattern Match

**Category:** Games

**Description:** Test your brain's limits by remembering and perfectly reproducing increasingly long light patterns.

## Rationale

A modern reinterpretation of the classic Simon game using vector graphics. Simple rules make it accessible to all ages, while providing an optimized environment for AI agents to test sequence learning and state maintenance capabilities.

## Details

The game screen consists of four square tiles, each with a different color and tone. The system randomly adds tiles one at a time to show a sequence, and the player must click the tiles in the same order. The sequence grows by one tile each round.

Built using Python's Pygame library, featuring tile glow effects and sound feedback. The game ends immediately when an incorrect tile is pressed.

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Run

```bash
uv run main.py
```

## Controls

- **Mouse Left Click**: Click tiles to repeat the pattern
- **Spacebar**: Start new game / Restart after game over
- **Escape**: Quit the game

## Features

- Progressive difficulty with growing sequences
- Visual glow effects on tile activation
- Procedurally generated sound feedback
- Score tracking
- AI-friendly observation interface for reinforcement learning

## AI Integration

AI agents can interact with the game through the `GameBoard` class:

- `get_observation()`: Returns current game state including sequence, player position, and tile states
- `step_ai(action)`: Execute an action (0-3 for tile selection) and receive (observation, reward, done)
- `get_valid_actions()`: Returns list of valid actions [0, 1, 2, 3]

### Reward Structure

- Correct step: +0.1
- Round complete: +1.0
- Game over: -1.0

### Observation Space

```python
{
    "sequence": [0, 2, 1, ...],     # Current pattern to match
    "player_index": 2,               # Current position in sequence
    "score": 5,                      # Current score
    "game_state": "playing",         # Current game state
    "tiles_lit": [False, True, ...]  # Which tiles are currently lit
}
```

## How to Stop

Send SIGINT (Ctrl+C) to the process or close the game window.

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Resolution:** 800x600
- **Input:** Mouse click / Sequence data (for AI)
