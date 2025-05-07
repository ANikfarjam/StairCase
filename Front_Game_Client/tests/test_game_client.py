import unittest
import pygame
import sys
import os

from game_client import (
    get_cell_coords,
    draw_board,
    draw_snakes_ladders,
    draw_players,
    draw_game_info,
    draw_player_identification,
    draw_dice_button,
    draw_restart_button,
    draw_modal
)

class TestGameClient(unittest.TestCase):
    def setUp(self):
        """Set up pygame and test surface before each test"""
        pygame.init()
        self.screen = pygame.Surface((800, 800))
        self.test_state = {
            "players": {"player_1": 0, "player_2": 0},
            "snakes": {"10": "5", "20": "15"},
            "ladders": {"3": "12", "7": "18"},
            "trivia_cells": [5, 15, 25],
            "hangman_cells": [10, 20, 30],
            "current_player": 1,
            "game_over": False,
            "winner": None,
            "message": "Test message"
        }

    def tearDown(self):
        """Clean up pygame after each test"""
        pygame.quit()

    def test_get_cell_coords(self):
        """Test cell coordinate calculations"""
        # Test first square of board (1)
        x, y = get_cell_coords(1)
        self.assertEqual(x, 130)
        self.assertEqual(y, 670)

        # Test last square of board (100)
        x, y = get_cell_coords(100)
        self.assertEqual(x, 670)
        self.assertEqual(y, 130)

        # Test position 50
        x, y = get_cell_coords(50)
        self.assertEqual(x, 670)
        self.assertEqual(y, 430)

if __name__ == '__main__':
    unittest.main()