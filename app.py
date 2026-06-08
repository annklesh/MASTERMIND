import sys
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox
from view.game_window import MastermindNeonUI
from logic.game_logic import MastermindLogic
from game_stats import StatsManager
from bot.game_bot import GameBot

class GameManager:
    def __init__(self, ui_window):
        self.ui = ui_window
        self.logic = MastermindLogic()
        self.stats = StatsManager()
        self.current_round = 1
        self.max_rounds = 10
        self.current_mode = None
        
        self._connect_signals()

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
        
        secret = self.logic.generate_secret_code()
        print(f"DEBUG: Secret code is: {secret}")
        
        self.ui.change_screen(1)

    def start_comp_vs_player(self):
        """Gracz wymyśla kod, a Bot zgaduje."""
        print("Starting mode: Computer vs Player")
        
        text, ok = QInputDialog.getText(
            self.ui, 
            "Your Secret Code", 
            "Enter 4 colors separated by space\n(Red, Orange, Yellow, Green, Blue, Purple):"
        )
        
        if ok and text:
            player_secret = [color.strip().capitalize() for color in text.split()]
            
            if len(player_secret) != 4:
                QMessageBox.warning(self.ui, "Error", "You must enter exactly 4 colors!")
                return
                
            self.logic.set_secret_code(player_secret)
            print(f"Secret code set to: {player_secret}")
            
            self.bot = GameBot(logic_answer=(0, 0))
            
            self.current_mode = "CvP"
            self.current_round = 1
            self.ui.change_screen(1)

    def start_player_vs_player(self):
        """Gracz 1 wymyśla kod, Gracz 2 zgaduje na planszy."""
        print("Starting mode: Player vs Player")
        
        text, ok = QInputDialog.getText(
            self.ui, 
            "Player 1: Set Secret Code", 
            "Player 1, enter 4 colors separated by space\n(Red, Orange, Yellow, Green, Blue, Purple):"
        )
        
        if ok and text:
            player_secret = [color.strip().capitalize() for color in text.split()]
            
            if len(player_secret) != 4:
                QMessageBox.warning(self.ui, "Error", "You must enter exactly 4 colors!")
                return
                
            self.logic.set_secret_code(player_secret)
            print("Secret code set by Player 1.")
            
            self.current_mode = "PvP"
            self.current_round = 1
            self.ui.change_screen(1)

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
                self.stats.save_game_result(won=True, rounds=self.current_round)
        
                QMessageBox.information(self.ui, "Victory!", f"You cracked the code in {self.current_round} attempts!")
                self.ui.change_screen(0) 
                return
            
            elif self.current_round >= self.max_rounds:
                print("Game Over! Out of attempts.")
                self.stats.save_game_result(won=False, rounds=self.current_round)
                
                QMessageBox.information(self.ui, "Game Over", "Out of attempts. The computer wins!")
                self.ui.change_screen(0) 
                return
            
            self.current_round += 1

        elif self.current_mode == "CvP":
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
                QMessageBox.information(self.ui, "Game Over", f"Bot cracked your code in {self.current_round} attempts!")
                self.ui.change_screen(0)
                return
                
            elif self.current_round >= self.max_rounds:
                QMessageBox.information(self.ui, "Game Over", "You won! Bot failed to crack your code.")
                self.ui.change_screen(0)
                return
        
            self.current_round += 1

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