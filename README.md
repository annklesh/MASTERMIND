# MASTERMIND
Projekt zespołowy. Gra logiczna Mastermind.

## 1. Środowisko i wymagane biblioteki

* **Interpreter**: Python (wersja >= 3.6)
* **Biblioteki zewnętrzne**: `PySide6`
* **Biblioteki standardowe**: `itertools`, `collections`, `multiprocessing`, `random`, `sys`, `os`
  
### Instalacja zależności:
```bash
pip install PySide6
```
---
## 2. Instrukcja uruchomienia prototypu

### Szybkie uruchomienie automatyczne:
Skrypty automatycznie tworzą środowisko wirtualne `venv`, instalują wymagane biblioteki i włączają grę.

* **System Windows**: Kliknij dwukrotnie plik `start_windows.bat`
* **System Linux / macOS**: Przed pierwszym uruchomieniem nadaj uprawnienia skryptowi, a następnie go odpal:
```bash
chmod +x start_linux.sh
./start_linux.sh
```
### Uruchomienie tradycyjne (Ręczne):
1. Otwórz terminal w głównym katalogu projektu.
2. Wpisz i zatwierdź komendę:

```bash
python app.py
```
---
## 3. Instrukcja użytkowania (Zasady Gry)

* **Cel gry**: Odgadnięcie ukrytego 4-kolorowego kodu w maksymalnie 10 próbach. Kolory w kodzie mogą się powtarzać.
* **Obsługa**: Wybierz kolory z dolnej palety, a następnie zatwierdź pełny wiersz przyciskiem `Check Code`. Użyj przycisku `⌫` (Backspace), aby cofnąć ostatni wybór.

### System podpowiedzi (Informacja zwrotna):
Po każdym ruchu obok wiersza pojawiają się kołki kontrolne:

* **Czarne kropki**: Wskazują prawidłowy kolor na właściwym miejscu.
* **Białe kropki**: Wskazują prawidłowy kolor, ale na błędnym miejscu.

### Dostępne tryby rozgrywki:
1. **Player vs Bot**: Gracz próbuje odgadnąć losowy kod wygenerowany przez komputer.
2. **Player vs Player**: Gracz 1 ustawia kod w ukrytym oknie dialogowym, a Gracz 2 odgaduje go na planszy.
3. **Bot vs Player**: Gracz definiuje kod, a Bot (algorytm Minimax Knutha) automatycznie go odgaduje.
---
## 4. Planowany diagram klas UML gotowej aplikacji

```mermaid
classDiagram
    class GameManager {
        +stats: StatsManager
        +current_round: int
        +max_rounds: int
        +current_mode: str
        +__init__(self, ui_window)
        #_connect_signals(self)
        +start_player_vs_comp(self)
        +start_comp_vs_player(self)
        +start_player_vs_player(self)
        +handle_check_button(self)
    }

    class MastermindLogic {
        +available_colors: list
        +code_length: int
        +secret_code: list
        +__init__(self)
        +generate_secret_code(self) -> list
        +set_secret_code(self, custom_code: list) -> None
        +check_guess(self, guess: list) -> tuple
    }

    class GameBot {
        +logic_answer: tuple
        +available_colors: list
        +code_length: int
        +set_of_answers: list
        +new_set_of_colors: list
        +check_colors: list
        +check_helps: list
        +__init__(self, logic_answer: tuple)
        +check(self, guess: list, target: list) -> tuple
        +restart_game(self, new_answer: tuple) -> None
        +get_a_check_to_logic(self) -> list
        +create_a_new_set_of_colors(self) -> None
        +make_a_guess(self) -> None
    }

    class MastermindNeonUI {
        +menu_screen: MainMenu
        +game_screen: GameScreen
        +__init__(self)
        +change_screen(self, index: int) -> None
    }

    class MainMenu {
        +btn_player_vs_comp: QPushButton
        +btn_player_vs_player: QPushButton
        +btn_comp_vs_player: QPushButton
        +__init__(self)
    }

    class GameScreen {
        +btn_check_turn: QPushButton
        +__init__(self)
        +get_current_colors(self) -> list
        +update_board_row(self, row: int, colors: list, pegs: tuple) -> None
        +reset_current_selection(self) -> None
    }

    GameManager --> MastermindNeonUI : ui
    GameManager --> MastermindLogic : logic
    GameManager --> GameBot : bot
    GameBot --> MastermindLogic : używa ustawień
    MastermindNeonUI *-- MainMenu : menu_screen
    MastermindNeonUI *-- GameScreen : game_screen
