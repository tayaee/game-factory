"""Test game logic without GUI."""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from game import Game, Panel, GameState


def test_game_initialization():
    """Test game initializes correctly."""
    game = Game()
    assert game.state == GameState.IDLE
    assert game.score == 0
    assert game.round_number == 1
    assert len(game.sequence) == 0
    print("Game initialization test passed!")


def test_start_round():
    """Test starting a round generates a sequence."""
    game = Game()
    game.start_round()
    assert len(game.sequence) == 1
    assert game.state == GameState.SHOWING_SEQUENCE
    print("Start round test passed!")


def test_observation():
    """Test AI observation space."""
    game = Game()
    game.start_round()
    obs = game.get_observation()
    assert 'sequence' in obs
    assert 'sequence_length' in obs
    assert 'player_progress' in obs
    assert 'state' in obs
    assert 'score' in obs
    assert 'round' in obs
    print("Observation test passed!")


def test_wrong_input():
    """Test wrong input leads to game over."""
    game = Game()
    game.sequence = [Panel.RED]
    game.state = GameState.WAITING_INPUT
    game._handle_panel_input(Panel.BLUE)
    assert game.state == GameState.GAME_OVER
    print("Wrong input test passed!")


def test_correct_sequence():
    """Test correct sequence completes round."""
    game = Game()
    game.sequence = [Panel.RED]
    game.state = GameState.WAITING_INPUT
    game._handle_panel_input(Panel.RED)
    assert game.score == POINTS_PER_ROUND
    assert game.round_number == 2
    print("Correct sequence test passed!")


if __name__ == "__main__":
    from config import POINTS_PER_ROUND

    test_game_initialization()
    test_start_round()
    test_observation()
    test_wrong_input()
    test_correct_sequence()
    print("\nAll tests passed!")
