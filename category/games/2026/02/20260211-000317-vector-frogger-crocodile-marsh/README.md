# Vector Frogger - Crocodile Marsh

Navigate a treacherous marsh while dodging crocodiles and snapping turtles in this precision timing challenge.

## Description

Guide your frog from the starting point at the bottom to the goal lilypads at the top. The river is filled with moving obstacles: logs (always safe), turtles (submerge periodically), and crocodiles (safe on back, deadly at mouth). Time your jumps carefully and track turtle dive cycles to reach all five goals.

## Game Details

- **Grid Size**: 20x20 units
- **Time Limit**: 60 seconds per life
- **Lives**: 3
- **Goal**: Fill all 5 lilypads at the top

## Hazards

- Water - instant death if not on an object
- Crocodile Mouth (red area) - instant death
- Submerged Turtles (dark green) - instant death

## Scoring

- Forward step: 10 points
- Goal lilypad reached: 1000 points
- Time bonus: remaining seconds × 10

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the launcher scripts:
- Windows: `run.bat`
- Unix/Mac: `run.sh`

## How to Stop

Press ESC or close the game window.

## Controls

- **Up Arrow**: Move forward
- **Down Arrow**: Move backward
- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space**: Restart after game over/win
- **ESC**: Quit game

## How to Play

1. Start at the bottom safe zone
2. Cross the river by jumping on logs, turtles, or crocodile backs
3. Watch for turtles submerging (turn dark green) - avoid jumping on them
4. On crocodiles, only stand on the green back area - avoid the red mouth on the right
5. Reach a lilypad at the top to score 1000 points
6. Fill all 5 lilypads to win
7. You have 3 lives and 60 seconds per life

## Tips

- Observe turtle dive cycles before committing to a jump
- Crocodile mouths are always on the right side - stay on the left/center
- Logs are the safest platforms - use them when possible
- Moving objects carry you - watch your position to avoid floating off-screen
