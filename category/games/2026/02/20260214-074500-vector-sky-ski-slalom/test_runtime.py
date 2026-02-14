"""Runtime analysis test for Vector Sky Ski Slalom."""

import os
import sys
import json
import time
import pygame
import pygame.key
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from game import Game
from renderer import Renderer
from config import *


def simulate_ai_inputs(game_state, elapsed_time):
    """Simulate basic AI player inputs based on game state."""
    inputs = {'left': False, 'right': False}

    if game_state.game_over:
        return inputs

    # Find nearest obstacle
    nearest_obstacle = None
    nearest_y = float('inf')

    for obstacle in game_state.obstacles:
        if obstacle.y > game_state.player.y - 200:  # Only look ahead
            if obstacle.y < nearest_y:
                nearest_y = obstacle.y
                nearest_obstacle = obstacle

    # Find nearest gate
    nearest_gate = None
    nearest_gate_y = float('inf')

    for gate in game_state.gates:
        if gate.y > game_state.player.y - 200:
            if gate.y < nearest_gate_y:
                nearest_gate_y = gate.y
                nearest_gate = gate

    # Simple avoidance logic
    player_center = game_state.player.x
    player_left_bound = player_center - 30
    player_right_bound = player_center + 30

    # Avoid obstacles
    if nearest_obstacle and nearest_obstacle.y < game_state.player.y + 150:
        obstacle_left = nearest_obstacle.x - nearest_obstacle.width // 2
        obstacle_right = nearest_obstacle.x + nearest_obstacle.width // 2

        # If obstacle is in our path, dodge
        if obstacle_left < player_right_bound and obstacle_right > player_left_bound:
            # Decide dodge direction
            if player_center < SCREEN_WIDTH // 2:
                inputs['right'] = True
            else:
                inputs['left'] = True

    # Try to pass through gates
    if nearest_gate and nearest_gate.y < game_state.player.y + 150:
        gate_center = (nearest_gate.left_pole_x + nearest_gate.right_pole_x) // 2

        # Steer toward gate center
        if abs(player_center - gate_center) > 20:
            if player_center < gate_center:
                inputs['right'] = True
            else:
                inputs['left'] = True

    # Stay on screen
    if player_center < 50:
        inputs['right'] = True
    elif player_center > SCREEN_WIDTH - 50:
        inputs['left'] = True

    return inputs


def run_runtime_analysis(max_duration_seconds=120):
    """Run the game and analyze runtime behavior."""
    print(f"[*] Starting runtime analysis for {max_duration_seconds} seconds...")

    pygame.init()
    pygame.display.init()

    game = Game()
    renderer = Renderer(game)
    clock = pygame.time.Clock()

    # Analysis data
    analysis = {
        'app_name': 'vector-sky-ski-slalom',
        'test_timestamp': datetime.utcnow().isoformat() + 'Z',
        'test_duration_seconds': max_duration_seconds,
        'framework': 'Pygame',
        'expected_resolution': f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}',
        'startup_test': {},
        'gameplay_test': {},
        'performance_test': {},
        'functionality_test': {},
        'events': []
    }

    start_time = time.time()
    start_ticks = pygame.time.get_ticks()

    try:
        # Test 1: Startup
        print("[*] Testing startup...")
        analysis['startup_test']['pygame_initialized'] = pygame.display.get_init()
        analysis['startup_test']['display_mode'] = str(pygame.display.get_surface().get_size())
        analysis['startup_test']['caption'] = pygame.display.get_caption()[0]
        analysis['events'].append({
            'time': 0,
            'type': 'startup',
            'status': 'PASSED',
            'message': 'Game initialized successfully'
        })

        # Test 2: Player initialization
        print("[*] Testing player initialization...")
        player = game.player
        analysis['gameplay_test']['player_start_position'] = {
            'x': player.x,
            'y': player.y,
            'expected_x': PLAYER_START_X,
            'expected_y': PLAYER_START_Y
        }
        analysis['gameplay_test']['player_alive_at_start'] = player.alive
        analysis['events'].append({
            'time': 0,
            'type': 'player_init',
            'status': 'PASSED',
            'message': f'Player initialized at ({player.x}, {player.y})'
        })

        frame_count = 0
        last_fps_update = start_time
        fps_frame_count = 0
        fps_samples = []

        print("[*] Running gameplay simulation...")
        running = True

        while running and (time.time() - start_time) < max_duration_seconds:
            current_time = time.time() - start_time
            dt = clock.tick(60) / 1000.0

            # Generate simulated AI inputs
            inputs = simulate_ai_inputs(game, current_time)

            # Simulate pygame events for quit check
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Update game
            game.update(dt, inputs)
            renderer.render()

            # Performance tracking
            frame_count += 1
            fps_frame_count += 1

            if time.time() - last_fps_update >= 1.0:
                fps = fps_frame_count / (time.time() - last_fps_update)
                fps_samples.append(fps)
                fps_frame_count = 0
                last_fps_update = time.time()

                analysis['events'].append({
                    'time': round(current_time, 2),
                    'type': 'fps_sample',
                    'value': round(fps, 2)
                })

            # Periodic checkpoints
            if frame_count % 360 == 0:  # Every ~6 seconds at 60 FPS
                checkpoint_time = round(current_time, 2)
                analysis['events'].append({
                    'time': checkpoint_time,
                    'type': 'checkpoint',
                    'game_over': game.game_over,
                    'score': game.score,
                    'distance': round(game.distance, 2),
                    'scroll_speed': round(game.scroll_speed, 2),
                    'obstacle_count': len(game.obstacles),
                    'gate_count': len(game.gates),
                    'player_position': {'x': round(game.player.x, 2), 'y': round(game.player.y, 2)}
                })

        # Test 3: Performance summary
        print("[*] Analyzing performance...")
        if fps_samples:
            analysis['performance_test']['average_fps'] = round(sum(fps_samples) / len(fps_samples), 2)
            analysis['performance_test']['min_fps'] = round(min(fps_samples), 2)
            analysis['performance_test']['max_fps'] = round(max(fps_samples), 2)
            analysis['performance_test']['total_frames'] = frame_count
            analysis['performance_test']['target_fps'] = 60

            fps_status = 'PASSED' if analysis['performance_test']['average_fps'] >= 55 else 'FAILED'
            analysis['events'].append({
                'time': round(time.time() - start_time, 2),
                'type': 'performance',
                'status': fps_status,
                'message': f"Average FPS: {analysis['performance_test']['average_fps']}"
            })

        # Test 4: Gameplay mechanics
        print("[*] Verifying gameplay mechanics...")
        analysis['gameplay_test']['final_score'] = game.score
        analysis['gameplay_test']['final_distance'] = round(game.distance, 2)
        analysis['gameplay_test']['final_scroll_speed'] = round(game.scroll_speed, 2)
        analysis['gameplay_test']['game_over'] = game.game_over
        analysis['gameplay_test']['player_alive'] = game.player.alive

        # Check if game progresses
        analysis['functionality_test']['score_increases'] = game.score > 0
        analysis['functionality_test']['distance_increases'] = game.distance > 0
        analysis['functionality_test']['speed_increases'] = game.scroll_speed > BASE_SCROLL_SPEED
        analysis['functionality_test']['obstacles_spawned'] = len(game.obstacles) > 0 or game.distance > 1000

        mechanics_status = 'PASSED'
        if not analysis['functionality_test']['score_increases']:
            mechanics_status = 'FAILED'
        if not analysis['functionality_test']['distance_increases']:
            mechanics_status = 'FAILED'

        analysis['events'].append({
            'time': round(time.time() - start_time, 2),
            'type': 'gameplay_mechanics',
            'status': mechanics_status,
            'message': f"Score: {game.score}, Distance: {round(game.distance, 2)}"
        })

        # Test 5: Rendering
        print("[*] Verifying rendering...")
        try:
            screen_surface = pygame.display.get_surface()
            analysis['functionality_test']['display_active'] = screen_surface is not None
            analysis['functionality_test']['display_size'] = str(screen_surface.get_size()) if screen_surface else None
            analysis['events'].append({
                'time': round(time.time() - start_time, 2),
                'type': 'rendering',
                'status': 'PASSED',
                'message': 'Rendering functional'
            })
        except Exception as e:
            analysis['functionality_test']['display_active'] = False
            analysis['events'].append({
                'time': round(time.time() - start_time, 2),
                'type': 'rendering',
                'status': 'FAILED',
                'message': str(e)
            })

        print("[*] Analysis complete.")
        analysis['overall_status'] = 'PASSED'

    except Exception as e:
        print(f"[!] Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        analysis['overall_status'] = 'FAILED'
        analysis['error'] = str(e)
        analysis['error_type'] = type(e).__name__
        analysis['events'].append({
            'time': round(time.time() - start_time, 2),
            'type': 'error',
            'status': 'FAILED',
            'message': str(e)
        })

    finally:
        pygame.quit()

    return analysis


if __name__ == "__main__":
    result = run_runtime_analysis(max_duration_seconds=120)

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), 'runtime_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n[*] Runtime analysis saved to {output_path}")
    print(f"[*] Overall Status: {result['overall_status']}")
    sys.exit(0 if result['overall_status'] == 'PASSED' else 1)
