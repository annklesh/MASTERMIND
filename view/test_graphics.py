import sys
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from graphics import MastermindNeonUI

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestMastermindGraphics(unittest.TestCase):
    def setUp(self):
        self.window = MastermindNeonUI()

    def tearDown(self):
        self.window.close()

    def test_initial_screen_is_menu(self):
        current_index = self.window.stacked_widget.currentIndex()
        self.assertEqual(current_index, 0)

    def test_menu_buttons_text(self):
        menu = self.window.menu_screen
        self.assertEqual(menu.btn_player_vs_comp.text(), "Human vs AI")
        self.assertEqual(menu.btn_player_vs_player.text(), "Human vs Hardware")
        self.assertEqual(menu.btn_comp_vs_player.text(), "AI vs Human")

    def test_navigation_to_game_screen(self):
        menu = self.window.menu_screen
        menu.btn_player_vs_comp.click()
        current_index = self.window.stacked_widget.currentIndex()
        self.assertEqual(current_index, 1)

    def test_game_board_structure(self):
        game = self.window.game_screen
        self.assertEqual(len(game.board_pegs), 10)
        for row in game.board_pegs:
            self.assertEqual(len(row), 4)

    def test_image_loading_fallback(self):
        game = self.window.game_screen
        fallback_label = game.create_image_icon("fake_file_name.png", 20, 20)
        self.assertEqual(fallback_label.text(), "?")

if __name__ == '__main__':
    unittest.main()