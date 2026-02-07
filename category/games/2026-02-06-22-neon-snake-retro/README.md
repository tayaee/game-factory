# Neon Snake Retro

**Category:** Games

**Description:** A classic snake game where you navigate a snake to eat food while avoiding walls and your own body.

## Rationale

Simple and intuitive controls make it enjoyable for all ages, making it the perfect base game project for AI agents to implement and extend logic.

## Details

The game is played on a 20x20 grid. The snake consists of a head and tail segments, moving one cell at a time in the selected direction. Food appears at random locations on the screen. When the snake eats food, it grows by one segment and the score increases. The game ends when the snake's head hits the screen boundary or collides with its own body. Use keyboard arrow keys to change direction (up, down, left, right), but you cannot immediately reverse direction.

## How to Build

This game requires Python 3.8+ and pygame. Install dependencies using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install pygame
```

Or with pip:

```bash
pip install pygame
```

## How to Run

Run the game from the app directory:

```bash
python main.py
```

## Examples

When you start the game, the snake begins moving. You can enjoy the visual pleasure of watching the snake grow as it eats food. The final score allows you to compete against your own records.

## Controls

- **Arrow Keys**: Change direction (Up, Down, Left, Right)
- **Space/Enter**: Start game / Restart after game over
- **Q / Esc**: Quit game

## Features

- Neon retro visual style with glow effects
- Real-time score and length tracking
- Smooth 60 FPS rendering
- Pulsing food animation
- Gradient snake body color based on segment position
- Grid-based movement (150ms intervals)
- Start screen and game over overlay
