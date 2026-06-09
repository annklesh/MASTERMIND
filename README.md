# MASTERMIND
Projekt zespołowy. Gra logiczna Mastermind.

## 1. Wymagane biblioteki i środowisko (Prerequisites)
Projekt opiera się na środowisku uruchomieniowym języka Python oraz zewnętrznym frameworku do obsługi interfejsu graficznego.
**Język programowania:** Python 3.8 lub nowszy
**Biblioteki zewnętrzne:** `PySide6`
**Biblioteki standardowe (wbudowane):** `itertools`, `collections`, `multiprocessing`, `random`, `sys`, `os`.

### Instalacja zależności:
Przed uruchomieniem projektu należy zainstalować bibliotekę PySide6 przy użyciu managera pakietów pip: pip install PySide6

## 2. Struktura plików i Instrukcja uruchomienia (Installation & Running)
Projekt został zorganizowany w sposób modułowy, dzieląc architekturę na logikę, bota oraz widok:

bot/                  # Pakiet obsługujący sztuczną inteligencję (GameBot)

logic/                # Pakiet mechaniki gry (MastermindLogic)

view/                # Pakiet przechowujący pliki interfejsu graficznego (widoki)
ты 
.gitignore            # Plik konfiguracyjny Gita do ignorowania m.in. cache i venv

README.md             # Dokumentacja projektu (ten plik)

app.py                # Główny punkt wejścia aplikacji (Main Execution File)

game_history.txt      # Plik tekstowy przeznaczony na zapis historii rozgrywek

game_stats.py         # Skrypt/Moduł odpowiedzialny za przetwarzanie statystyk

start_linux.sh        #Skrypt powłoki (Shell) do szybkiego uruchomienia na systemach Linux/macOS

start_windows.bat     #Plik wsadowy (Batch) do szybkiego uruchomienia na systemie Windows

**Krok po kroku, jak uruchomić prototyp:**
1. Sklonuj lub pobierz repozytorium na swój komputer.
2. Otwórz terminal / wiersz poleceń w głównym katalogu projektu (tam, gdzie znajduje się plik app.py).
3. Uruchom aplikację za pomocą następującej komendy: python app.py
**Szybkie uruchomienie za pomocą skryptów:**
1. Na systemie Windows: Kliknij dwukrotnie plik start_windows.bat
2. Na systemach Linux / macOS: Uruchom w terminalu skrypt poleceniem: ./start_linux.sh

## 3. Instrukcja obsługi i stan obecny prototypu (Usage Guide)
Aktywne funkcjonalności (Co już działa):
### Cyberpunk GUI (Pakiet view & app.py):
**Menu Główne:** Efektowny ekran startowy z animowanym neonowym napisem "MASTERMIND". Udostępnia przyciski wyboru trybów gry (Player vs Bot, Player vs Player, Bot vs Player). Kliknięcie dowolnego z nich płynnie przełącza widok na ekran planszy.

**Plansza Rozgrywki:** Zawiera przewijany obszar z 10 rzędami na próby odgadnięcia kodu, paletę 6 kolorów na dole oraz boczne panele zasad, statystyk i ukrytego kodu.

**Wprowadzanie ruchu użytkownika:** Klikanie kolorowych kulek w palecie powoduje dynamiczne dodawanie ich do sekcji "YOUR TURN" z zachowaniem odpowiedniego koloru HEX i efektu poświaty. Przycisk ⌫ (Backspace) poprawnie usuwa ostatnio wybrany kolor.
### Logika gry (Pakiet logic):
Klasa MastermindLogic posiada sprawny system losowania 4-elementowego kodu z puli 6 kolorów (generate_secret_code) oraz możliwość ręcznego ustawienia kodu (set_secret_code).
Metoda check_guess bezbłędnie porównuje propozycję kodu z sekretem, zwracając precyzyjną liczbę czarnych i białych kołków (informacja zwrotna).
### Algorytm AI Bota (Pakiet bot):
Gotowy zaawansowany bot realizujący algorytm Minimax Knutha. Dzięki zastosowaniu biblioteki multiprocessing, obliczenia kolejnych najlepszych strzałów bota są rozproszone na wiele rdzeni procesora, co zapewnia natychmiastowe działanie.
