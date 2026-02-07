# Color Flood Puzzle

**Category:** Games

**Description:** An addictive strategy puzzle game to unify all tiles to one color in minimum moves.

## Rationale

Simple rules make it accessible to everyone, while challenging players to find optimal paths within limited moves, stimulating logical thinking skills.

## Details

The game is played on a 12x12 or 16x16 grid board with randomly colored tiles. Starting from the top-left (0,0) tile, players select one of the color buttons at the bottom. When a color is selected, all adjacent tiles of that color connected to the player's current territory change to the selected color, expanding the flooded area. The goal is to fill the entire board with one color within the maximum number of turns. Score is calculated based on remaining moves when completed.

## How to Build

This game is a pure web application using HTML5, CSS3, and JavaScript. No build process required. Simply open the index.html file in a web browser.

Optionally, you can run a local web server for better development experience:

```bash
# Using Python
python -m http.server 8000

# Using Node.js live-server (requires npm install -g live-server)
live-server

# Using uv to serve static files
uv run --with python http.server
```

## How to Run

**Option 1: Direct Browser Access**
Simply open the `index.html` file in any modern web browser (Chrome, Firefox, Safari, Edge).

**Option 2: Python Launcher**
Use the provided Python launcher to start a local web server:
```bash
python main.py
```
The game will automatically open in your default browser.

**Option 3: Manual Web Server**
Alternatively, if using a local web server manually, navigate to:
```
http://localhost:8000
```

## Examples

When you start the game, a colorful board appears. Click the blue button and watch as blue tiles adjacent to your starting position merge into your territory. Strategically choose colors to unify the entire board to yellow within 22 moves for a satisfying victory!

## Controls

- **Color Buttons**: Select a color to flood your territory
- **New Game Button**: Start a fresh game
- **Board Size Button**: Toggle between 12x12 (22 moves) and 16x16 (30 moves)

## Features

- Two board sizes: 12x12 (casual) and 16x16 (challenging)
- Six vibrant, accessible colors
- Move counter and maximum moves display
- Score calculation with bonuses for efficiency
- Smooth animations for tile flooding
- Responsive design for mobile and desktop
- Win/lose detection with overlay messages
- Clean, modern UI with gradient backgrounds
- No server required - runs entirely in browser
