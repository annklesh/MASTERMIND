import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, 
                               QGraphicsDropShadowEffect, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap

class MainMenu(QWidget):
    """Klasa menu głównego odpowiedzialna za wybór trybu rozgrywki."""
    def __init__(self, change_screen_callback):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("MASTERMIND")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 42px; 
                font-weight: bold; 
                color: #ff007f; 
                letter-spacing: 5px; 
                margin-bottom: 30px;
                background: transparent;
            }
        """)
        
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor("#ff007f"))
        glow.setOffset(0, 0)
        title.setGraphicsEffect(glow)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_player_vs_comp = QPushButton("Player vs Bot")       # tryb 1: komputer losuje sekretny kod, gracz go odgaduje
        self.btn_player_vs_player = QPushButton("Player vs Player")  # tryb 2: pierwszy gracz wpisuje kod, drugi gracz odgaduje
        self.btn_comp_vs_player = QPushButton("Bot vs Player")       # tryb 3: gracz wymyśla i wpisuje kod, a bot go odgaduje
        
        for btn in [self.btn_player_vs_comp, self.btn_player_vs_player, self.btn_comp_vs_player]:
            btn.setFixedSize(280, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #141622;
                    border: 2px solid #00ffff;
                    color: #00ffff;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #00ffff;
                    color: #0d0e15;
                }
            """)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            btn.clicked.connect(lambda: change_screen_callback(1))

        self.setLayout(layout)


class GameScreen(QWidget):
    """Klasa głównego ekranu rozgrywki (planszy)."""
    def __init__(self, add_glow_method):
        super().__init__()
        self.add_glow_method = add_glow_method

        # Słownik do mapowania kolorów HEX na nazwy dla modułu logiki
        self.color_mapping = {
            "#ef4444": "Red",
            "#ea580c": "Orange",
            "#eab308": "Yellow",
            "#22c55e": "Green",
            "#3b82f6": "Blue",
            "#a855f7": "Purple"
        }

        self.selected_colors = []   # lista przechowująca aktualny wybór gracza w rundzie

        # Główny układ poziomy dzielący ekran na 3 kolumny
        hbox_layout = QHBoxLayout(self)
        hbox_layout.setContentsMargins(20, 20, 20, 20)
        hbox_layout.setSpacing(20)

        # 1. LEWA KOLUMNA (Sterowanie i zasady)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        menu_card = QFrame()
        menu_card.setObjectName("Card")
        menu_card.setFixedWidth(240)
        menu_layout = QVBoxLayout(menu_card)
        menu_layout.setContentsMargins(15, 15, 15, 15)
        menu_layout.setSpacing(10)
        
        menu_title = QLabel("CONTROLS")
        menu_title.setStyleSheet("font-weight: bold; color: #ff007f; font-size: 13px; letter-spacing: 1px; margin-bottom: 5px; background: transparent;")
        menu_layout.addWidget(menu_title)

        for text in ["New Game", "Main Menu"]:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1c28; color: #a0aec0; text-align: left;
                    padding-left: 15px; border: 1px solid #2d3748; font-size: 14px; font-weight: bold; border-radius: 8px;
                }
                QPushButton:hover { background-color: #1f2336; color: #00ffff; border: 1px solid #00ffff; }
            """)
            menu_layout.addWidget(btn)
        left_panel.addWidget(menu_card)

        rules_card = QFrame()
        rules_card.setObjectName("Card")
        rules_card.setFixedWidth(240)
        rules_layout = QVBoxLayout(rules_card)
        rules_layout.setContentsMargins(15, 15, 15, 15)
        
        rules_title = QLabel("RULES")
        rules_title.setStyleSheet("font-weight: bold; color: #ff007f; font-size: 13px; letter-spacing: 1px; margin-bottom: 5px; background: transparent;")
        
        rules_text = QLabel(
            "<div style='line-height: 1.6; color: #a0aec0; font-size: 13px;'>"
            "Guess the secret code of 4 colored pegs.<br>"
            "After each attempt, you get clues:<br><br>"
            "• Black — right color, right position.<br>"
            "• White — right color, wrong position."
            "</div>"
        )
        rules_text.setStyleSheet("background: transparent;")
        rules_text.setWordWrap(True)
        
        rules_layout.addWidget(rules_title)
        rules_layout.addWidget(rules_text)
        left_panel.addWidget(rules_card)
        left_panel.addStretch()
        
        hbox_layout.addLayout(left_panel, 1)

       # 2. ŚRODKOWA KOLUMNA (Główna plansza prób + Paleta kolorów)

        center_area = QVBoxLayout()
        center_area.setSpacing(12)

       # Obszar przewijania rzędów zapobiegający zniekształceniom interfejsu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QScrollBar:vertical { background: #0d0e15; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #1f2336; border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: #00ffff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }
        """)

        board_card = QFrame()
        board_card.setObjectName("Card")
        board_layout = QVBoxLayout(board_card)
        board_layout.setContentsMargins(20, 15, 20, 15)
        board_layout.setSpacing(6)

        board_title = QLabel("Attempts")
        board_title.setStyleSheet("color: #6b7280; font-size: 14px; font-weight: 500; margin-bottom: 2px; background: transparent;")
        board_layout.addWidget(board_title)

        self.board_pegs = []   
        self.board_hints = []  

        for row in range(10):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 4, 15, 4)
            row_layout.setSpacing(0)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_widget.setStyleSheet("QWidget { background-color: #161925; border-radius: 8px; }")

            # Numery rzędów na planszy
            num_label = QLabel(f"{row + 1}")
            num_label.setFixedWidth(35)
            num_label.setStyleSheet("color: #4a5568; font-size: 13px; font-weight: bold; background: transparent;")
            row_layout.addWidget(num_label)
            
            # Cztery otwory na pionki w danym rzędzie
            pegs_layout = QHBoxLayout()
            pegs_layout.setSpacing(12)
            pegs_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_pegs_list = []
            for _ in range(4):
                peg = QFrame()
                peg.setFixedSize(34, 34)
                peg.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #2d3748; border-radius: 17px; }")
                pegs_layout.addWidget(peg)
                row_pegs_list.append(peg)
            self.board_pegs.append(row_pegs_list)
            row_layout.addLayout(pegs_layout)
            
            row_layout.addStretch() 

            # Cztery miniaturowe otwory na podpowiedzi (feedback) dla każdego rzędu
            hints_layout = QHBoxLayout()
            hints_layout.setSpacing(6)
            hints_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_hints_list = []
            for _ in range(4):
                hint = QFrame()
                hint.setFixedSize(12, 12)
                hint.setStyleSheet("QFrame { background-color: transparent; border: 1px solid #4a5568; border-radius: 6px; }")
                hints_layout.addWidget(hint)
                row_hints_list.append(hint)
                    
            self.board_hints.append(row_hints_list)
            row_layout.addLayout(hints_layout)

            board_layout.addWidget(row_widget)

        scroll_area.setWidget(board_card)
        center_area.addWidget(scroll_area, 1)

        # Panel wyboru aktualnego ruchu "YOUR TURN"
        control_card = QFrame()
        control_card.setObjectName("Card")
        control_layout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(15, 12, 15, 12)
        
        control_title = QLabel("YOUR TURN")
        control_title.setStyleSheet("color: #6b7280; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent;")
        control_layout.addWidget(control_title)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setSpacing(12)
        bottom_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        current_input_box = QFrame()
        current_input_box.setStyleSheet("QFrame { background-color: #11131e; border: 1px solid #312e81; border-radius: 12px; }")
        input_box_layout = QHBoxLayout(current_input_box)
        input_box_layout.setContentsMargins(15, 6, 15, 6)
        input_box_layout.setSpacing(12)
        input_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.current_slots = []
        for _ in range(4):
            slot = QFrame()
            slot.setFixedSize(40, 40)
            slot.setStyleSheet("background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;")
            input_box_layout.addWidget(slot)
            self.current_slots.append(slot)
            
        bottom_row_layout.addWidget(current_input_box, 1)

        self.btn_backspace = QPushButton("⌫")
        self.btn_backspace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backspace.setFixedSize(50, 50)
        self.btn_backspace.setStyleSheet("""
            QPushButton { background-color: #161925; color: #a0aec0; border: 1px solid #2d3748; border-radius: 12px; font-size: 18px; }
            QPushButton:hover { background-color: #1f2336; color: #ffffff; }
        """)

        self.btn_backspace.clicked.connect(self._handle_backspace)  # podłączenie funkcji kasowania backspace
        bottom_row_layout.addWidget(self.btn_backspace)
    
        self.btn_check_turn = QPushButton("CHECK CODE")
        self.btn_check_turn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_turn.setFixedSize(180, 50)
        self.btn_check_turn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1e3a8a, stop:1 #6d28d9);
                color: white; font-weight: bold; font-size: 13px; letter-spacing: 1px; border: none; border-radius: 12px;
            }
            QPushButton:hover { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #7c3aed); }
        """)
        bottom_row_layout.addWidget(self.btn_check_turn)
        control_layout.addLayout(bottom_row_layout)
        center_area.addWidget(control_card)

        # Paleta dostępnych kolorów na samym dole ekranu
        palette_layout = QHBoxLayout()
        palette_layout.setSpacing(12)
        palette_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        exact_colors = ["#a855f7", "#3b82f6", "#22c55e", "#eab308", "#ea580c", "#ef4444"]
        for color in exact_colors:
            color_btn = QPushButton()
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setFixedSize(40, 40)
            color_btn.setStyleSheet(f"QPushButton {{ background-color: {color}; border: none; border-radius: 20px; }} QPushButton:hover {{ border: 3px solid #ffffff; }}")
            self.add_glow_method(color_btn, color, radius=12)
            
            # Każdy przycisk palety przekazuje swój kolor po kliknięciu
            color_btn.clicked.connect(lambda checked=False, c=color: self._handle_color_click(c))
            palette_layout.addWidget(color_btn)
            
        center_area.addLayout(palette_layout)
        hbox_layout.addLayout(center_area, 4)

        # 3. PRAWA KOLUMNA (Statystyki i podgląd kodu bota)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # Panel Statystyk
        stats_card = QFrame()
        stats_card.setObjectName("Card")
        stats_card.setFixedWidth(280)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(18, 15, 18, 15)
        stats_layout.setSpacing(12)

        stats_header = QHBoxLayout()
        stats_title = QLabel("STATISTICS")
        stats_title.setStyleSheet("font-weight: bold; color: #8a8dbe; font-size: 13px; letter-spacing: 1px; background: transparent;")
        
        stats_header.addWidget(stats_title)
        stats_header.addStretch()
        stats_layout.addLayout(stats_header)

        def create_stat_row(text):
            row = QHBoxLayout()
            lbl_text = QLabel(text)
            lbl_text.setStyleSheet("color: #9ca3af; font-size: 14px; background: transparent; padding: 2px 0;")
            row.addWidget(lbl_text)
            row.addStretch()
            return row

        stats_layout.addLayout(create_stat_row("Games"))
        stats_layout.addLayout(create_stat_row("Wins"))
        stats_layout.addLayout(create_stat_row("Best Score"))
        right_panel.addWidget(stats_card)

        # Panel ukrytego Kodu 
        code_card = QFrame()
        code_card.setObjectName("Card")
        code_card.setFixedWidth(280)
        code_layout = QVBoxLayout(code_card)
        code_layout.setContentsMargins(18, 18, 18, 18)
        code_layout.setSpacing(15)

        code_header = QHBoxLayout()
        code_title = QLabel("CODE")
        code_title.setStyleSheet("font-weight: bold; color: #8a8dbe; font-size: 13px; letter-spacing: 1px; background: transparent;")
        code_header.addWidget(code_title)
        code_header.addStretch()
        code_layout.addLayout(code_header)

        code_slots_layout = QHBoxLayout()
        code_slots_layout.setSpacing(12)
        code_slots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for _ in range(4):
            lock_slot = QFrame()
            lock_slot.setFixedSize(52, 52) 
            lock_slot.setStyleSheet("""
                QFrame { 
                    background-color: #161925; 
                    border: 2px solid #2d3748; 
                    border-radius: 12px; 
                }
            """)
            inner_layout = QHBoxLayout(lock_slot)
            inner_layout.setContentsMargins(4, 4, 4, 4)
            inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            slot_lock = self.create_image_icon("lock.png", 34, 34) 
            
            inner_layout.addWidget(slot_lock)
            code_slots_layout.addWidget(lock_slot)
            
        code_layout.addLayout(code_slots_layout)
        right_panel.addWidget(code_card)
        
        right_panel.addStretch()
        hbox_layout.addLayout(right_panel, 1)


    def create_image_icon(self, filename, width, height):
        """Metoda pomocnicza do bezpiecznego wczytywania ikon z katalogu projektu."""
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if os.path.exists(filename):
            pixmap = QPixmap(filename)
            scaled_pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl.setPixmap(scaled_pixmap)
        else:
            lbl.setText("?")
            lbl.setStyleSheet("""
                QLabel {
                    color: #4b5563; 
                    font-weight: bold; 
                    font-size: 24px; 
                    background: transparent; 
                    border: none;
                }
            """)
        return lbl
    
    # METODY OBSŁUGI INTERFEJSU GRAFICZNEGO

    def _handle_color_click(self, color_hex: str) -> None:
        """Dodaje wybrany z palety kolor do wolnego slotu w aktualnym ruchu."""
        if len(self.selected_colors) < 4:
            self.selected_colors.append(color_hex)
            slot_index = len(self.selected_colors) - 1
            self.current_slots[slot_index].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 20px;"
            )
            self.add_glow_method(self.current_slots[slot_index], color_hex, radius=10)
           
    def _handle_backspace(self) -> None:
        """Usuwa ostatnio dodany kolor z aktualnego wyboru."""
        if self.selected_colors:
            slot_index = len(self.selected_colors) - 1
            self.selected_colors.pop()
            self.current_slots[slot_index].setGraphicsEffect(None)
            self.current_slots[slot_index].setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )

    # FUNKCJE DLA APP.PY
    
    def get_current_colors(self) -> list[str]:
        """Zwraca aktualnie wybrane kolory przetłumaczone na nazwy tekstowe dla logiki."""
        return [self.color_mapping[c] for c in self.selected_colors]


    def reset_current_selection(self) -> None:
        """Czyści wybór w sekcji 'YOUR TURN' przed nową rundą."""
        self.selected_colors.clear()
        for slot in self.current_slots:
            slot.setGraphicsEffect(None)
            slot.setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )


    def update_board_row(self, row_index: int, colors: list[str], feedback: tuple[int, int]) -> None:
        """
        Zapisuje na stałe ruch gracza w historycznym rzędzie planszy 
        oraz wyświetla czarne i białe punkty podpowiedzi.
        """
        reverse_mapping = {v: k for k, v in self.color_mapping.items()} # odwracamy mapowanie nazw
        
        # Kolorujemy 4 kulki w historycznym rzędzie planszy
        for i, color_name in enumerate(colors):
            color_hex = reverse_mapping[color_name]
            self.board_pegs[row_index][i].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 17px;"
            )
            self.add_glow_method(self.board_pegs[row_index][i], color_hex, radius=8)

        # Wyświetlamy podpowiedzi (czarne i białe kropki)
        black_pegs, white_pegs = feedback
        hint_index = 0

        # Czarne kropki (prawidłowe miejsce i kolor)
        for _ in range(black_pegs):
            if hint_index < 4:
                self.board_hints[row_index][hint_index].setStyleSheet(
                    "background-color: #000000; border: 1px solid #ff007f; border-radius: 6px;"
                )
                self.add_glow_method(self.board_hints[row_index][hint_index], "#ff007f", radius=6)
                hint_index += 1

        # Białe kropki (prawidłowy kolor, złe miejsce)
        for _ in range(white_pegs):
            if hint_index < 4:
                self.board_hints[row_index][hint_index].setStyleSheet(
                    "background-color: #ffffff; border: 1px solid #00ffff; border-radius: 6px;"
                )
                self.add_glow_method(self.board_hints[row_index][hint_index], "#00ffff", radius=6)
                hint_index += 1


class MastermindNeonUI(QMainWindow):
    """Główne okno aplikacji."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mastermind // Cyberpunk Edition")
        self.resize(1240, 820)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0e15; }
            QLabel { font-family: 'Segoe UI', Helvetica, sans-serif; }
            QFrame#Card { background-color: #141622; border-radius: 12px; border: 1px solid #1f2336; }
        """)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.menu_screen = MainMenu(self.change_screen)
        self.game_screen = GameScreen(self.add_glow_effect)

        self.stacked_widget.addWidget(self.menu_screen) 
        self.stacked_widget.addWidget(self.game_screen) 

        self.stacked_widget.setCurrentIndex(0)

    def change_screen(self, index):
        """Zmienia aktualnie wyświetlany ekran aplikacji."""
        self.stacked_widget.setCurrentIndex(index)

    def add_glow_effect(self, widget, color_hex, radius=10):
        """Nadaje elementom interfejsu graficznego neonowy efekt poświaty."""
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(radius)
        glow.setColor(QColor(color_hex))
        glow.setOffset(0, 0)
        widget.setGraphicsEffect(glow)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MastermindNeonUI()
    window.show()
    sys.exit(app.exec())
