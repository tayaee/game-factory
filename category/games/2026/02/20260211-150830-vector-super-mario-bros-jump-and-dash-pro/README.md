# Vector Super Mario Bros Jump and Dash Pro

A precision-focused platformer where dash management and jump timing determine survival.

## Description

Navigate through a procedurally generated world of floating platforms using precise movement mechanics. Master variable-height jumping and strategic dash usage to cross gaps, avoid spike hazards, and collect coins. Your dash meter recharges over time, forcing strategic decisions about when to use bursts of speed for risky platform-to-platform leaps.

## Features

- Variable jump height: Hold longer to jump higher
- Dash system with rechargeable energy meter (up to 3 charges)
- Procedurally generated platforms with increasing difficulty
- Moving platforms and spike hazards
- Coin collection and checkpoint system
- Clean vector-style graphics for optimal visibility

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 main.py
```

Or use the provided scripts:

- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Close the game window or press ESC.

## Controls

- **Left/Right Arrow**: Move horizontally
- **Space**: Jump (hold for higher jumps)
- **Z**: Dash in facing direction
- **ESC**: Quit game
- **Space (when game over)**: Restart

## Rules

- Jump height varies based on how long you hold the jump key
- Dashing consumes a charge from your dash meter
- Dash charges slowly refill over time
- Landing on platforms grants points
- Collecting coins grants bonus points
- Touching spikes or falling off screen ends the run
- Checkpoints save your progress periodically
- Reach the goal flag for victory

## Examples

Time your short hops to land on narrow platforms, then use a dash mid-air to cross large gaps. conserve your dash charges for difficult sections, and use variable jump height to precisely control your landing on moving platforms.

## How to Cleanup

```bash
rm -rf __pycache__ .venv
```
