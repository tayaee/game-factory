"""Headless runtime test for Vector Mario Bros Hammer Throw."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock pygame for headless testing
class MockPygame:
    """Mock pygame module for headless testing."""
    QUIT = 1
    KEYDOWN = 2
    KEYUP = 3
    K_ESCAPE = 1
    K_SPACE = 2
    K_UP = 3
    K_DOWN = 4
    K_r = 5

    class time:
        @staticmethod
        def Clock():
            class MockClock:
                def tick(self, fps):
                    return 16
            return MockClock()

        @staticmethod
        def get_ticks():
            return 0

    class display:
        @staticmethod
        def set_mode(size):
            return None

        @staticmethod
        def set_caption(title):
            pass

        @staticmethod
        def flip():
            pass

    class draw:
        @staticmethod
        def line(surface, color, start, end, width):
            pass

        @staticmethod
        def rect(surface, color, rect, width=0):
            pass

        @staticmethod
        def circle(surface, color, center, radius):
            pass

        @staticmethod
        def ellipse(surface, color, rect):
            pass

        @staticmethod
        def arc(surface, color, rect, start, stop, width):
            pass

    class font:
        @staticmethod
        def Font(filename, size):
            class MockFont:
                def render(self, text, antialias, color):
                    class MockSurface:
                        def get_width(self):
                            return len(text) * 10
                        def get_height(self):
                            return 20
                        def get_width_half(self):
                            return len(text) * 5
                        width = property(lambda self: self.get_width())
                    return MockSurface()
            return MockFont()

    @staticmethod
    def init():
        pass

    @staticmethod
    def quit():
        pass

    @staticmethod
    def event():
        @staticmethod
        def get():
            return []

    @staticmethod
    def key():
        @staticmethod
        def get_pressed():
            return []

    @staticmethod
    def Surface(size):
        class MockSurface:
            def set_alpha(self, alpha):
                pass

            def fill(self, color):
                pass

            def blit(self, source, dest):
                pass
        return MockSurface()

    class Rect:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.width, self.height = x, y, w, h

        @property
        def left(self):
            return self.x

        @property
        def right(self):
            return self.x + self.width

        @property
        def top(self):
            return self.y

        @property
        def bottom(self):
            return self.y + self.height

        @property
        def center(self):
            return (self.x + self.width // 2, self.y + self.height // 2)

        def midleft(self):
            return (self.x, self.y + self.height // 2)

# Test the actual game logic
def test_game_imports():
    """Test that game modules can be imported."""
    results = []

    # Mock pygame
    sys.modules['pygame'] = MockPygame()

    try:
        import config
        results.append(("config module import", "PASS", None))
    except Exception as e:
        results.append(("config module import", "FAIL", str(e)))
        return results

    # Verify config constants
    try:
        assert hasattr(config, 'SCREEN_WIDTH')
        assert hasattr(config, 'SCREEN_HEIGHT')
        assert hasattr(config, 'GRAVITY')
        assert hasattr(config, 'PLAYER_X')
        assert hasattr(config, 'PLAYER_Y')
        assert hasattr(config, 'MAX_HAMMERS')
        assert hasattr(config, 'REWARD_HIT')
        assert hasattr(config, 'REWARD_MULTI_KILL')
        assert hasattr(config, 'REWARD_MISS')
        assert hasattr(config, 'REWARD_GAME_OVER')
        results.append(("config constants check", "PASS", None))
    except Exception as e:
        results.append(("config constants check", "FAIL", str(e)))

    try:
        import entities
        results.append(("entities module import", "PASS", None))
    except Exception as e:
        results.append(("entities module import", "FAIL", str(e)))
        return results

    try:
        import game
        results.append(("game module import", "PASS", None))
    except Exception as e:
        results.append(("game module import", "FAIL", str(e)))
        return results

    return results


def test_entity_creation():
    """Test that game entities can be created."""
    sys.modules['pygame'] = MockPygame()
    import config
    from entities import Player, Hammer, Enemy, Platform

    results = []

    # Test Player creation
    try:
        player = Player(config.PLAYER_X, config.PLAYER_Y)
        assert player.x == config.PLAYER_X
        assert player.y == config.PLAYER_Y
        assert player.angle == 45
        assert player.hammers_left == config.MAX_HAMMERS
        results.append(("Player creation", "PASS", None))
    except Exception as e:
        results.append(("Player creation", "FAIL", str(e)))

    # Test Hammer creation
    try:
        hammer = Hammer(100, 100, 45, 200)
        assert hammer.x == 100
        assert hammer.y == 100
        assert hammer.active == True
        results.append(("Hammer creation", "PASS", None))
    except Exception as e:
        results.append(("Hammer creation", "FAIL", str(e)))

    # Test Enemy creation
    try:
        enemy = Enemy(200, 300, 300, "koopa")
        assert enemy.x == 200
        assert enemy.y == 300
        assert enemy.type == "koopa"
        assert enemy.alive == True
        results.append(("Enemy creation", "PASS", None))
    except Exception as e:
        results.append(("Enemy creation", "FAIL", str(e)))

    # Test Platform creation
    try:
        platform = Platform(config.PLATFORM_Y)
        assert platform.y == config.PLATFORM_Y
        results.append(("Platform creation", "PASS", None))
    except Exception as e:
        results.append(("Platform creation", "FAIL", str(e)))

    return results


def test_physics():
    """Test basic physics calculations."""
    sys.modules['pygame'] = MockPygame()
    import config
    from entities import Hammer, Enemy

    results = []

    # Test hammer projectile physics
    try:
        hammer = Hammer(100, 400, 45, 300)
        initial_vx = hammer.vx
        initial_vy = hammer.vy

        # Simulate a few frames
        dt = 0.016  # 60 FPS
        for _ in range(10):
            hammer.update(dt)

        # Check that hammer moves (gravity affects vy)
        assert hammer.y != 400, "Hammer should move due to gravity"
        assert hammer.x != 100, "Hammer should move horizontally"
        assert hammer.vy > initial_vy, "Gravity should increase vy"
        results.append(("Hammer physics simulation", "PASS", None))
    except Exception as e:
        results.append(("Hammer physics simulation", "FAIL", str(e)))

    # Test enemy movement
    try:
        enemy = Enemy(200, 300, 300, "koopa")
        initial_x = enemy.x
        enemy.update(0.016)
        # Enemy should move in default direction
        assert enemy.x != initial_x, "Enemy should move"
        results.append(("Enemy movement", "PASS", None))
    except Exception as e:
        results.append(("Enemy movement", "FAIL", str(e)))

    # Test enemy boundary bouncing
    try:
        enemy = Enemy(40, 300, 300, "koopa")
        initial_direction = enemy.direction
        enemy.update(0.016)
        # Should bounce at left edge (x <= 50)
        assert enemy.direction == 1, f"Enemy should bounce right at left edge, got direction={enemy.direction}"
        results.append(("Enemy boundary bounce", "PASS", None))
    except Exception as e:
        results.append(("Enemy boundary bounce", "FAIL", str(e)))

    return results


def test_collision_detection():
    """Test collision detection logic."""
    sys.modules['pygame'] = MockPygame()
    import config
    from entities import Hammer, Enemy
    import game

    results = []

    # Test hammer-enemy collision (circle-rect)
    try:
        g = game.Game()
        hammer = Hammer(200, 200, 45, 200)
        enemy = Enemy(200, 200, 200, "koopa")

        # Hit boxes
        hammer_hitbox = hammer.get_hitbox()
        enemy_hitbox = enemy.get_hitbox()

        assert hammer_hitbox["type"] == "circle", "Hammer should have circular hitbox"
        assert enemy_hitbox["type"] == "rect", "Enemy should have rectangular hitbox"

        # Collision when overlapping
        collision = g.check_collision(hammer, enemy)
        results.append(("Hitbox types and collision detection", "PASS", f"collision={collision}"))
    except Exception as e:
        results.append(("Hitbox types and collision detection", "FAIL", str(e)))

    return results


def test_game_state():
    """Test game state management."""
    sys.modules['pygame'] = MockPygame()
    import config
    import game

    results = []

    try:
        g = game.Game()

        # Check initial state
        assert g.state == config.STATE_PLAYING, "Initial state should be PLAYING"
        assert g.score == 0, "Initial score should be 0"
        assert len(g.enemies) > 0, "Should spawn initial enemies"
        assert g.player is not None, "Player should be initialized"
        results.append(("Game initialization", "PASS", None))
    except Exception as e:
        results.append(("Game initialization", "FAIL", str(e)))

    # Test player throwing mechanic
    try:
        g = game.Game()

        # Start charging
        g.player.start_charge()
        assert g.player.charging == True, "Player should be charging"
        assert g.player.power >= config.MIN_POWER, "Power should be at least MIN_POWER"

        # Update charge
        g.player.update_charge(0.1)
        assert g.player.power > config.MIN_POWER, "Power should increase"

        # Release throw
        hammer = g.player.release_throw()
        assert hammer is not None, "Should create hammer"
        assert g.player.charging == False, "Should stop charging"
        assert g.player.hammers_left == config.MAX_HAMMERS - 1, "Should decrement hammer count"

        results.append(("Player throw mechanic", "PASS", None))
    except Exception as e:
        results.append(("Player throw mechanic", "FAIL", str(e)))

    # Test angle adjustment
    try:
        g = game.Game()
        initial_angle = g.player.angle

        g.player.adjust_angle(10)
        assert g.player.angle > initial_angle, "Angle should increase"

        g.player.adjust_angle(-100)
        assert g.player.angle == config.MIN_ANGLE, "Angle should clamp to MIN_ANGLE"

        g.player.adjust_angle(100)
        assert g.player.angle == config.MAX_ANGLE, "Angle should clamp to MAX_ANGLE"

        results.append(("Angle adjustment", "PASS", None))
    except Exception as e:
        results.append(("Angle adjustment", "FAIL", str(e)))

    return results


def test_reward_system():
    """Test reward structure."""
    sys.modules['pygame'] = MockPygame()
    import config

    results = []

    try:
        assert config.REWARD_HIT == 10
        assert config.REWARD_MULTI_KILL == 25
        assert config.REWARD_MISS == -1
        assert config.REWARD_GAME_OVER == -50
        results.append(("Reward constants", "PASS", None))
    except Exception as e:
        results.append(("Reward constants", "FAIL", str(e)))

    return results


def run_all_tests():
    """Run all runtime tests."""
    all_results = {
        "overall_status": "PASSED",
        "tests": []
    }

    test_categories = [
        ("Module Imports", test_game_imports),
        ("Entity Creation", test_entity_creation),
        ("Physics Simulation", test_physics),
        ("Collision Detection", test_collision_detection),
        ("Game State Management", test_game_state),
        ("Reward System", test_reward_system),
    ]

    for category_name, test_func in test_categories:
        try:
            results = test_func()
            category_passed = True
            for test_name, status, error in results:
                if status == "FAIL":
                    category_passed = False
                    all_results["overall_status"] = "FAILED"

                test_entry = {
                    "category": category_name,
                    "test": test_name,
                    "status": status
                }
                if error:
                    test_entry["error"] = error
                all_results["tests"].append(test_entry)
        except Exception as e:
            all_results["overall_status"] = "FAILED"
            all_results["tests"].append({
                "category": category_name,
                "test": "Test Suite",
                "status": "FAILED",
                "error": str(e)
            })

    return all_results


if __name__ == "__main__":
    import json

    test_results = run_all_tests()

    # Print summary
    passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
    total = len(test_results["tests"])

    print(f"\n{'='*60}")
    print(f"Runtime Analysis Results")
    print(f"{'='*60}")
    print(f"Overall Status: {test_results['overall_status']}")
    print(f"Tests Passed: {passed}/{total}")
    print(f"{'='*60}\n")

    for test in test_results["tests"]:
        status_symbol = "PASS" if test["status"] == "PASS" else "FAIL"
        print(f"[{status_symbol}] {test['category']}: {test['test']}")
        if "error" in test:
            print(f"    Error: {test['error']}")

    # Save to JSON
    with open("runtime_analysis.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"\nResults saved to runtime_analysis.json")
