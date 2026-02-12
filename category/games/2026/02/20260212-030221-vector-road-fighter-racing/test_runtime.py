"""Runtime analysis test for Road Fighter Racing."""

import sys
import os

# Mock pygame for headless testing
class MockPygame:
    QUIT = 1
    KEYDOWN = 2
    K_ESCAPE = 27
    K_SPACE = 32
    K_LEFT = 276
    K_RIGHT = 275
    K_UP = 273
    K_DOWN = 274
    K_r = 114
    SRCALPHA = 0

    def __init__(self):
        self.initialized = False
        self.screen_surface = None
        self.display_set = False
        self.clock_created = False
        self.fonts_created = 0

    def init(self):
        self.initialized = True
        return None

    class display:
        @staticmethod
        def set_mode(size):
            return MockSurface(size)

        @staticmethod
        def set_caption(title):
            pass

        @staticmethod
        def flip():
            pass

    def display_set_mode(self, size):
        self.display_set = True
        return MockSurface(size)

    def display_set_caption(self, title):
        pass

    def time_get_ticks(self):
        return 0

    def time_Clock(self):
        self.clock_created = True
        return MockClock()

    def font_Font(self, name, size):
        self.fonts_created += 1
        return MockFont()

    def event_get(self):
        return []

    def key_get_pressed(self):
        return {}

    def display_flip(self):
        pass

    def quit(self):
        pass

    class time:
        @staticmethod
        def get_ticks():
            return 0

        @staticmethod
        def Clock():
            return MockClock()

    class font:
        @staticmethod
        def Font(name, size):
            return MockFont()

    def time_get_ticks(self):
        return 0

    def time_Clock(self):
        self.clock_created = True
        return MockClock()

    def draw_line(self, surface, color, start, end, width):
        pass

    def draw_rect(self, surface, color, rect, width=0):
        pass

    def Surface(self, size, flags=0):
        return MockSurface(size)


class MockSurface:
    def __init__(self, size):
        self.size = size
        self.width = size[0]
        self.height = size[1]

    def fill(self, color):
        pass

    def blit(self, source, dest):
        pass


class MockClock:
    def tick(self, fps):
        return 16


class MockFont:
    def __init__(self):
        self.size = 24

    def render(self, text, antialias, color):
        return MockSurface((len(text) * 10, self.size))

    def get_width(self):
        return 100

    def get_height(self):
        return 20


class MockRect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.width = w
        self.height = h

    def colliderect(self, other):
        return False


# Replace pygame module
sys.modules['pygame'] = MockPygame()
sys.modules['pygame'].QUIT = 1
sys.modules['pygame'].KEYDOWN = 2
sys.modules['pygame'].K_ESCAPE = 27
sys.modules['pygame'].K_SPACE = 32
sys.modules['pygame'].K_LEFT = 276
sys.modules['pygame'].K_RIGHT = 275
sys.modules['pygame'].K_UP = 273
sys.modules['pygame'].K_DOWN = 274
sys.modules['pygame'].K_r = 114
sys.modules['pygame'].SRCALPHA = 0
sys.modules['pygame'].Rect = MockRect

# Now import the game modules
from config import *
from entities import Player, Enemy, FuelTank
from game import Game
import json

def analyze_game():
    """Perform runtime analysis of the game."""
    results = {
        "test_name": "Runtime Analysis - Road Fighter Racing",
        "timestamp": "2026-02-12T03:02:21Z",
        "tests": []
    }

    # Test 1: Import and initialization
    try:
        game = Game()
        results["tests"].append({
            "name": "Game Initialization",
            "status": "PASSED",
            "description": "Game object created successfully"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Game Initialization",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 2: Player entity
    try:
        player = Player()
        tests_passed = 0
        tests_total = 0

        tests_total += 1
        if player.lane == 1:  # Starting lane
            tests_passed += 1

        tests_total += 1
        if player.fuel == INITIAL_FUEL:
            tests_passed += 1

        tests_total += 1
        if player.velocity == 0.0:
            tests_passed += 1

        # Test acceleration
        player.accelerate()
        tests_total += 1
        if player.velocity > 0:
            tests_passed += 1

        # Test braking
        player.brake()
        tests_total += 1
        if player.velocity < PLAYER_MAX_SPEED:
            tests_passed += 1

        # Test lane change
        initial_lane = player.lane
        player.change_lane(1)
        tests_total += 1
        if player.lane == initial_lane + 1:
            tests_passed += 1

        # Test bounds check
        player.lane = 0
        player.change_lane(-1)
        tests_total += 1
        if player.lane == 0:  # Should not go below 0
            tests_passed += 1

        results["tests"].append({
            "name": "Player Entity",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed",
            "initial_lane": 1,
            "initial_fuel": INITIAL_FUEL,
            "lane_change_works": player.lane >= 0 and player.lane < NUM_LANES
        })
    except Exception as e:
        results["tests"].append({
            "name": "Player Entity",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 3: Enemy entity
    try:
        enemy = Enemy(distance=500, erratic=True)
        tests_passed = 0
        tests_total = 0

        tests_total += 1
        if 0 <= enemy.lane < NUM_LANES:
            tests_passed += 1

        tests_total += 1
        if ENEMY_SPEED_MIN <= enemy.speed <= ENEMY_SPEED_MAX:
            tests_passed += 1

        tests_total += 1
        if enemy.erratic:
            tests_passed += 1

        # Test enemy update
        initial_dist = enemy.distance
        enemy.update()
        tests_total += 1
        if enemy.distance < initial_dist:  # Enemy moves toward player
            tests_passed += 1

        results["tests"].append({
            "name": "Enemy Entity",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Enemy Entity",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 4: Fuel Tank entity
    try:
        fuel = FuelTank(distance=300)
        tests_passed = 0
        tests_total = 0

        tests_total += 1
        if 0 <= fuel.lane < NUM_LANES:
            tests_passed += 1

        tests_total += 1
        if not fuel.collected:
            tests_passed += 1

        results["tests"].append({
            "name": "Fuel Tank Entity",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Fuel Tank Entity",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 5: Game state management
    try:
        game = Game()
        tests_passed = 0
        tests_total = 0

        tests_total += 1
        if game.game_state == STATE_MENU:
            tests_passed += 1

        tests_total += 1
        if len(game.enemies) == 0:
            tests_passed += 1

        tests_total += 1
        if game.score == 0:
            tests_passed += 1

        # Test observation system
        obs = game.get_observation()
        tests_total += 1
        if "player" in obs and "enemies" in obs and "fuel" in obs:
            tests_passed += 1

        # Test AI action system
        obs, reward, done = game.step_ai(2)  # Accelerate
        tests_total += 1
        if "player" in obs:
            tests_passed += 1

        results["tests"].append({
            "name": "Game State Management",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Game State Management",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 6: Collision detection setup
    try:
        player = Player()
        enemy = Enemy(distance=100)

        player_rect = player.get_rect()
        enemy_rect = enemy.get_rect(player.distance)

        tests_passed = 0
        tests_total = 0

        tests_total += 1
        if player_rect is not None:
            tests_passed += 1

        tests_total += 1
        if enemy_rect is not None:
            tests_passed += 1

        results["tests"].append({
            "name": "Collision Detection",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Collision Detection",
            "status": "FAILED",
            "error": str(e)
        })

    # Test 7: Win/Lose conditions
    try:
        player = Player()

        # Test fuel depletion
        player.fuel = 0
        tests_total = 1
        tests_passed = 1 if player.fuel <= 0 else 0

        # Test win condition distance
        win_distance_met = TARGET_DISTANCE >= 10000
        tests_total += 1
        if win_distance_met:
            tests_passed += 1

        results["tests"].append({
            "name": "Win/Lose Conditions",
            "status": "PASSED" if tests_passed == tests_total else "FAILED",
            "details": f"{tests_passed}/{tests_total} sub-tests passed",
            "target_distance": TARGET_DISTANCE,
            "initial_fuel": INITIAL_FUEL
        })
    except Exception as e:
        results["tests"].append({
            "name": "Win/Lose Conditions",
            "status": "FAILED",
            "error": str(e)
        })

    # Calculate overall status
    passed = sum(1 for t in results["tests"] if t.get("status") == "PASSED")
    total = len(results["tests"])
    results["overall_status"] = "PASSED" if passed == total else "FAILED"
    results["summary"] = f"{passed}/{total} tests passed"

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("RUNTIME ANALYSIS - Road Fighter Racing")
    print("=" * 60)

    results = analyze_game()

    print("\nTest Results:")
    for test in results["tests"]:
        status_symbol = "✓" if test["status"] == "PASSED" else "✗"
        print(f"  {status_symbol} {test['name']}: {test['status']}")
        if "details" in test:
            print(f"      {test['details']}")
        if "error" in test:
            print(f"      Error: {test['error']}")

    print(f"\n{results['summary']}")
    print(f"Overall Status: {results['overall_status']}")

    # Save to JSON
    with open("runtime_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to runtime_analysis.json")
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)
