import json
import os

class StatsManager:
    """Menedżer statystyk odpowiedzialny za trwały zapis historii gier w formacie JSON."""
    
    def __init__(self, filename="game_history.json"):
        self.filename = filename
        # Domyślna struktura bazy danych z podziałem na niezależne tryby rozgrywki
        self.data = {
            "PvC": {
                "total_games": 0,
                "wins": 0,
                "best_score": None  # najmniejsza liczba prób gracza do złamania kodu
            },
            "PvP": {
                "total_games": 0,
                "wins_setter": 0,   # wygrane gracza, który ukrył kod (Gracz 1)
                "wins_guesser": 0,  # wygrane gracza, który zgadywał (Gracz 2)
                "best_score": None  # najlepszy wynik tylko dla zgadywającego
            },
            "CvP": {
                "total_games": 0,
                "wins": 0,
                "best_score": None  # najmniejsza liczba prób bota do złamania kodu
            },
            "history": []   # ogólny dziennik zdarzeń dla wszystkich rozegranych partii
        }
        self.load_statistics()

    def load_statistics(self):
        """Wczytuje statystyki z pliku JSON na dysku."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)
            except json.JSONDecodeError:
                print("Błąd pliku JSON, tworzenie nowej bazy danych.")

    def save_statistics(self):
        """Zapisuje aktualne statystyki na dysk."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def add_game_result(self, game_mode, player_name, result, attempts):
        """Rejestruje wynik dla konkretnego trybu gry."""
        # Weryfikacja, czy wskazany tryb gry istnieje w strukturze danych
        if game_mode in self.data:
            mode_data = self.data[game_mode]
            mode_data["total_games"] += 1
                
            if game_mode == "PvP":
            # Rozróżniamy dwa rodzaje wygranych
                if result == "WIN_GUESSER":
                    mode_data["wins_guesser"] += 1
                    if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                        mode_data["best_score"] = attempts
                elif result == "WIN_SETTER":
                    mode_data["wins_setter"] += 1
            else:
                # Standardowa logika dla PvC i CvP
                if result == "WIN":
                    mode_data["wins"] += 1
                    if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                        mode_data["best_score"] = attempts
        
        # Dodanie wpisu do ogólnej historii rozgrywek
        new_entry = {
            "game_mode": game_mode,
            "player": player_name,
            "result": result,
            "attempts": attempts
        }
        self.data["history"].append(new_entry)
        self.save_statistics()