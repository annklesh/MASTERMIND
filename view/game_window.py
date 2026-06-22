import sys
import os
from typing import Callable, Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, 
                               QGraphicsDropShadowEffect, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap


class MainMenu(QWidget):
    """Klasa menu głównego odpowiedzialna za wybór trybu rozgrywki."""

    def __init__(self, change_screen_callback: Callable[[int], None], set_pvp_callback: Optional[Callable[[bool], None]] = None) -> None:
        """
        Inicjalizuje menu główne, ustawia tytuł z efektem neonu oraz przyciski wyboru trybu.

        :param change_screen_callback: Funkcja zwrotna do zmiany indeksu ekranu.
        :param set_pvp_callback: Opcjonalna funkcja zwrotna do ustawiania trybu PvP/Solo.
        """
        super().__init__()
        self.change_screen_callback: Callable[[int], None] = change_screen_callback
        self.set_pvp_callback: Optional[Callable[[bool], None]] = set_pvp_callback

        layout: QVBoxLayout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title: QLabel = QLabel("MASTERMIND")
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
        
        glow: QGraphicsDropShadowEffect = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor("#ff007f"))
        glow.setOffset(0, 0)
        title.setGraphicsEffect(glow)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_player_vs_comp: QPushButton = QPushButton("Player vs Bot")
        self.btn_player_vs_player: QPushButton = QPushButton("Player vs Player")
        self.btn_comp_vs_player: QPushButton = QPushButton("Bot vs Player")
        
        self.btn_player_vs_comp.clicked.connect(lambda: self._handle_mode_selection(False))
        self.btn_comp_vs_player.clicked.connect(lambda: self._handle_mode_selection(False))
        self.btn_player_vs_player.clicked.connect(lambda: self._handle_mode_selection(True))

        btn: QPushButton
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

        self.setLayout(layout)

    def _handle_mode_selection(self, is_pvp: bool) -> None:
        """
        Przekazuje informację o wybranym trybie gry poprzez callback.

        :param is_pvp: Wartość True, jeśli wybrano tryb Player vs Player, w przeciwnym razie False.
        """
        if self.set_pvp_callback:
            self.set_pvp_callback(is_pvp)


class GameScreen(QWidget):
    """Klasa głównego ekranu rozgrywki (planszy)."""

    def __init__(self, add_glow_method: Callable[[QWidget, str, int], None]) -> None:
        """
        Inicjalizuje komponenty planszy gry, panele boczne, statystyki oraz paletę kolorów.

        :param add_glow_method: Metoda z głównego okna służąca do nakładania efektu poświaty neonowej.
        """
        super().__init__()
        self.add_glow_method: Callable[[QWidget, str, int], None] = add_glow_method

        self.color_mapping: dict[str, str] = {
            "#ef4444": "Red",
            "#ea580c": "Orange",
            "#eab308": "Yellow",
            "#22c55e": "Green",
            "#3b82f6": "Blue",
            "#a855f7": "Purple"
        }

        self.selected_colors: list[str] = []

        hbox_layout: QHBoxLayout = QHBoxLayout(self)
        hbox_layout.setContentsMargins(20, 20, 20, 20)
        hbox_layout.setSpacing(20)

        ### 1. LEWA KOLUMNA (Sterowanie i zasady)
        left_panel: QVBoxLayout = QVBoxLayout()
        left_panel.setSpacing(15)

        menu_card: QFrame = QFrame()
        menu_card.setObjectName("Card")
        menu_card.setFixedWidth(240)

        self.menu_layout: QVBoxLayout = QVBoxLayout(menu_card)
        self.menu_layout.setContentsMargins(15, 15, 15, 15)
        self.menu_layout.setSpacing(10)
        
        menu_title: QLabel = QLabel("CONTROLS")
        menu_title.setStyleSheet("font-weight: bold; color: #ff007f; font-size: 13px; letter-spacing: 1px; margin-bottom: 5px; background: transparent;")
        self.menu_layout.addWidget(menu_title)

        self.btn_new_game: QPushButton = QPushButton("New Game")
        self.btn_main_menu: QPushButton = QPushButton("Main Menu")

        btn: QPushButton
        for btn in [self.btn_new_game, self.btn_main_menu]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1c28; 
                    color: #a0aec0; 
                    text-align: left;
                    padding-left: 15px; 
                    border: 1px solid #2d3748; 
                    font-size: 14px; 
                    font-weight: bold; 
                    border-radius: 8px;
                }
                QPushButton:hover { 
                    background-color: #1f2336; 
                    color: #ffffff; 
                    border: 1px solid #ff007f; 
                }
            """)
            self.menu_layout.addWidget(btn)
        left_panel.addWidget(menu_card)

        rules_card: QFrame = QFrame()
        rules_card.setObjectName("Card")
        rules_card.setFixedWidth(240)
        rules_layout: QVBoxLayout = QVBoxLayout(rules_card)
        rules_layout.setContentsMargins(15, 15, 15, 15)
        
        rules_title: QLabel = QLabel("RULES")
        rules_title.setStyleSheet("font-weight: bold; color: #ff007f; font-size: 13px; letter-spacing: 1px; margin-bottom: 5px; background: transparent;")
        
        rules_text: QLabel = QLabel(
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

        ### 2. ŚRODKOWA KOLUMNA (Główna plansza prób + Paleta kolorów)
        center_area: QVBoxLayout = QVBoxLayout()
        center_area.setSpacing(12)

        scroll_area: QScrollArea = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QScrollArea QWidget { background-color: transparent; }
            QScrollBar:vertical { background: #0d0e15; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #1f2336; border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: #00ffff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }
        """)

        board_card: QFrame = QFrame()
        board_card.setObjectName("Card")
        board_layout: QVBoxLayout = QVBoxLayout(board_card)
        board_layout.setContentsMargins(20, 15, 20, 15)
        board_layout.setSpacing(6)

        board_title: QLabel = QLabel("Attempts")
        board_title.setStyleSheet("color: #6b7280; font-size: 14px; font-weight: 500; margin-bottom: 2px; background: transparent;")
        board_layout.addWidget(board_title)

        self.board_pegs: list[list[QFrame]] = []   
        self.board_hints: list[list[QFrame]] = []  

        row: int
        for row in range(10):
            row_widget: QWidget = QWidget()
            row_layout: QHBoxLayout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 4, 15, 4)
            row_layout.setSpacing(0)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_widget.setStyleSheet("QWidget { background-color: #161925; border-radius: 8px; }")

            num_label: QLabel = QLabel(f"{row + 1}")
            num_label.setFixedWidth(35)
            num_label.setStyleSheet("color: #4a5568; font-size: 13px; font-weight: bold; background: transparent;")
            row_layout.addWidget(num_label)
            
            pegs_layout: QHBoxLayout = QHBoxLayout()
            pegs_layout.setSpacing(12)
            pegs_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_pegs_list: list[QFrame] = []
            for _ in range(4):
                peg: QFrame = QFrame()
                peg.setFixedSize(34, 34)
                peg.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #2d3748; border-radius: 17px; }")
                pegs_layout.addWidget(peg)
                row_pegs_list.append(peg)
            self.board_pegs.append(row_pegs_list)
            row_layout.addLayout(pegs_layout)
            
            row_layout.addStretch() 

            hints_layout: QHBoxLayout = QHBoxLayout()
            hints_layout.setSpacing(6)
            hints_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            row_hints_list: list[QFrame] = []
            for _ in range(4):
                hint: QFrame = QFrame()
                hint.setFixedSize(12, 12)
                hint.setStyleSheet("QFrame { background-color: transparent; border: 1px solid #4a5568; border-radius: 6px; }")
                hints_layout.addWidget(hint)
                row_hints_list.append(hint)
                    
            self.board_hints.append(row_hints_list)
            row_layout.addLayout(hints_layout)

            board_layout.addWidget(row_widget)

        scroll_area.setWidget(board_card)
        center_area.addWidget(scroll_area, 1)

        control_card: QFrame = QFrame()
        control_card.setObjectName("Card")
        control_layout: QVBoxLayout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(15, 12, 15, 12)
        
        control_title: QLabel = QLabel("YOUR TURN")
        control_title.setStyleSheet("color: #6b7280; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent;")
        control_layout.addWidget(control_title)

        bottom_row_layout: QHBoxLayout = QHBoxLayout()
        bottom_row_layout.setSpacing(12)
        bottom_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        current_input_box: QFrame = QFrame()
        current_input_box.setStyleSheet("QFrame { background-color: #11131e; border: 1px solid #312e81; border-radius: 12px; }")
        input_box_layout: QHBoxLayout = QHBoxLayout(current_input_box)
        input_box_layout.setContentsMargins(15, 6, 15, 6)
        input_box_layout.setSpacing(12)
        input_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.current_slots: list[QFrame] = []
        for _ in range(4):
            slot: QFrame = QFrame()
            slot.setFixedSize(40, 40)
            slot.setStyleSheet("background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;")
            input_box_layout.addWidget(slot)
            self.current_slots.append(slot)
            
        bottom_row_layout.addWidget(current_input_box, 1)

        self.btn_backspace: QPushButton = QPushButton("⌫")
        self.btn_backspace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backspace.setFixedSize(50, 50)
        self.btn_backspace.setStyleSheet("""
            QPushButton { background-color: #161925; color: #a0aec0; border: 1px solid #2d3748; border-radius: 12px; font-size: 18px; }
            QPushButton:hover { background-color: #1f2336; color: #ffffff; }
        """)

        self.btn_backspace.clicked.connect(self._handle_backspace)
        bottom_row_layout.addWidget(self.btn_backspace)
    
        self.btn_check_turn: QPushButton = QPushButton("CHECK CODE")
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

        palette_layout: QHBoxLayout = QHBoxLayout()
        palette_layout.setSpacing(12)
        palette_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        exact_colors: list[str] = ["#a855f7", "#3b82f6", "#22c55e", "#eab308", "#ea580c", "#ef4444"]
        color: str
        for color in exact_colors:
            color_btn: QPushButton = QPushButton()
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setFixedSize(40, 40)
            color_btn.setStyleSheet(f"QPushButton {{ background-color: {color}; border: none; border-radius: 20px; }} QPushButton:hover {{ border: 3px solid #ffffff; }}")
            self.add_glow_method(color_btn, color, 12)
            
            color_btn.clicked.connect(lambda checked=False, c=color: self._handle_color_click(c))
            palette_layout.addWidget(color_btn)
            
        center_area.addLayout(palette_layout)
        hbox_layout.addLayout(center_area, 4)

        ### 3. PRAWA KOLUMNA (Statystyki i podgląd kodu bota)
        right_panel: QVBoxLayout = QVBoxLayout()
        right_panel.setSpacing(15)

        stats_card: QFrame = QFrame()
        stats_card.setObjectName("Card")
        stats_card.setFixedWidth(280)
        stats_layout: QVBoxLayout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(12)

        stats_header: QHBoxLayout = QHBoxLayout()
        stats_title: QLabel = QLabel("STATISTICS")
        stats_title.setStyleSheet("font-weight: bold; color: #8a8dbe; font-size: 13px; letter-spacing: 1px; background: transparent; margin-bottom: 5px;")
        stats_header.addWidget(stats_title)
        stats_header.addStretch()
        stats_layout.addLayout(stats_header)

        def create_stat_row(text: str, parent_layout: QVBoxLayout) -> tuple[QLabel, QLabel]:
            row_lay: QHBoxLayout = QHBoxLayout()
            row_lay.setContentsMargins(0, 2, 0, 2)
            lbl_t: QLabel = QLabel(text)
            lbl_t.setStyleSheet("color: #9ca3af; font-size: 13px; background: transparent; border: none;")
            
            lbl_v: QLabel = QLabel("-")
            lbl_v.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; background: transparent; border: none;")
            
            row_lay.addWidget(lbl_t)
            row_lay.addStretch()
            row_lay.addWidget(lbl_v)
            parent_layout.addLayout(row_lay)
            return lbl_t, lbl_v

        self.lbl_games_desc: QLabel
        self.label_games_val: QLabel
        self.lbl_games_desc, self.label_games_val = create_stat_row("Games", stats_layout)
        
        line: QFrame = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1f2336; max-height: 1px; border: none;")
        stats_layout.addWidget(line)

        self.single_player_container: QWidget = QWidget()
        self.single_player_container.setStyleSheet("background: transparent;")
        sp_layout: QVBoxLayout = QVBoxLayout(self.single_player_container)
        sp_layout.setContentsMargins(0, 0, 0, 0)
        sp_layout.setSpacing(8)
        
        self.lbl_wins_desc: QLabel
        self.label_wins_val: QLabel
        self.lbl_best_desc: QLabel
        self.label_best_val: QLabel
        self.lbl_wins_desc, self.label_wins_val = create_stat_row("Wins", sp_layout)
        self.lbl_best_desc, self.label_best_val = create_stat_row("Best Score", sp_layout)
        stats_layout.addWidget(self.single_player_container)

        self.pvp_container: QWidget = QWidget()
        self.pvp_container.setStyleSheet("background: transparent;")
        pvp_layout: QVBoxLayout = QVBoxLayout(self.pvp_container)
        pvp_layout.setContentsMargins(0, 0, 0, 0)
        pvp_layout.setSpacing(16)

        self.codemaker_frame: QFrame = QFrame()
        self.codemaker_frame.setStyleSheet("""
            QFrame { background-color: #11131e; border: 1px solid #2d3748; border-radius: 8px; } 
            QLabel { background: transparent; border: none; }
        """)
        cm_layout: QVBoxLayout = QVBoxLayout(self.codemaker_frame)
        cm_layout.setContentsMargins(12, 12, 12, 12)
        cm_layout.setSpacing(8)
        
        cm_title_layer: QHBoxLayout = QHBoxLayout()
        cm_title_layer.setContentsMargins(0, 0, 0, 0)
        cm_title: QLabel = QLabel("CODEMAKER (Setter)")
        cm_title.setStyleSheet("font-weight: bold; color: #ff007f; font-size: 11px; letter-spacing: 0.5px;")
        cm_title_layer.addWidget(cm_title)
        cm_layout.addLayout(cm_title_layer)

        cm_body_layout: QVBoxLayout = QVBoxLayout()
        cm_body_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_setter_wins_desc: QLabel
        self.label_setter_wins_val: QLabel
        self.lbl_setter_wins_desc, self.label_setter_wins_val = create_stat_row("Wins", cm_body_layout)
        cm_layout.addLayout(cm_body_layout)
        pvp_layout.addWidget(self.codemaker_frame)

        self.codebreaker_frame: QFrame = QFrame()
        self.codebreaker_frame.setStyleSheet("""
            QFrame { background-color: #11131e; border: 1px solid #2d3748; border-radius: 8px; } 
            QLabel { background: transparent; border: none; }
        """)
        cb_layout: QVBoxLayout = QVBoxLayout(self.codebreaker_frame)
        cb_layout.setContentsMargins(12, 12, 12, 12)
        cb_layout.setSpacing(8)
        
        cb_title_layer: QHBoxLayout = QHBoxLayout()
        cb_title_layer.setContentsMargins(0, 0, 0, 0)
        cb_title: QLabel = QLabel("CODEBREAKER (Guesser)")
        cb_title.setStyleSheet("font-weight: bold; color: #00ffff; font-size: 11px; letter-spacing: 0.5px;")
        cb_title_layer.addWidget(cb_title)
        cb_layout.addLayout(cb_title_layer)

        cb_body_layout: QVBoxLayout = QVBoxLayout()
        cb_body_layout.setContentsMargins(0, 0, 0, 0)
        cb_body_layout.setSpacing(6)
        self.lbl_guesser_wins_desc: QLabel
        self.label_guesser_wins_val: QLabel
        self.lbl_guesser_best_desc: QLabel
        self.label_guesser_best_val: QLabel
        self.lbl_guesser_wins_desc, self.label_guesser_wins_val = create_stat_row("Wins", cb_body_layout)
        self.lbl_guesser_best_desc, self.label_guesser_best_val = create_stat_row("Best Score", cb_body_layout)
        cb_layout.addLayout(cb_body_layout)
        pvp_layout.addWidget(self.codebreaker_frame)

        stats_layout.addWidget(self.pvp_container)
        
        self.pvp_container.setVisible(False)
        self.single_player_container.setVisible(True)

        right_panel.addWidget(stats_card)

        code_card: QFrame = QFrame()
        code_card.setObjectName("Card")
        code_card.setFixedWidth(280)
        code_layout: QVBoxLayout = QVBoxLayout(code_card)
        code_layout.setContentsMargins(18, 18, 18, 18)
        code_layout.setSpacing(15)

        code_header: QHBoxLayout = QHBoxLayout()
        code_title: QLabel = QLabel("CODE")
        code_title.setStyleSheet("font-weight: bold; color: #8a8dbe; font-size: 13px; letter-spacing: 1px; background: transparent;")
        code_header.addWidget(code_title)
        code_header.addStretch()
        code_layout.addLayout(code_header)

        self.code_slots_layout: QHBoxLayout = QHBoxLayout()
        self.code_slots_layout.setSpacing(12)
        self.code_slots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for _ in range(4):
            lock_slot: QFrame = QFrame()
            lock_slot.setFixedSize(52, 52) 
            lock_slot.setStyleSheet("QFrame { background-color: #161925; border: 2px solid #2d3748; border-radius: 12px; }")
            inner_layout: QHBoxLayout = QHBoxLayout(lock_slot)
            inner_layout.setContentsMargins(4, 4, 4, 4)
            inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            slot_lock: QLabel = self.create_image_icon("lock.png", 34, 34) 
            inner_layout.addWidget(slot_lock)
            self.code_slots_layout.addWidget(lock_slot)
            
        code_layout.addLayout(self.code_slots_layout)
        right_panel.addWidget(code_card)
        
        right_panel.addStretch()
        hbox_layout.addLayout(right_panel, 1)

    def set_pvp_mode(self, is_pvp: bool) -> None:
        """
        Dynamicznie przełącza widoczność kafelków statystyk między trybami Solo/PVP.

        :param is_pvp: True jeśli włączono tryb PvP, False jeśli tryb jednoosobowy.
        """
        self.single_player_container.setVisible(not is_pvp)
        self.pvp_container.setVisible(is_pvp)

    def create_image_icon(self, filename: str, width: int, height: int) -> QLabel:
        """
        Tworzy widget QLabel zawierający dopasowany obrazek (ikonę).

        :param filename: Ścieżka do pliku graficznego.
        :param width: Docelowa szerokość ikony.
        :param height: Docelowa wysokość ikony.
        :return: Obiekt QLabel z załadowaną ikoną lub pytajnikiem.
        """
        lbl: QLabel = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if os.path.exists(filename):
            pixmap: QPixmap = QPixmap(filename)
            scaled_pixmap: QPixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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

    def _handle_color_click(self, color_hex: str) -> None:
        """
        Obsługuje kliknięcie przycisku koloru z palety i dodaje go do wyboru użytkownika.

        :param color_hex: Reprezentacja szesnastkowa wybranego koloru.
        """
        if len(self.selected_colors) < 4:
            self.selected_colors.append(color_hex)
            slot_index: int = len(self.selected_colors) - 1
            self.current_slots[slot_index].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 20px;"
            )
            self.add_glow_method(self.current_slots[slot_index], color_hex, 10)
           
    def _handle_backspace(self) -> None:
        """Usuwa ostatnio wybrany kolor z bieżącego wiersza wyboru."""
        if self.selected_colors:
            slot_index: int = len(self.selected_colors) - 1
            self.selected_colors.pop()
            self.current_slots[slot_index].setGraphicsEffect(None)
            self.current_slots[slot_index].setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )

    def get_current_colors(self) -> list[str]:
        """
        Zwraca listę słownych nazw aktualnie wybranych kolorów.

        :return: Lista nazw kolorów (np. ['Red', 'Blue', ...]).
        """
        return [self.color_mapping[c] for c in self.selected_colors]

    def reset_current_selection(self) -> None:
        """Czyści aktualny wybór kolorów oraz resetuje wygląd slotów wejściowych."""
        self.selected_colors.clear()
        slot: QFrame
        for slot in self.current_slots:
            slot.setGraphicsEffect(None)
            slot.setStyleSheet(
                "background-color: transparent; border: 2px solid #2d3748; border-radius: 20px;"
            )

    def update_board_row(self, row_index: int, colors: list[str], feedback: tuple[int, int]) -> None:
        """
        Wizualizuje zatwierdzoną próbę gracza w danym wierszu planszy oraz dodaje kołki informacji zwrotnej.

        :param row_index: Indeks wiersza planszy (0-9).
        :param colors: Lista słownych nazw kolorów.
        :param feedback: Krotka (czarne_kołki, białe_kołki).
        """
        reverse_mapping: dict[str, str] = {v: k for k, v in self.color_mapping.items()}
        
        i: int
        color_name: str
        for i, color_name in enumerate(colors):
            color_hex: str = reverse_mapping[color_name]
            self.board_pegs[row_index][i].setStyleSheet(
                f"background-color: {color_hex}; border: none; border-radius: 17px;"
            )
            self.add_glow_method(self.board_pegs[row_index][i], color_hex, 8)

        black_pegs, white_pegs = feedback
        hint_index: int = 0

        for _ in range(black_pegs):
            if hint_index < 4:
                self.board_hints[row_index][hint_index].setStyleSheet(
                    "background-color: #000000; border: 1px solid #ff007f; border-radius: 6px;"
                )
                self.add_glow_method(self.board_hints[row_index][hint_index], "#ff007f", 6)
                hint_index += 1

        for _ in range(white_pegs):
            if hint_index < 4:
                self.board_hints[row_index][hint_index].setStyleSheet(
                    "background-color: #ffffff; border: 1px solid #00ffff; border-radius: 6px;"
                )
                self.add_glow_method(self.board_hints[row_index][hint_index], "#00ffff", 6)
                hint_index += 1

    def reset_board(self) -> None:
        """Przywraca stan początkowy całej głównej planszy gry (czyści wszystkie prób i wskazówki)."""
        self.reset_current_selection()
        row: int
        for row in range(10):
            peg: QFrame
            for peg in self.board_pegs[row]:
                peg.setGraphicsEffect(None)
                peg.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #2d3748; border-radius: 17px; }")
            hint: QFrame
            for hint in self.board_hints[row]:
                hint.setGraphicsEffect(None)
                hint.setStyleSheet("QFrame { background-color: transparent; border: 1px solid #4a5568; border-radius: 6px; }")

    def setup_ui_for_bot_mode(self, is_bot_mode: bool) -> None:
        """
        Dostosowuje etykiety interfejsu i dostępność przycisków na potrzeby trybu bota.

        :param is_bot_mode: True, jeśli aktualnie ruch wykonuje bot, False w trybie gracza.
        """
        if is_bot_mode:
            self.btn_check_turn.setText("NEXT BOT MOVE")
            self.btn_backspace.setEnabled(False)
        else:
            self.btn_check_turn.setText("CHECK CODE")
            self.btn_backspace.setEnabled(True)

    def reveal_secret_code(self, secret_code: list[str]) -> None:
        """
        Odsłania ukryty kod na koniec gry w panelu boczny gry.

        :param secret_code: Lista nazw kolorów stanowiących sekretny kod.
        """
        reverse_mapping: dict[str, str] = {v: k for k, v in self.color_mapping.items()}
        
        while self.code_slots_layout.count():
            item = self.code_slots_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        color_name: str
        for color_name in secret_code:
            color_hex: str = reverse_mapping[color_name]
            color_slot: QFrame = QFrame()
            color_slot.setFixedSize(52, 52)
            color_slot.setStyleSheet(
                f"background-color: {color_hex}; border: 2px solid #2d3748; border-radius: 26px;"
            )
            self.add_glow_method(color_slot, color_hex, 12)
            self.code_slots_layout.addWidget(color_slot)
    
    def reset_secret_code_panel(self) -> None:
        """Przywraca ikony kłódek (pytajniki) w panelu ukrytego kodu przed rozpoczęciem nowej rozgrywki."""
        while self.code_slots_layout.count():
            item = self.code_slots_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        for _ in range(4):
            lock_slot: QFrame = QFrame()
            lock_slot.setFixedSize(52, 52)
            lock_slot.setStyleSheet("QFrame { background-color: #161925; border: 2px solid #2d3748; border-radius: 12px; }")
            
            inner_layout: QHBoxLayout = QHBoxLayout(lock_slot)
            inner_layout.setContentsMargins(4, 4, 4, 4)
            inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            slot_lock: QLabel = self.create_image_icon("lock.png", 34, 34)
            inner_layout.addWidget(slot_lock)
            self.code_slots_layout.addWidget(lock_slot)


class MastermindNeonUI(QMainWindow):
    """Główne okno aplikacji zarządzające nawigacją ekranów oraz efektami wizualnymi."""

    def __init__(self) -> None:
        """Inicjalizuje główne okno, wczytuje arkusz stylów CSS i konfiguruje ekrany."""
        super().__init__()
        self.setWindowTitle("Mastermind")
        self.resize(1240, 820)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0e15; }
            QLabel { font-family: 'Segoe UI', Helvetica, sans-serif; }
            QFrame#Card { background-color: #141622; border-radius: 12px; border: 1px solid #1f2336; }
        """)

        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.game_screen: GameScreen = GameScreen(self.add_glow_effect)
        self.menu_screen: MainMenu = MainMenu(self.change_screen, set_pvp_callback=self.game_screen.set_pvp_mode)

        self.stacked_widget.addWidget(self.menu_screen) 
        self.stacked_widget.addWidget(self.game_screen) 

        self.stacked_widget.setCurrentIndex(0)

    def change_screen(self, index: int) -> None:
        """
        Zmienia aktywny ekran w elemencie QStackedWidget.

        :param index: Indeks docelowego ekranu (np. 0 dla menu, 1 dla gry).
        """
        self.stacked_widget.setCurrentIndex(index)

    def add_glow_effect(self, widget: QWidget, color_hex: str, radius: int = 10) -> None:
        """
        Nakłada neonowy efekt poświaty zewnętrznej na wskazany widget.

        :param widget: Widget PySide6, do którego zostanie dodany efekt.
        :param color_hex: Kolor poświaty w formacie HEX.
        :param radius: Promień rozmycia poświaty.
        """
        glow: QGraphicsDropShadowEffect = QGraphicsDropShadowEffect()
        glow.setBlurRadius(radius)
        glow.setColor(QColor(color_hex))
        glow.setOffset(0, 0)
        widget.setGraphicsEffect(glow)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    window: MastermindNeonUI = MastermindNeonUI()
    window.show()
    sys.exit(app.exec())
