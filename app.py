import sys
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from view.game_window import MastermindNeonUI
from logic.game_logic import MastermindLogic
from game_stats import StatsManager
from bot.game_bot import GameBot


class SecretCodeDialog(QDialog):
    """Dialog window for visually selecting the secret code."""

    def __init__(self, parent, add_glow_method):
        super().__init__(parent)
        self.add_glow_method = add_glow_method
        self.setWindowTitle("Set Secret Code")
        # FIX #3: increased height to accommodate the new backspace button
        self.setFixedSize(400, 310)

        self.setStyleSheet("""
            QDialog { background-color: #0d0e15; border: 2px solid #1f2336; border-radius: 12px; }
            QLabel  { font-family: 'Segoe UI', sans-serif; color: #a0aec0; font-size: 14px; }
        """)

        self.color_mapping = {
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

        # Preview slots for the currently selected code
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

        # Color palette
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

        # FIX #3: Backspace button — lets the user undo the last colour pick
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

        # Confirm button
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
        """Adds the chosen colour to the next free preview slot."""
        if len(self.selected_colors) < 4:
            self.selected_colors.append(color_hex)
            idx = len(self.selected_colors) - 1
            self.slots[idx].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 20px;"
            )
            self.add_glow_method(self.slots[idx], color_hex, radius=10)
            self.btn_backspace.setEnabled(True)   # FIX #3: enable undo as soon as ≥1 colour chosen

            if len(self.selected_colors) == 4:
                self.btn_confirm.setEnabled(True)

    def _handle_backspace(self) -> None:
        """Removes the last chosen colour from the preview (FIX #3)."""
        if self.selected_colors:
            self.selected_colors.pop()
            idx = len(self.selected_colors)
            self.slots[idx].setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )
            self.btn_confirm.setEnabled(False)
            self.btn_backspace.setEnabled(bool(self.selected_colors))

    def get_code(self) -> list[str]:
        """Returns the selected colours translated to names for game logic."""
        return [self.color_mapping[c] for c in self.selected_colors]


class GameManager:
    def __init__(self, ui_window):
        self.ui = ui_window
        self.logic = MastermindLogic()
        self.stats = StatsManager()
        self.current_round = 1
        self.max_rounds = 10
        self.current_mode: str | None = None
        self.bot: GameBot | None = None

        self._connect_signals()
        self.update_stats_on_screen()

    def update_stats_on_screen(self) -> None:
        """Updates the stats panel according to the current game mode."""
        # FIX #6: PvP stats are set to "-" manually in start_player_vs_player;
        # calling this method for PvP would incorrectly show PvC numbers.
        if self.current_mode == "PvP":
            return

        mode = self.current_mode if self.current_mode in ("PvC", "CvP") else "PvC"
        mode_data = self.stats.data.get(
            mode, {"total_games": 0, "wins": 0, "best_score": None}
        )

        total_games = mode_data.get("total_games", 0)
        wins = mode_data.get("wins", 0)
        best_score = mode_data.get("best_score")
        best_display = str(best_score) if best_score is not None else "-"

        self.ui.game_screen.label_games_val.setText(str(total_games))
        self.ui.game_screen.label_wins_val.setText(str(wins))
        self.ui.game_screen.label_best_val.setText(best_display)

    def _connect_signals(self) -> None:
        """Connects menu/game UI buttons to GameManager methods."""
        self.ui.menu_screen.btn_player_vs_comp.clicked.connect(self.start_player_vs_comp)
        self.ui.menu_screen.btn_comp_vs_player.clicked.connect(self.start_comp_vs_player)
        self.ui.menu_screen.btn_player_vs_player.clicked.connect(self.start_player_vs_player)
        self.ui.game_screen.btn_check_turn.clicked.connect(self.handle_check_button)

    def _disconnect_game_buttons(self) -> None:
        """Safely disconnects in-game button signals to prevent duplicate connections.
        FIX #4: replaced bare 'except:' with 'except RuntimeError:'.
        """
        for btn in (self.ui.game_screen.btn_new_game, self.ui.game_screen.btn_main_menu):
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass  # signal had no connections — harmless

    def start_player_vs_comp(self) -> None:
        """Classic mode: Player guesses the computer-generated code."""
        self.current_mode = "PvC"
        self.current_round = 1

        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.ui.game_screen.setup_ui_for_bot_mode(False)
        self.update_stats_on_screen()

        self.logic.secret_code = self.logic.generate_secret_code()
        # FIX #5: removed DEBUG print that exposed the secret code in the console

        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)

    def start_comp_vs_player(self) -> None:
        """Player sets the code; the bot attempts to guess it."""
        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.current_mode = "CvP"
        self.update_stats_on_screen()
        self.ui.game_screen.setup_ui_for_bot_mode(True)

        dialog = SecretCodeDialog(self.ui, self.ui.add_glow_effect)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player_secret = dialog.get_code()
            self.logic.secret_code = player_secret
            self.current_round = 1

            if self.bot is None:
                self.bot = GameBot(logic_answer=(0, 0))
            else:
                # FIX #7: was using keyword 'new_answer', inconsistent with the
                # 'logic_answer' attribute name used everywhere else.
                # Verify this matches the signature in bot/game_bot.py.
                self.bot.restart_game(logic_answer=(0, 0))

            self.execute_bot_turn()
        else:
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)

    def start_player_vs_player(self) -> None:
        """Player 1 sets the code; Player 2 guesses on the board."""
        self._disconnect_game_buttons()
        self.ui.game_screen.btn_new_game.clicked.connect(self.restart_current_mode)
        self.ui.game_screen.btn_main_menu.clicked.connect(self.return_to_main_menu)

        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()
        self.ui.game_screen.reset_secret_code_panel()
        self.ui.game_screen.setup_ui_for_bot_mode(False)
        self.current_mode = "PvP"

        self.ui.game_screen.label_games_val.setText("-")
        self.ui.game_screen.label_wins_val.setText("-")
        self.ui.game_screen.label_best_val.setText("-")

        dialog = SecretCodeDialog(self.ui, self.ui.add_glow_effect)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player_secret = dialog.get_code()
            self.logic.secret_code = player_secret
            self.current_round = 1
        else:
            self.ui.change_screen(0)

    def execute_bot_turn(self) -> None:
        """Executes one automated bot turn and evaluates the game state."""
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
            QMessageBox.information(
                self.ui, "Game Over",
                f"Bot cracked your code in {self.current_round} attempt(s)!"
            )
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)
            return

        elif self.current_round >= self.max_rounds:
            # Safety guard — Knuth's minimax always solves in ≤5 guesses;
            # this branch should never be reached in practice.
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
        """Handles the 'Check Code' button click on the game board."""
        if self.current_mode == "PvC":
            user_guess = self.ui.game_screen.get_current_colors()
            if len(user_guess) < 4:
                QMessageBox.warning(self.ui, "Warning", "Select 4 colors first!")
                return

            black_pegs, white_pegs = self.logic.check_guess(user_guess)

            row_index = self.current_round - 1
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()

            if black_pegs == 4:
                self.stats.add_game_result("PvC", "Player 1", "WIN", self.current_round)
                self.update_stats_on_screen()
                QMessageBox.information(
                    self.ui, "Victory!",
                    f"You cracked the code in {self.current_round} attempt(s)!"
                )
                self.ui.change_screen(0)
                return

            elif self.current_round >= self.max_rounds:
                # FIX #1: was saving "WIN" even though the player lost (ran out of attempts).
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

            black_pegs, white_pegs = self.logic.check_guess(user_guess)

            row_index = self.current_round - 1
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()

            if black_pegs == 4:
                # FIX #2: PvP results were never saved to stats at all.
                self.stats.add_game_result("PvP", "Player 2", "WIN_GUESSER", self.current_round)
                QMessageBox.information(
                    self.ui, "Game Over",
                    f"Player 2 wins! Code cracked in {self.current_round} attempt(s)."
                )
                self.ui.change_screen(0)
                return

            elif self.current_round >= self.max_rounds:
                # FIX #2: PvP results were never saved to stats at all.
                self.stats.add_game_result("PvP", "Player 1", "WIN_SETTER", self.current_round)
                self.ui.game_screen.reveal_secret_code(self.logic.secret_code)
                QApplication.processEvents()
                QMessageBox.information(
                    self.ui, "Game Over",
                    "Player 1 wins! Player 2 is out of attempts."
                )
                self.ui.change_screen(0)
                return

            self.current_round += 1

    def return_to_main_menu(self) -> None:
        """Returns to the main menu from the current game."""
        self.ui.change_screen(0)

    def restart_current_mode(self) -> None:
        """Restarts the current game mode when 'New Game' is clicked."""
        if self.current_mode == "PvC":
            self.start_player_vs_comp()
        elif self.current_mode == "CvP":
            self.start_comp_vs_player()
        elif self.current_mode == "PvP":
            self.start_player_vs_player()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MastermindNeonUI()
    manager = GameManager(main_window)
    main_window.show()
    sys.exit(app.exec())
