"""
Testy jednostkowe dla klasy GameBot.

Uruchomienie:
    pytest test_game_bot.py -v
"""

import unittest
from unittest.mock import patch, MagicMock

from bot.game_bot import GameBot


def make_bot(logic_answer: tuple[int, int] = (0, 0)) -> GameBot:
    """Tworzy instancję GameBot z zamockowaną logiką gry.

    Args:
        logic_answer (tuple[int, int]): Odpowiedź logiki przekazana do bota.

    Returns:
        GameBot: Instancja bota gotowa do testowania.
    """
    mock_logic = MagicMock()
    mock_logic.available_colors = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
    mock_logic.code_length = 4

    with patch('bot.game_bot.MastermindLogic', return_value=mock_logic):
        return GameBot(logic_answer)


class TestCheck(unittest.TestCase):
    """Testy metody check() sprawdzającej przypuszczenie względem celu."""

    def setUp(self) -> None:
        """Inicjalizuje bota przed każdym testem."""
        self.bot = make_bot()

    def test_wszystkie_kolory_na_wlasciwym_miejscu(self) -> None:
        """Zwraca (4, 0) gdy guess jest identyczny z target."""
        wynik = self.bot.check(['Red', 'Blue', 'Green', 'Yellow'], ['Red', 'Blue', 'Green', 'Yellow'])
        self.assertEqual(wynik, (4, 0))

    def test_brak_trafien(self) -> None:
        """Zwraca (0, 0) gdy żaden kolor nie pasuje."""
        wynik = self.bot.check(['Red', 'Red', 'Red', 'Red'], ['Blue', 'Blue', 'Blue', 'Blue'])
        self.assertEqual(wynik, (0, 0))

    def test_tylko_zle_miejsca(self) -> None:
        """Zwraca (0, n) gdy kolory się zgadzają, ale są na złych miejscach."""
        wynik = self.bot.check(['Red', 'Blue', 'Green', 'Yellow'], ['Blue', 'Green', 'Yellow', 'Red'])
        self.assertEqual(wynik, (0, 4))

    def test_mieszane_trafienia(self) -> None:
        """Zwraca poprawny wynik dla mieszanej kombinacji trafień."""
        wynik = self.bot.check(['Red', 'Orange', 'Yellow', 'Green'], ['Red', 'Green', 'Orange', 'Blue'])
        self.assertEqual(wynik, (1, 2))

    def test_powtarzajace_sie_kolory_w_guess(self) -> None:
        """Nie liczy tego samego koloru z target więcej niż raz."""
        wynik = self.bot.check(['Red', 'Red', 'Red', 'Red'], ['Red', 'Blue', 'Blue', 'Blue'])
        self.assertEqual(wynik, (1, 0))

    def test_powtarzajace_sie_kolory_w_target(self) -> None:
        """Poprawnie obsługuje powtórzenia kolorów w target."""
        wynik = self.bot.check(['Red', 'Blue', 'Blue', 'Blue'], ['Red', 'Red', 'Red', 'Red'])
        self.assertEqual(wynik, (1, 0))


class TestRestartGame(unittest.TestCase):
    """Testy metody restart_game() resetującej stan bota."""

    def setUp(self) -> None:
        """Inicjalizuje bota przed każdym testem."""
        self.bot = make_bot()

    def test_reset_zbioru_kolorow(self) -> None:
        """Po restarcie new_set_of_colors jest równy pełnemu zbiorowi."""
        self.bot.new_set_of_colors = [['Red', 'Red', 'Red', 'Red']]
        self.bot.restart_game()
        self.assertEqual(self.bot.new_set_of_colors, self.bot.set_of_answers)

    def test_reset_check_colors(self) -> None:
        """Po restarcie check_colors wraca do wartości początkowej."""
        self.bot.check_colors = ['Blue', 'Blue', 'Blue', 'Blue']
        self.bot.restart_game()
        self.assertEqual(self.bot.check_colors, ['Red', 'Red', 'Orange', 'Orange'])

    def test_aktualizacja_logic_answer(self) -> None:
        """Przekazanie new_answer aktualizuje logic_answer."""
        self.bot.restart_game(new_answer=(3, 1))
        self.assertEqual(self.bot.logic_answer, (3, 1))

    def test_brak_aktualizacji_bez_new_answer(self) -> None:
        """Bez new_answer logic_answer pozostaje niezmieniony."""
        self.bot.logic_answer = (2, 2)
        self.bot.restart_game()
        self.assertEqual(self.bot.logic_answer, (2, 2))


class TestGetACheckToLogic(unittest.TestCase):
    """Testy metody get_a_check_to_logic() zwracającej aktualne przypuszczenie."""

    def test_zwraca_check_colors(self) -> None:
        """Zwraca aktualną wartość check_colors."""
        bot = make_bot()
        self.assertEqual(bot.get_a_check_to_logic(), ['Red', 'Red', 'Orange', 'Orange'])

    def test_zwraca_zaktualizowane_check_colors(self) -> None:
        """Po zmianie check_colors zwraca nową wartość."""
        bot = make_bot()
        bot.check_colors = ['Blue', 'Green', 'Yellow', 'Purple']
        self.assertEqual(bot.get_a_check_to_logic(), ['Blue', 'Green', 'Yellow', 'Purple'])


class TestCreateANewSetOfColors(unittest.TestCase):
    """Testy metody create_a_new_set_of_colors() filtrującej zbiór kandydatów."""

    def test_filtruje_poprawnie(self) -> None:
        """Pozostawia tylko kandydatów zgodnych z logic_answer."""
        bot = make_bot(logic_answer=(4, 0))
        bot.check_colors = ['Red', 'Blue', 'Green', 'Yellow']
        bot.new_set_of_colors = [
            ['Red', 'Blue', 'Green', 'Yellow'],
            ['Red', 'Blue', 'Green', 'Purple'],
            ['Orange', 'Orange', 'Orange', 'Orange'],
        ]
        bot.create_a_new_set_of_colors()
        self.assertEqual(bot.new_set_of_colors, [['Red', 'Blue', 'Green', 'Yellow']])

    def test_pusty_zbior_gdy_brak_kandydatow(self) -> None:
        """Zwraca pusty zbiór gdy żaden kandydat nie pasuje do logic_answer."""
        bot = make_bot(logic_answer=(4, 0))
        bot.check_colors = ['Red', 'Blue', 'Green', 'Yellow']
        bot.new_set_of_colors = [['Orange', 'Orange', 'Orange', 'Orange']]
        bot.create_a_new_set_of_colors()
        self.assertEqual(bot.new_set_of_colors, [])


class TestMakeAGuess(unittest.TestCase):
    """Testy metody make_a_guess() wybierającej kolejne przypuszczenie."""

    def test_jeden_kandydat_wybrany_bezposrednio(self) -> None:
        """Gdy zostaje jeden kandydat, bot wybiera go bez obliczeń."""
        bot = make_bot()
        bot.new_set_of_colors = [['Blue', 'Green', 'Yellow', 'Purple']]
        bot.make_a_guess()
        self.assertEqual(bot.check_colors, ['Blue', 'Green', 'Yellow', 'Purple'])

    def test_wynik_jest_prawidlowa_kombinacja(self) -> None:
        """Po make_a_guess check_colors jest prawidłową kombinacją ze zbioru."""
        bot = make_bot()
        bot.make_a_guess()
        self.assertIn(bot.check_colors, bot.set_of_answers)

    def test_bot_odgaduje_w_max_5_ruchach(self) -> None:
        """Bot odgaduje losową próbkę 30 kodów w maksymalnie 5 ruchach (gwarancja Knutha)."""
        import random
        import itertools
        colors = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
        all_codes = [list(p) for p in itertools.product(colors, repeat=4)]
        sample = random.sample(all_codes, 30)

        for secret in sample:
            bot = make_bot(logic_answer=(0, 0))
            ruchy = 0
            while True:
                bot.make_a_guess()
                guess = bot.get_a_check_to_logic()
                ruchy += 1
                result = bot.check(guess, secret)
                if result == (4, 0):
                    break
                bot.logic_answer = result
                bot.create_a_new_set_of_colors()
                self.assertLessEqual(ruchy, 5, f"Bot nie odgadł {secret} w 5 ruchach")


if __name__ == '__main__':
    unittest.main()