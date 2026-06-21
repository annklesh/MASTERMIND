import json
import os


class StatsManager:
    """Stats manager responsible for persistent game history stored as JSON."""

    def __init__(self, filename: str = "game_history.json"):
        self.filename = filename
        # Default structure split by game mode
        self.data: dict = {
            "PvC": {
                "total_games": 0,
                "wins": 0,
                "best_score": None,   # fewest attempts by the player to crack the code
            },
            "PvP": {
                "total_games": 0,
                "wins_setter": 0,     # wins for Player 1 (code setter)
                "wins_guesser": 0,    # wins for Player 2 (guesser)
                "best_score": None,   # best score for the guesser only
            },
            "CvP": {
                "total_games": 0,
                "wins": 0,
                "best_score": None,   # fewest attempts for the bot to crack the code
            },
            "history": [],            # flat log of every completed game
        }
        self.load_statistics()

    def load_statistics(self) -> None:
        """Loads statistics from the JSON file on disk."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print("[StatsManager] JSON file is corrupted — starting with empty statistics.")

    def save_statistics(self) -> None:
        """Persists current statistics to disk."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_game_result(
        self,
        game_mode: str,
        player_name: str,
        result: str,
        attempts: int,
    ) -> None:
        """Records the outcome of a finished game.

        Args:
            game_mode:   "PvC" | "CvP" | "PvP"
            player_name: Display name of the player or bot
            result:      "WIN" / "LOSS"          for PvC / CvP
                         "WIN_GUESSER" / "WIN_SETTER"  for PvP
            attempts:    Number of rounds played in this game
        """
        # FIX #9: validate the mode so a typo never silently corrupts the data
        if game_mode not in ("PvC", "PvP", "CvP"):
            print(f"[StatsManager] Unknown game mode '{game_mode}' — result not saved.")
            return

        mode_data = self.data[game_mode]
        mode_data["total_games"] += 1

        if game_mode == "PvP":
            # FIX #8: the original comment was at wrong indentation (looked like dead code)
            # PvP distinguishes two win types
            if result == "WIN_GUESSER":
                mode_data["wins_guesser"] += 1
                if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                    mode_data["best_score"] = attempts
            elif result == "WIN_SETTER":
                mode_data["wins_setter"] += 1
            # Any other PvP result: total_games already incremented above

        else:
            # Standard WIN / LOSS logic for PvC and CvP
            if result == "WIN":
                mode_data["wins"] += 1
                if mode_data["best_score"] is None or attempts < mode_data["best_score"]:
                    mode_data["best_score"] = attempts
            # LOSS: total_games already incremented; wins and best_score stay unchanged

        new_entry = {
            "game_mode": game_mode,
            "player": player_name,
            "result": result,
            "attempts": attempts,
        }
        self.data["history"].append(new_entry)
        self.save_statistics()
