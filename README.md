# Mach Ten Project Artifacts

Can we break the speed of Mach 10? Let’s find out. This repo challenges the limits of 1000x productivity in software engineering. This repo is updated by AI agents. I (as a human, the repo owner) have intentionally throttled the speed to 1/1000th.

## Apps

### Games

* 2026-02-07 | [Polar Bear Ice Bridge](category/games/2026/02/1738933488-polar-bear-ice-bridge/) | Timing-based physics puzzle where you build bridges to help a polar bear cross ice floes.
* 2026-02-07 | [Ocean Cleanup Bubble Pop](category/games/2026/02/1738918819-ocean-cleanup-bubble-pop/) | Trap ocean trash in bubbles to purify the sea in this addictive puzzle arcade game.
* 2026-02-07 | [Binary Crossroad Traffic Control](category/games/2026/02/1738918960-binary-crossroad-traffic-control/) | Manage traffic signals at an intersection to pass vehicles without accidents.
* 2026-02-07 | [Lunar Lander Physics Lite](category/games/2026/02/1738891527-lunar-lander-physics-lite/) | Guide your lander to a safe landing on the lunar surface with gravity physics.
* 2026-02-07 | [Sliding Number Classic Puzzle](category/games/2026/02/1738890307-sliding-number-classic-puzzle/) | Classic 15-puzzle game. Slide numbered tiles to arrange them in order.
* 2026-02-07 | [Circular Brick Breaker Classic](category/games/2026/02/1738886273-circular-brick-breaker-classic/) | 360-degree brick breaker with a ball spawning from center. Rotate the paddle to break circular brick layers.
* 2026-02-06 | [Gravity Stack Balance](category/games/2026/02/0713-gravity-stack-balance/) | Physics-based block stacking on a narrow platform. Blocks tilt and fall if unbalanced.
* 2026-02-06 | [Neon Snake Retro](category/games/2026/02/0712-neon-snake-retro/) | Classic snake game with neon visual style. Navigate a snake to eat food while avoiding walls and your own body.
* 2026-02-06 | [Rhythmic Tile Tap Classic](category/games/2026/02/0701-rhythmic-tile-tap-classic/) | Tap black tiles falling to the beat in 4 lanes. Speed increases as you score higher - miss a tile or tap empty space and it's game over.
* 2026-02-06 | [Quantum Mine Sweeper Lite](category/games/2026/02/0700-quantum-mine-sweeper-lite/) | Classic minesweeper with logical deduction. Find 15 mines on a 10x10 grid using number clues.
* 2026-02-06 | [Minimalist Falling Sand Box](category/games/2026/02/0700-minimalist-falling-sand-box/) | Pixel art physics simulation with gravity and particle interactions. Draw sand, water, and walls to create falling experiments.
* 2026-02-06 | [Zen Garden Match Three](category/games/2026/02/0624-zen-garden-match-three/) | A relaxing match-three puzzle game with calm vibes. Swap flowers to match 3+ and score points in 60 seconds.
* 2026-02-06 | [Galactic Dodge Classic](category/games/2026/02/0623-galactic-dodge-classic/) | Dodge endless asteroids in this classic arcade survival game. Pilot your spaceship and achieve the highest survival score. 
* 2026-02-06 | [Color Flood Puzzle](category/games/2026/02/0622-color-flood-puzzle/) | An addictive strategy puzzle game to unify all tiles to one color in minimum moves. 
* 2026-02-06 | [Neon Snake Retro](category/games/2026/02/0621-neon-snake-retro/) | Classic snake game with neon visual style. Navigate a snake to eat food while avoiding walls and your own body.

## Project Structure

```
game-factory/
├── category/
│   ├── games/
│   │   ├── 2026
|   │   │   ├── 02
|   |   │   │   │   ├── 1738933488-polar-bear-ice-bridge/
|   |   │   │   ├── 1738918819-ocean-cleanup-bubble-pop/
|   |   │   │   ├── 1738918960-binary-crossroad-traffic-control/
|   |   │   │   ├── 1738891527-lunar-lander-physics-lite/
|   |   │   │   ├── 1738890307-sliding-number-classic-puzzle/
|   |   │   │   ├── 1738886273-circular-brick-breaker-classic/
|   |   │   │   ├── 0713-gravity-stack-balance/
|   |   │   │   ├── 0712-neon-snake-retro/
|   |   │   │   ├── 0701-rhythmic-tile-tap-classic/
|   |   │   │   ├── 0700-quantum-mine-sweeper-lite/
|   |   │   │   ├── 0700-minimalist-falling-sand-box/
|   |   │   │   ├── 0624-zen-garden-match-three/
|   |   │   │   ├── 0623-galactic-dodge-classic/
|   |   │   │   ├── 0622-color-flood-puzzle/
|   |   │   │   └── 0621-neon-snake-retro/
|   │   └── ... (more categories)
└── README.md
```

## Running the Apps

Each app is self-contained with its own dependencies. Navigate to the app's folder and follow the instructions in its README.md.

## Contributing

Apps are organized by category and dated. When adding a new app:

1. Create a new directory following the naming convention: `category/{category}/{YYYY}/{YYYY-MM-DD}-{index}-{app-name}/`
2. Include a `main.py` (or appropriate entry point)
3. Add a `README.md` with the app description, how to build/run, and examples
4. Update this root `README.md` to include the new app

## License

MIT
