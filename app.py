import sys
from PySide6.QtWidgets import QApplication,QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt
from view.game_window import MastermindNeonUI
from logic.game_logic import MastermindLogic
from game_stats import StatsManager
from bot.game_bot import GameBot

class SecretCodeDialog(QDialog):
    """Okno dialogowe do wizualnego wyboru tajnego kodu."""
    def __init__(self, parent, add_glow_method):
        super().__init__(parent)
        self.add_glow_method = add_glow_method
        self.setWindowTitle("Set Secret Code")
        self.setFixedSize(400, 260)

        self.setStyleSheet("""
            QDialog { background-color: #0d0e15; border: 2px solid #1f2336; border-radius: 12px; }
            QLabel { font-family: 'Segoe UI', sans-serif; color: #a0aec0; font-size: 14px; }
        """)

        self.color_mapping = {
            "#a855f7": "Purple", "#3b82f6": "Blue", "#22c55e": "Green", 
            "#eab308": "Yellow","#ea580c": "Orange","#ef4444": "Red"}
        self.selected_colors = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("SELECT 4 COLORS FOR THE SECRET CODE:")
        self.title_label.setStyleSheet("color: #ff007f; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Podgląd aktualnie wybranych slotów
        self.preview_layout = QHBoxLayout()
        self.preview_layout.setSpacing(15)
        self.slots = []
        for _ in range(4):
            slot = QFrame()
            slot.setFixedSize(40, 40)
            slot.setStyleSheet("background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;")
            self.preview_layout.addWidget(slot)
            self.slots.append(slot)
        layout.addLayout(self.preview_layout)

        # Paleta kolorów do klikania
        palette_layout = QHBoxLayout()
        palette_layout.setSpacing(12)
        for color_hex in self.color_mapping.keys():
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(f"QPushButton {{ background-color: {color_hex}; border: none; border-radius: 18px; }} QPushButton:hover {{ border: 2px solid #ffffff; }}")
            self.add_glow_method(btn, color_hex, radius=10)
            
            btn.clicked.connect(lambda checked=False, c=color_hex: self._handle_color_click(c))
            palette_layout.addWidget(btn)
        layout.addLayout(palette_layout)

        # Przycisk zatwierdzenia kodu
        self.btn_confirm = QPushButton("CONFIRM CODE")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.setFixedSize(180, 40)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton { background-color: #1f2336; color: #4a5568; font-weight: bold; border-radius: 8px; border: 1px solid #2d3748; }
            QPushButton:enabled { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1e3a8a, stop:1 #6d28d9); color: white; border: none; }
        """)
        self.btn_confirm.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirm, alignment=Qt.AlignmentFlag.AlignCenter)

    def _handle_color_click(self, color_hex: str) -> None:
        """Dodaje wybrany z palety kolor do wolnego slotu podglądu."""
        if len(self.selected_colors) < 4:
            self.selected_colors.append(color_hex)
            idx = len(self.selected_colors) - 1
            self.slots[idx].setStyleSheet(f"background-color: {color_hex}; border: none; border-radius: 20px;")
            self.add_glow_method(self.slots[idx], color_hex, radius=10)
            
            if len(self.selected_colors) == 4:
                self.btn_confirm.setEnabled(True)

    def get_code(self) -> list[str]:
        """Zwraca kod przetłumaczony na nazwy dla logiki."""
        return [self.color_mapping[c] for c in self.selected_colors]


class GameManager:
    def __init__(self, ui_window):
        self.ui = ui_window
        self.logic = MastermindLogic()
        self.stats = StatsManager()
        self.current_round = 1
        self.max_rounds = 10
        self.current_mode = None
        self.bot = None

        self._connect_signals()
        self.update_stats_on_screen()

    def update_stats_on_screen(self):
        """Aktualizuje panel statystyk na podstawie bocznego modułu i trybu."""
        mode = self.current_mode if self.current_mode in ["PvC", "CvP"] else "PvC"
        mode_data = self.stats.data.get(mode, {"total_games": 0, "wins": 0, "best_score": None})
        
        total_games = mode_data.get("total_games", 0)
        wins = mode_data.get("wins", 0)
        best_score = mode_data.get("best_score")
        if best_score is None:
            best_score = "-"

        self.ui.game_screen.label_games_val.setText(str(total_games))
        self.ui.game_screen.label_wins_val.setText(str(wins))
        self.ui.game_screen.label_best_val.setText(str(best_score))

    def _connect_signals(self):
        """Łączenie przycisków z UI do funkcji w tej klasie."""
        self.ui.menu_screen.btn_player_vs_comp.clicked.connect(self.start_player_vs_comp)
        self.ui.menu_screen.btn_comp_vs_player.clicked.connect(self.start_comp_vs_player)
        self.ui.menu_screen.btn_player_vs_player.clicked.connect(self.start_player_vs_player)
        self.ui.game_screen.btn_check_turn.clicked.connect(self.handle_check_button)

    def start_player_vs_comp(self):
        """Klasyczny tryb: Gracz zgaduje kod komputera."""
        print("Starting mode: Player vs Computer")
        self.current_mode = "PvC"
        self.current_round = 1

        self.ui.game_screen.reset_board()
        self.ui.game_screen.setup_ui_for_bot_mode(False)
        self.update_stats_on_screen()
        
        self.logic.secret_code = self.logic.generate_secret_code()
        print(f"DEBUG: Secret code is: {self.logic.secret_code}")
        
        self.ui.change_screen(1)

    def start_comp_vs_player(self):
        """Gracz wymyśla kod, a Bot zgaduje."""
        print("Starting mode: Computer vs Player")
        
        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()     
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
                self.bot.restart_game(new_answer=(0, 0))

            self.execute_bot_turn()
        else:
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)

    def start_player_vs_player(self):
        """Gracz 1 wymyśla kod, Gracz 2 zgaduje na planszy."""
        print("Starting mode: Player vs Player")
        
        self.ui.change_screen(1)
        self.ui.game_screen.reset_board()
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
            print(f"Secret code set by Player 1: {player_secret}")
        else:
            self.ui.change_screen(0)
            
    def execute_bot_turn(self):
        """Wykonuje automatyczną turę bota i sprawdza stan gry."""
        print(f"Bot's turn: {self.current_round}")
        
        self.bot.make_a_guess()
        bot_guess_string = self.bot.get_a_check_to_logic()
        
        black_pegs, white_pegs = self.logic.check_guess(bot_guess_string)
        print(f"Bot guessed: {bot_guess_string} | Result: Black={black_pegs}, White={white_pegs}")
        
        self.bot.logic_answer = (black_pegs, white_pegs)
        self.bot.create_a_new_set_of_colors()
        
        row_index = self.current_round - 1
        self.ui.game_screen.update_board_row(row_index, bot_guess_string, (black_pegs, white_pegs))
        
        if black_pegs == 4:
            # Bot odgadł kod -> przekazuje "WIN" i liczbę prób bota
            self.stats.add_game_result("CvP", "Bot", "WIN", self.current_round)
            self.update_stats_on_screen()

            QMessageBox.information(self.ui, "Game Over", f"Bot cracked your code in {self.current_round} attempts!")
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)
            return
            
        elif self.current_round >= self.max_rounds:
            # ZABEZPIECZENIE: Teoretycznie niemożliwe dla bota, dodane jako hamulec bezpieczeństwa 
            self.stats.add_game_result("CvP", "Bot", "LOSS", self.current_round)
            self.update_stats_on_screen()
            
            QMessageBox.information(self.ui, "Game Over", "You won! Bot failed to crack your code.")
            self.ui.game_screen.setup_ui_for_bot_mode(False)
            self.ui.change_screen(0)
            return
    
        self.current_round += 1

    def handle_check_button(self):
        """Co się dzieje po kliknięciu 'Check Code' na planszy."""
        if self.current_mode == "PvC":
            print(f"Player turn: {self.current_round}")
            
            user_guess = self.ui.game_screen.get_current_colors()
            if len(user_guess) < 4:
                QMessageBox.warning(self.ui, "Warning", "Select 4 colors first!")
                return 
            
            black_pegs, white_pegs = self.logic.check_guess(user_guess)
            print(f"Result: Black={black_pegs}, White={white_pegs}")
            
            row_index = self.current_round - 1 
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()
            
            if black_pegs == 4:
                print("Victory! Code cracked.")
                self.stats.add_game_result("PvC", "Player 1", "WIN", self.current_round)
                self.update_stats_on_screen()
                QMessageBox.information(self.ui, "Victory!", f"You cracked the code in {self.current_round} attempts!")
                self.ui.change_screen(0) 
                return
            
            elif self.current_round >= self.max_rounds:
                print("Game Over! Out of attempts.")
                self.stats.add_game_result("PvC", "Player 1", "WIN", self.current_round)
                self.update_stats_on_screen()
                QMessageBox.information(self.ui, "Game Over", "Out of attempts. The computer wins!")
                self.ui.change_screen(0) 
                return
            
            self.current_round += 1

        elif self.current_mode == "CvP":
            self.execute_bot_turn()

        elif self.current_mode == "PvP":
            print(f"Player 2 turn: {self.current_round}")
            
            user_guess = self.ui.game_screen.get_current_colors()

            if len(user_guess) < 4:
                QMessageBox.warning(self.ui, "Warning", "Select 4 colors first!")
                return 
            
            black_pegs, white_pegs = self.logic.check_guess(user_guess)
            
            row_index = self.current_round - 1 
            self.ui.game_screen.update_board_row(row_index, user_guess, (black_pegs, white_pegs))
            self.ui.game_screen.reset_current_selection()
            
            if black_pegs == 4:
                QMessageBox.information(self.ui, "Game Over", f"Player 2 wins! Code cracked in {self.current_round} attempts.")
                self.ui.change_screen(0)
                return
            
            elif self.current_round >= self.max_rounds:
                QMessageBox.information(self.ui, "Game Over", "Player 1 wins! Player 2 is out of attempts.")
                self.ui.change_screen(0)
                return
            
            self.current_round += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MastermindNeonUI()
    manager = GameManager(main_window)
    main_window.show()
    sys.exit(app.exec())
