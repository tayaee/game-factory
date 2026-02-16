# Pattern Match

A memory puzzle game where you memorize and recreate patterns on a grid of colored symbols.

## Description

Train your visual memory by watching a pattern light up, then clicking the correct cells to recreate it. As levels progress, patterns become longer and more challenging.

## Rationale

Memory training games are excellent for cognitive health and can help improve:
- Visual-spatial working memory
- Pattern recognition skills
- Focus and concentration
- Reaction time

This game is perfect for:
- Quick mental breaks during work
- Brain training enthusiasts
- Anyone wanting to exercise their memory
- Players of all ages

## Details

The game displays a 4x4 grid of colored symbols (circles, squares, triangles, diamonds). Each level:
1. A pattern is highlighted on the grid for a few seconds
2. The highlighting disappears
3. You must click the cells that were highlighted
4. Correct answers advance to the next level with longer patterns
5. Wrong answers cost a life
6. Game ends when all 3 lives are lost

Scoring:
- Points = Level x 100 per correct pattern
- Higher levels = more points but harder patterns

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the scripts:
- Windows: `run.bat`
- Linux/Mac: `chmod +x run.sh && ./run.sh`

## How to Stop

Press ESC or close the game window.

## How to Play

**Controls:**
- Mouse Left Click: Select/deselect grid cells
- SPACE: Start game / Restart after game over
- ESC: Quit game

**Scoring:**
- Correctly recreate the highlighted pattern to advance
- Each correct pattern gives Level x 100 points
- Wrong pattern selection costs 1 life
- 3 lives total per game

**Strategy:**
- Focus on the positions, not the symbols (symbols are decorative)
- Use verbal or spatial memory techniques (e.g., "top-left to bottom-right diagonal")
- Stay calm - you have 3 seconds to memorize each pattern

## Technical Specifications

- Language: Python 3.12+
- Framework: pygame-ce 2.5.0+
- Screen: 600x700 pixels
- Grid: 4x4 cells

## AI Integration

For reinforcement learning training:

**Observation Space:**
- 4x4x6 tensor (grid x colors)
- Additional scalar for game state (0: menu, 1: showing, 2: playing, 3: gameover)
- Pattern countdown timer value

**Action Space:**
- Discrete 17 actions: 16 cells + wait/no-op
- Or use 16-action binary mask for cell selection

**Reward Function:**
- +100 * level: Correct pattern
- -50: Wrong pattern
- -1 per time step (encourage speed)

**State Representation:**
```python
observation = {
    'grid': 4x4x6 one-hot color encoding,
    'highlighted': 4x4 binary mask,
    'selected': 4x4 binary mask,
    'timer': pattern_countdown_timer,
    'level': current_level,
    'lives': remaining_lives
}
```

## How to Cleanup

```bash
# Remove virtual environment
rm -rf .venv

# Remove uv lock file
rm uv.lock
```
