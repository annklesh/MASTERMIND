import json
import os


class StatsManager:
    """Menedżer statystyk odpowiedzialny za trwałą historię gier zapisaną w formacie JSON."""

    def __init__(self, filename: str = "game_history.json"):
        self.filename = filename
        # Domyślna struktura podzielona na tryby gry
        self.data: dict = {
            "PvC": {
                "total_games": 0,
                "wins": 0,
                "best_score": None,   # najmniejsza liczba prób gracza na złamanie kodu
            },
            "PvP": {
                "total_games": 0,
                "wins_setter": 0,     # wygrane Gracza 1 (ustawiającego kod)
                "wins_guesser": 0,    # wygrane Gracza 2 (odgadującego kod)
                "best_score": None,   # najlepszy wynik tylko dla osoby odgadującej
            },
            "CvP": {
                "total_games": 0,
                "wins": 0,
                "best_score": None,   # najmniejsza liczba prób bota na złamanie kodu
            },
            "history": [],            # płaski log każdej zakończonej gry
        }
        self.load_statistics()

    def load_statistics(self) -> None:
        """Wczytuje statystyki z pliku JSON na dysku."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                #print("[StatsManager] JSON file is corrupted — starting with empty statistics.")
                pass

    def save_statistics(self) -> None:
        """Zapisuje aktualne statystyki na dysku."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_game_result(
        self,
        game_mode: str,
        player_name: str,
        result: str,
        attempts: int,
    ) -> None:
        """Zapisuje wynik zakończonej rozgrywki.

        Argumenty:
            game_mode:   "PvC" | "CvP" | "PvP"
            player_name: Wyświetlana nazwa gracza lub bota
            result:      "WIN" / "LOSS"                dla PvC / CvP
                         "WIN_GUESSER" / "WIN_SETTER"  dla PvP
            attempts:    Liczba rund rozegranych w tej grze
        """
        # walidacja trybu, aby literówka nigdy po cichu nie uszkodziła danych
        if game_mode not in ("PvC", "PvP", "CvP"):
            print(f"[StatsManager] Nieznany tryb gry '{game_mode}' — wynik nie został zapisany.")
            return

        mode_data = self.data[game_mode]
        mode_data["total_games"] += 1

        if game_mode == "PvP":
            # PvP rozróżnia dwa typy wygranych
            if result == "WIN_GUESSER":
                mode_data["wins_guesser"] += 1
                if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                    mode_data["best_score"] = attempts
            elif result == "WIN_SETTER":
                mode_data["wins_setter"] += 1
        else:
            # Standardowa logika WIN / LOSS dla PvC i CvP
            if result == "WIN":
                mode_data["wins"] += 1
                if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                    mode_data["best_score"] = attempts
                
        new_entry = {
            "game_mode": game_mode,
            "player": player_name,
            "result": result,
            "attempts": attempts,
        }
        self.data["history"].append(new_entry)
        self.save_statistics()