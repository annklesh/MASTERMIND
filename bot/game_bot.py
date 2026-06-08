"""
GameBot — bot do gry Mastermind wykorzystujący algorytm minimax Knutha.

Użycie:
-------
    Tworzenie bota:
        bot = GameBot(logic_answer=(2, 1))

    Gdzie logic_answer to krotka (trafione miejsce, dobry kolor złe miejsce),
    którą zwraca MastermindLogic po sprawdzeniu kolejnej próby gracza.

    Typowa pętla gry:
        1. bot.make_a_guess()                — bot wybiera kolejne przypuszczenie
        2. guess = bot.get_a_check_to_logic() — pobierz przypuszczenie bota
        3. result = logic.check(guess)        — sprawdź przypuszczenie w logice gry
        4. bot.logic_answer = result          — zaktualizuj odpowiedź logiki
        5. bot.create_a_new_set_of_colors()   — odfiltruj zbiór możliwych odpowiedzi
        6. Powtarzaj aż do wygranej

    Restart gry:
        bot.restart_game(new_answer=(0, 0))
"""

import itertools
from collections import Counter
from multiprocessing import Pool, cpu_count

from logic.game_logic import MastermindLogic


def _evaluate_candidate(args: tuple) -> tuple:
    """Oblicza najgorszy przypadek dla pojedynczego kandydata (funkcja pomocnicza dla multiprocessing).

    Musi być zdefiniowana na poziomie modułu, aby mogła być serializowana przez pickle.

    Args:
        args (tuple): Krotka (candidate, new_set_of_colors, in_new_set), gdzie:
            - candidate (list[str]): Kandydat do oceny,
            - new_set_of_colors (list[list[str]]): Aktualny zbiór możliwych odpowiedzi,
            - in_new_set (bool): Czy kandydat należy do zbioru możliwych odpowiedzi.

    Returns:
        tuple: Krotka (max_remaining, in_new_set, candidate).
    """
    candidate, new_set_of_colors, in_new_set = args
    scores = Counter()
    for target in new_set_of_colors:
        target_rest = []
        guess_rest = []
        cp = 0
        for tc, gc in zip(target, candidate):
            if tc == gc:
                cp += 1
            else:
                target_rest.append(tc)
                guess_rest.append(gc)
        wp = 0
        for color in guess_rest:
            if color in target_rest:
                wp += 1
                target_rest.remove(color)
        scores[(cp, wp)] += 1

    return max(scores.values()), in_new_set, candidate


class GameBot:
    """Bot do gry Mastermind wykorzystujący algorytm minimax (algorytm Knutha).

    Bot przegląda wszystkie możliwe kombinacje kolorów i na każdym kroku
    wybiera takie przypuszczenie, które minimalizuje maksymalną liczbę
    wariantów pozostałych po odpowiedzi logiki.

    Attributes:
        logic_answer (tuple[int, int]): Aktualna odpowiedź logiki gry w formacie
            (liczba kolorów na właściwym miejscu, liczba właściwych kolorów
            na złym miejscu).
        available_colors (list[str]): Lista dostępnych kolorów w grze.
        code_length (int): Długość kodu do odgadnięcia.
        set_of_answers (list[list[str]]): Pełny zbiór wszystkich możliwych kombinacji.
        new_set_of_colors (list[list[str]]): Aktualny przefiltrowany zbiór możliwych
            odpowiedzi po uwzględnieniu podpowiedzi.
        check_colors (list[str]): Aktualne przypuszczenie bota.
        check_helps (list[tuple[int, int]]): Lista wszystkich możliwych wyników
            sprawdzenia w formacie (właściwe miejsce, złe miejsce).
    """

    def __init__(self, logic_answer: tuple[int, int]) -> None:
        """Inicjalizuje bota z początkową odpowiedzią logiki gry.

        Args:
            logic_answer (tuple[int, int]): Początkowa odpowiedź logiki w formacie
                (liczba kolorów na właściwym miejscu, liczba właściwych kolorów
                na złym miejscu).
        """
        self.logic_answer = logic_answer

        logic = MastermindLogic()
        self.available_colors = logic.available_colors
        self.code_length = logic.code_length

        self.set_of_answers = [
            list(p) for p in itertools.product(self.available_colors, repeat=self.code_length)
        ]
        self.new_set_of_colors = list(self.set_of_answers)
        self.check_colors = ['Red', 'Red', 'Orange', 'Orange']

        self.check_helps = [
            (h, t)
            for h in range(self.code_length + 1)
            for t in range(self.code_length + 1)
            if h + t <= self.code_length
        ]

    def check(self, guess: list[str], target: list[str]) -> tuple[int, int]:
        """Sprawdza przypuszczenie względem docelowej kombinacji.

        Zlicza liczbę kolorów na właściwym miejscu oraz liczbę właściwych
        kolorów na złym miejscu.

        Args:
            guess (list[str]): Przypuszczenie — lista kolorów o długości code_length.
            target (list[str]): Cel — lista kolorów o długości code_length.

        Returns:
            tuple[int, int]: Krotka (correct_place, wrong_place), gdzie:
                - correct_place — liczba kolorów na właściwym miejscu,
                - wrong_place — liczba właściwych kolorów na złym miejscu.
        """
        correct_place = 0
        target_rest = []
        guess_rest = []

        for target_color, guess_color in zip(target, guess):
            if target_color == guess_color:
                correct_place += 1
            else:
                target_rest.append(target_color)
                guess_rest.append(guess_color)

        wrong_place = 0
        for color in guess_rest:
            if color in target_rest:
                wrong_place += 1
                target_rest.remove(color)

        return correct_place, wrong_place

    def restart_game(self, new_answer=None) -> None:
        """Resetuje stan bota do początkowego dla nowej gry.

        Przywraca pełny zbiór możliwych wariantów oraz początkowe przypuszczenie.
        Opcjonalnie aktualizuje odpowiedź logiki dla nowej rundy.

        Args:
            new_answer (tuple[int, int] | None): Nowa odpowiedź logiki dla
                kolejnej rundy. Jeśli None — logic_answer pozostaje bez zmian.
        """
        self.new_set_of_colors = list(self.set_of_answers)
        self.check_colors = ['Red', 'Red', 'Orange', 'Orange']
        if new_answer is not None:
            self.logic_answer = new_answer

    def get_a_check_to_logic(self) -> list[str]:
        """Zwraca aktualne przypuszczenie bota do przekazania do logiki gry.

        Returns:
            list[str]: Aktualne przypuszczenie bota — lista kolorów o długości code_length.
        """
        return self.check_colors

    def create_a_new_set_of_colors(self) -> None:
        """Filtruje zbiór możliwych odpowiedzi na podstawie ostatniej podpowiedzi.

        Pozostawia tylko te kombinacje, dla których wynik sprawdzenia aktualnego
        przypuszczenia zgadza się z odpowiedzią logiki gry (self.logic_answer).
        Należy wywoływać po otrzymaniu odpowiedzi od logiki na aktualne przypuszczenie.
        """
        self.new_set_of_colors = [
            candidate for candidate in self.new_set_of_colors
            if self.logic_answer == self.check(self.check_colors, candidate)
        ]

    def make_a_guess(self) -> None:
        """Wybiera kolejne przypuszczenie zgodnie z algorytmem minimax Knutha.

        Dla każdego możliwego przypuszczenia z pełnego zbioru oblicza najgorszy
        przypadek — maksymalną liczbę wariantów, która pozostanie po dowolnej
        odpowiedzi logiki. Wybiera przypuszczenie z najmniejszą taką wartością.
        Przy równości priorytet otrzymuje przypuszczenie należące do aktualnego
        zbioru możliwych odpowiedzi.

        Obliczenia są wykonywane równolegle przy użyciu multiprocessing.Pool,
        co znacząco przyspiesza działanie na maszynach wielordzeniowych.

        Wynik zapisywany jest w self.check_colors i dostępny przez
        get_a_check_to_logic().
        """
        if len(self.new_set_of_colors) == 1:
            self.check_colors = self.new_set_of_colors[0]
            return

        new_set_frozen = [list(c) for c in self.new_set_of_colors]
        new_set_set = [tuple(c) for c in self.new_set_of_colors]

        args = [
            (candidate, new_set_frozen, tuple(candidate) in new_set_set)
            for candidate in self.set_of_answers
        ]

        with Pool(processes=cpu_count()) as pool:
            results = pool.map(_evaluate_candidate, args)

        min_max_score = float('inf')
        maybe_a_guess = None

        for max_remaining, in_new_set, candidate in results:
            if max_remaining < min_max_score:
                min_max_score = max_remaining
                maybe_a_guess = candidate
            elif (
                max_remaining == min_max_score
                and in_new_set
                and (maybe_a_guess is None or tuple(maybe_a_guess) not in new_set_set)
            ):
                maybe_a_guess = candidate

        self.check_colors = maybe_a_guess