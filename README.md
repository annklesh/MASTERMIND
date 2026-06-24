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

_**Uwaga!** Kolejność kropek kontrolnych jest losowa i nie odpowiada pozycji kolorów w Twojej próbie. Kropki informują jedynie o ogólnej liczbie trafień._

### Dostępne tryby rozgrywki:
1. **Player vs Bot**: Gracz próbuje odgadnąć losowy kod wygenerowany przez komputer.
2. **Player vs Player**: Gracz 1 ustawia kod w ukrytym oknie dialogowym, a Gracz 2 odgaduje go na planszy.
3. **Bot vs Player**: Gracz definiuje kod, a Bot (algorytm Minimax Knutha) automatycznie go odgaduje.
---
## 4. Diagram klas UML gotowej aplikacji

```mermaid
classDiagram
direction TB

class GameManager {
    - MastermindNeonUI ui
    - MastermindLogic logic
    - StatsManager stats
    - GameBot bot
    - Optional~str~ current_mode
    - int current_round
    - int max_rounds
    + update_stats_on_screen()
    + setup_connections()
    - _disconnect_game_buttons()
    + start_player_vs_comp()
    + start_comp_vs_player()
    + start_player_vs_player()
    + execute_bot_turn()
    + handle_check_button()
    + return_to_main_menu()
    + restart_current_mode()
}

class MastermindLogic {
    - list~str~ available_colors
    - int code_length
    - list~str~ secret_code
    + generate_secret_code() list~str~
    + set_secret_code(custom_code)
    + check_guess(guess) tuple
}

class GameBot {
    - tuple logic_answer
    - list~str~ available_colors
    - int code_length
    - list set_of_answers
    - list new_set_of_colors
    - list~str~ check_colors
    + check(guess, target) tuple
    + restart_game(new_answer)
    + get_a_check_to_logic() list~str~
    + create_a_new_set_of_colors()
    + make_a_guess()
}

class StatsManager {
    - str filename
    - dict data
    + load_statistics()
    + save_statistics()
    + add_game_result(game_mode, player_name, result, attempts)
}

class MastermindNeonUI {
    - QStackedWidget stacked_widget
    - GameScreen game_screen
    - MainMenu menu_screen
    + change_screen(index)
    + add_glow_effect(widget, color_hex, radius)
}

class MainMenu {
    - Callable change_screen_callback
    - Optional~Callable~ set_pvp_callback
    - QPushButton btn_player_vs_comp
    - QPushButton btn_player_vs_player
    - QPushButton btn_comp_vs_player
    - _handle_mode_selection(is_pvp)
}

class GameScreen {
    - dict color_mapping
    - list~str~ selected_colors
    - list board_pegs
    - list board_hints
    - list current_slots
    + set_pvp_mode(is_pvp)
    + get_current_colors() list~str~
    + reset_current_selection()
    + update_board_row(row_index, colors, feedback)
    + reset_board()
    + setup_ui_for_bot_mode(is_bot_mode)
    + reveal_secret_code(secret_code)
    + reset_secret_code_panel()
}

class SecretCodeDialog {
    - dict color_mapping
    - list~str~ selected_colors
    - list slots
    + get_code() list~str~
    - _handle_color_click(color_hex)
    - _handle_backspace()
}

GameManager *-- MastermindNeonUI : controls UI
GameManager *-- MastermindLogic : uses logic
GameManager *-- StatsManager : saves statistics
GameManager *-- GameBot : controls bot
GameManager ..> SecretCodeDialog : opens dialog

MastermindNeonUI *-- MainMenu : contains
MastermindNeonUI *-- GameScreen : contains

MainMenu ..> GameScreen : sets PvP mode
GameBot ..> MastermindLogic : uses game settings
```
---
## 4. Zaktualizowany plan działania 
W celu dokończenia aplikacji i uruchomienia wszystkich zaplanowanych modułów, w najbliższych tygodniach skupimy się na następujących zadaniach:
* Uruchomienie paneli bocznych interfejsu: Naprawa i aktywacja bocznych sekcji okna gry w PySide6, aby prawidłowo reagowały na działania użytkownika i dynamicznie dopasowywały się do ekranu. 
* Stworzenie modułu statystyk: Napisanie pliku game_stats.py, który będzie odpowiadał za zbieranie danych o o rozgrywkach (np. liczba ruchów, wygrane/przegrane) oraz zapisywanie tych informacji w strukturze pliku game_history.txt..
* Wizualne wdrożenie panelu statystyk: Zaprojektowanie dedykowanego okna lub zakładki w menu graficznym aplikacji, która pobierze dane z pliku tekstowego i wyświetli je użytkownikowi w postaci estetycznej tabeli lub podsumowania.
* Pełna integracja trybów gry: Ostateczne spięcie logiki bota oraz okien dialogowych. 
* Testowanie i optymalizacja: Przeprowadzenie testów całej aplikacji w celu eliminacji błędów, sprawdzenie stabilności działania bota oraz uporządkowanie struktury kodu przed oddaniem projektu. 
---
## 5. Zaktualizowany plan funkcjonalności gotowej aplikacji
Zgodnie z pierwotnymi założeniami projektu, gotowa aplikacja będzie w pełni funkcjonalną grą desktopową Mastermind z interfejsem graficznym PySide6: 
* Trzy niezależne tryby rozgrywki: Pełna obsługa trybów Człowiek vs Komputer, Człowiek vs Człowiek oraz Komputer vs Człowiek (w którym komputer logicznie odgaduje szyfr użytkownika). 
* Menu główne: W pełni responsywne okno startowe pozwalające na wygodny wybór jednego z trzech trybów rozgrywki. 
* Kompletna i dynamiczna plansza gry: Tradycyjna wirtualna plansza z widocznymi rzędami na próby oraz mniejszymi polami na kołki sygnalizacyjne (czarne i białe). 
* Panel statystyk i historii: Działający moduł zapisu wyników, który trwale przechowuje historię rozegranych partii na dysku i wyświetla najlepsze rezultaty bezpośrednio w oknie gry.
