class StatsManager:
    
    """
    Wersja tymczasowa modułu statystyk do testów jednostkowych logiki gry.
    
    W kolejnym etapie projektu klasa zostanie rozbudowana o pełną strukturę
    pliku JSON oraz obsługę trzech wymaganych trybów rozgrywki.
    """
    
    def __init__(self):
        self.history_file = "game_history.txt" 
    def save_game_result(self, won: bool, rounds: int) -> None:

        with open(self.history_file, "a", encoding="utf-8") as f:
            status = "Wygrana" if won else "Przegrana"
            f.write(f"Status: {status}, Rundy: {rounds}\n")
        print("Statystyki zostały zapisane!")

