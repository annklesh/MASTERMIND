import unittest
from game_logic import MastermindLogic

class TestMastermindLogic(unittest.TestCase):
    def setUp(self):
        self.game = MastermindLogic()

    def test_full_match(self):
        self.game.set_secret_code(['Red', 'Blue', 'Green', 'Yellow'])
        result = self.game.check_guess(['Red', 'Blue', 'Green', 'Yellow'])
        self.assertEqual(result, (4, 0))

    def test_partial_match(self):
        self.game.set_secret_code(['Red', 'Blue', 'Green', 'Yellow'])
        result = self.game.check_guess(['Blue', 'Red', 'Yellow', 'Green'])
        self.assertEqual(result, (0, 4))

if __name__ == '__main__':
    unittest.main()