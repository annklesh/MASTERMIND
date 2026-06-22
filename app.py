import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from view.game_window import MastermindNeonUI
from logic.game_logic import MastermindLogic
from game_stats import StatsManager
from bot.game_bot import GameBot

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Failed to disconnect.*")
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"

class SecretCodeDialog(QDialog):
    """Okno dialogowe do wizualnego wyboru tajnego kodu przez gracza."""

    def __init__(self, parent: MastermindNeonUI, add_glow_method) -> None:
        """Inicjalizuje okno dialogowe wyboru kodu."""
        super().__init__(parent)
        self.add_glow_method = add_glow_method
        self.setWindowTitle("Set Secret Code")
        self.setFixedSize(400, 310)

        self.setStyleSheet("""
            QDialog { background-color: #0d0e15; border: 2px solid #1f2336; border-radius: 12px; }
            QLabel  { font-family: 'Segoe UI', sans-serif; color: #a0aec0; font-size: 14px; }
        """)

        self.color_mapping: dict[str, str] = {
            "#a855f7": "Purple",
            "#3b82f6": "Blue",
            "#22c55e": "Green",
            "#eab308": "Yellow",
            "#ea580c": "Orange",
            "#ef4444": "Red",
        }
        self.selected_colors: list[str] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("SELECT 4 COLORS FOR THE SECRET CODE:")
        title_label.setStyleSheet(
            "color: #ff007f; font-weight: bold; font-size: 13px; letter-spacing: 1px;"
        )
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(15)
        self.slots: list[QFrame] = []
        for _ in range(4):
            slot = QFrame()
            slot.setFixedSize(40, 40)
            slot.setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )
            preview_layout.addWidget(slot)
            self.slots.append(slot)
        layout.addLayout(preview_layout)

        palette_layout = QHBoxLayout()
        palette_layout.setSpacing(12)
        for color_hex in self.color_mapping:
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color_hex}; border: none; border-radius: 18px; }}"
                f"QPushButton:hover {{ border: 2px solid #ffffff; }}"
            )
            self.add_glow_method(btn, color_hex, radius=10)
            btn.clicked.connect(lambda checked=False, c=color_hex: self._handle_color_click(c))
            palette_layout.addWidget(btn)
        layout.addLayout(palette_layout)

        self.btn_backspace = QPushButton("⌫ Undo")
        self.btn_backspace.setEnabled(False)
        self.btn_backspace.setFixedSize(110, 30)
        self.btn_backspace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backspace.setStyleSheet("""
            QPushButton {
                background-color: #1f2336; color: #4a5568;
                font-weight: bold; border-radius: 6px; border: 1px solid #2d3748;
            }
            QPushButton:enabled {
                background-color: #2d3748; color: #a0aec0; border: 1px solid #4a5568;
            }
        """)
        self.btn_backspace.clicked.connect(self._handle_backspace)
        layout.addWidget(self.btn_backspace, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_confirm = QPushButton("CONFIRM CODE")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.setFixedSize(180, 40)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #1f2336; color: #4a5568;
                font-weight: bold; border-radius: 8px; border: 1px solid #2d3748;
            }
            QPushButton:enabled {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a8a, stop:1 #6d28d9);
                color: white; border: none;
            }
        """)
        self.btn_confirm.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirm, alignment=Qt.AlignmentFlag.AlignCenter)

    def _handle_color_click(self, color_hex: str) -> None:
        """Dodaje wybrany kolor do sekwencji kodu szyfrującego."""
        if len(self.selected_colors) < 4:
            self.selected_colors.append(color_hex)
            idx = len(self.selected_colors) - 1
            self.slots[idx].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 20px;"
            )
            self.add_glow_method(self.slots[idx], color_hex, radius=10)
            self.btn_backspace.setEnabled(True)

            if len(self.selected_colors) == 4:
                self.btn_confirm.setEnabled(True)

    def _handle_backspace(self) -> None:
        """Usuwa ostatnio wybrany kolor z podglądu."""
        if self.selected_colors:
            self.selected_colors.pop()
            idx = len(self.selected_colors)
            self.slots[idx].setGraphicsEffect(None)
            self.slots[idx].setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )
            self.btn_confirm.setEnabled(False)
            self.btn_backspace.setEnabled(bool(self.selected_colors))

    def get_code(self) -> list[str]:
        """Zwraca ostatecznie skompletowany kod szyfrujący dla logiki gry."""
        return [self.color_mapping[c] for c in self.selected_colors]


class GameManager:
    """Główny kontroler aplikacji Mastermind łączący interfejs użytkownika z logiką gry."""

    def __init__(self) -> None:
        """Inicjalizuje główne komponenty aplikacji i menedżerów."""
        self.ui: MastermindNeonUI = MastermindNeonUI()
        self.logic: MastermindLogic = MastermindLogic()
        self.stats: StatsManager = StatsManager()
        self.bot: GameBot = GameBot(logic_answer=(0, 0))

        self.current_mode: str | None = None
        self.current_round: int = 1
        self.max_rounds: int = 10

        self.setup_connections()
        self.update_stats_on_screen()

    def update_stats_on_screen(self) -> None:
        """Aktualizuje panel statystyk na ekranie gry dla trybów Solo oraz PVP."""
        if self.current_mode == "PvP":
            pvp_data = self.stats.data.get("PvP", {"total_games": 0, "wins_setter": 0, "wins_guesser": 0, "best_score": None})
            self.ui.game_screen.label_games_val.setText(str(pvp_data.get("total_games", 0)))
            self.ui.game_screen.label_setter_wins_val.setText(str(pvp_data.get("wins_setter", 0)))
            self.ui.game_screen.label_guesser_wins_val.setText(str(pvp_data.get("wins_guesser", 0)))
            best_score = pvp_data.get("best_score")
            self.ui.game_screen.label_guesser_best_val.setText(str(best_score) if best_score is not None else "-")
            return

        mode = self.current_mode if self.current_mode in ("PvC", "CvP") else "PvC"
        mode_data = self.stats.data.get(mode, {"total_games": 0, "wins": 0, "best_score": None})

        self.ui.game_screen.label_games_val.setText(str(mode_data.get("total_games", 0)))
        self.ui.game_screen.label_wins_val.setText(str(mode_data.get("wins", 0)))
        best_score = mode_data.get("best_score")
        self.ui.game_screen.label_best_val.setText(str(best_score) if best_score is not None else "-")

    def setup_connections(self) -> None:
        """Łączy sygnały interfejsu z odpowiednimi metodami kontrolera."""
        self.ui.menu_screen.btn_player_vs_comp.clicked.connect(self.start_player_vs_comp)
        self.ui.menu_screen.btn_comp_vs_player.clicked.connect(self.start_comp_vs_player)
        self.ui.menu_screen.btn_player_vs_player.clicked.connect(self.start_player_vs_player)
        self.ui.game_screen.btn_check_turn.clicked.connect(self.handle_check_button)

    def _disconnect_game_buttons(self) -> None:
        """Bezpiecznie odłącza stare połączenia przycisków przed zmianą trybu."""
        for btn in (self.ui.game_screen.btn_new_game, self.ui.game_screen.btn_main_menu):
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass

    def start_player_vs_comp(self) -> None:
        """Inicjuje tryb rozgrywki Gracz vs Komputer (PvC)."""
        self.current_mode = "PvC"
        self.current_round = 1

        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.ui.game_screen.setup_ui_for_bot_mode(False)
        self.ui.game_screen.set_pvp_mode(False)
        self.update_stats_on_screen()

        self.logic.secret_code = self.logic.generate_secret_code()

        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)

    def start_comp_vs_player(self) -> None:
        """Inicjuje tryb rozgrywki Komputer vs Gracz (CvP)."""
        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.current_mode = "CvP"
        self.ui.game_screen.set_pvp_mode(False)
        self.update_stats_on_screen()
        
        self.ui.game_screen.setup_ui_for_bot_mode(True)

        dialog = SecretCodeDialog(self.ui, self.ui.add_glow_effect)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player_secret = dialog.get_code()
            self.logic.secret_code = player_secret
            self.current_round = 1
            self.bot.restart_game(new_answer=(0, 0))
            self.execute_bot_turn()
        else:
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)

    def start_player_vs_player(self) -> None:
        """Inicjuje tryb rozgrywki Gracz vs Gracz (PvP)."""
        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.ui.game_screen.setup_ui_for_bot_mode(False)
        self.current_mode = "PvP"
        self.ui.game_screen.set_pvp_mode(True)
        self.update_stats_on_screen()

        dialog = SecretCodeDialog(self.ui, self.ui.add_glow_effect)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player_secret = dialog.get_code()
            self.logic.secret_code = player_secret
            self.current_round = 1
        else:
            self.ui.change_screen(0)

    def execute_bot_turn(self) -> None:
        """Obsługuje pełną sekwencję wykonania ruchu przez bota."""
        self.bot.make_a_guess()
        bot_guess_string = self.bot.get_a_check_to_logic()

        black_pegs, white_pegs = self.logic.check_guess(bot_guess_string)

        self.bot.logic_answer = (black_pegs, white_pegs)
        self.bot.create_a_new_set_of_colors()

        row_index = self.current_round - 1
        self.ui.game_screen.update_board_row(row_index, bot_guess_string, (black_pegs, white_pegs))

        if black_pegs == 4:
            self.stats.add_game_result("CvP", "Bot", "WIN", self.current_round)
            self.update_stats_on_screen()
            self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
            QMessageBox.information(
                self.ui, "Game Over",
                f"Bot cracked your code in {self.current_round} attempt(s)!"
            )
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)
            return

        elif self.current_round >= self.max_rounds:
            self.stats.add_game_result("CvP", "Bot", "LOSS", self.current_round)
            self.update_stats_on_screen()
            self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
            QApplication.processEvents()
            QMessageBox.information(self.ui, "Game Over", "You won! Bot failed to crack your code.")
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)
            return

        self.current_round += 1

    def handle_check_button(self) -> None:
        """Przetwarza ruch gracza po zatwierdzeniu wybranej kombinacji."""
        if self.current_mode == "PvC":
            user_guess = self.ui.game_screen.get_current_colors()
            if len(user_guess) < 4:
                QMessageBox.warning(self.ui, "Warning", "Select 4 colors first!")
                return

            print(f"\n=== PvC RUNDA №{self.current_round} ===")
            print(f"Wprowadzony kod: {user_guess}")

            black_pegs, white_pegs = self.logic.check_guess(user_guess)

            print(f"Wynik -> Czarne: {black_pegs}, Białe: {white_pegs}")
            print("====================================")

            row_index = self.current_round - 1
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()

            if black_pegs == 4:
                self.stats.add_game_result("PvC", "Player 1", "WIN", self.current_round)
                self.update_stats_on_screen()
                self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
                QApplication.processEvents()
                QMessageBox.information(
                    self.ui, "Victory!",
                    f"Victory! Code cracked in {self.current_round} attempt(s)."
                )
                self.ui.change_screen(0)
                return

            elif self.current_round >= self.max_rounds:
                self.stats.add_game_result("PvC", "Player 1", "LOSS", self.current_round)
                self.update_stats_on_screen()
                self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
                QApplication.processEvents()
                QMessageBox.information(self.ui, "Game Over", "Out of attempts. The computer wins!")
                self.ui.change_screen(0)
                return

            self.current_round += 1

        elif self.current_mode == "CvP":
            self.execute_bot_turn()

        elif self.current_mode == "PvP":
            user_guess = self.ui.game_screen.get_current_colors()
            if len(user_guess) < 4:
                QMessageBox.warning(self.ui, "Warning", "Select 4 colors first!")
                return

            print(f"\n=== PvP RUNDA №{self.current_round} ===")
            print(f"Gracz 2 wpisał: {user_guess}")

            black_pegs, white_pegs = self.logic.check_guess(user_guess)

            print(f"Wynik -> Czarne: {black_pegs}, Białe: {white_pegs}")
            print("====================================")

            row_index = self.current_round - 1
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()

            if black_pegs == 4:
                self.stats.add_game_result("PvP", "Player 2", "WIN_GUESSER", self.current_round)
                self.update_stats_on_screen()
                self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
                QApplication.processEvents()
                QMessageBox.information(
                    self.ui, "Game Over",
                    f"Codebreaker wins! Code cracked in {self.current_round} attempt(s)."
                )
                self.ui.change_screen(0)
                return

            elif self.current_round >= self.max_rounds:
                self.stats.add_game_result("PvP", "Player 1", "WIN_SETTER", self.current_round)
                self.update_stats_on_screen()
                self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
                QApplication.processEvents()
                QMessageBox.information(
                    self.ui, "Game Over",
                    "Codemaker wins! Codebreaker is out of attempts."
                )
                self.ui.change_screen(0)
                return

            self.current_round += 1

    def return_to_main_menu(self) -> None:
        """Wychodzi z obecnej gry do menu głównego."""
        self.ui.change_screen(0)

    def restart_current_mode(self) -> None:
        """Szybki restart obecnego trybu gry po kliknięciu 'New Game'."""
        if self.current_mode == "PvC":
            self.start_player_vs_comp()
        elif self.current_mode == "CvP":
            self.start_comp_vs_player()
        elif self.current_mode == "PvP":
            self.start_player_vs_player()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = GameManager()
    main_window.ui.show()
    sys.exit(app.exec())