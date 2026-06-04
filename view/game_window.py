import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, 
                               QGraphicsDropShadowEffect, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap

class MainMenu(QWidget):
    """Main Menu class for game mode selection"""
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

        self.btn_player_vs_comp = QPushButton("Human vs AI")
        self.btn_player_vs_player = QPushButton("Human vs Hardware")
        self.btn_comp_vs_player = QPushButton("AI vs Human")

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
    """Main Game Interface class"""
    def __init__(self, add_glow_method):
        super().__init__()
        self.add_glow_method = add_glow_method
        
        # Main horizontal layout for 3 columns
        hbox_layout = QHBoxLayout(self)
        hbox_layout.setContentsMargins(20, 20, 20, 20)
        hbox_layout.setSpacing(20)

        # 1. LEFT COLUMN (Controls & Rules)

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

        for text in ["New Game", "Statistics", "Main Menu"]:
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
        rules_text = QLabel("Guess the secret code of 4 colored pegs.\nAfter each attempt, you get clues:\n\n• Black — right color & right spot\n• White — right color but wrong spot")
        rules_text.setStyleSheet("color: #a0aec0; font-size: 13px; line-height: 18px; background: transparent;")
        rules_text.setWordWrap(True)
        
        rules_layout.addWidget(rules_title)
        rules_layout.addWidget(rules_text)
        left_panel.addWidget(rules_card)
        left_panel.addStretch()
        
        hbox_layout.addLayout(left_panel, 1)

        # 2. CENTRAL COLUMN (Main Board + Palette)

        center_area = QVBoxLayout()
        center_area.setSpacing(12)

        # Scroll area for rows to prevent layout distortion
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

            # 1. Row number
            num_label = QLabel(f"{row + 1}")
            num_label.setFixedWidth(35)
            num_label.setStyleSheet("color: #4a5568; font-size: 13px; font-weight: bold; background: transparent;")
            row_layout.addWidget(num_label)
            
            # 2. Four pegs in a row
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
            
            # 3. Spacer
            row_layout.addStretch() 

            # 4. Hints strictly aligned
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

        # Input panel "YOUR MOVE"
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

        # Color palette
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
            palette_layout.addWidget(color_btn)
            
        center_area.addLayout(palette_layout)
        hbox_layout.addLayout(center_area, 4)

        # 3. RIGHT COLUMN (Statistics, AI Code)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # STATISTICS 
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

        stats_layout.addLayout(create_stat_row("Attempts"))
        stats_layout.addLayout(create_stat_row("Wins"))
        stats_layout.addLayout(create_stat_row("Best Score"))
        right_panel.addWidget(stats_card)

        # CODE 
        code_card = QFrame()
        code_card.setObjectName("Card")
        code_card.setFixedWidth(280)
        code_layout = QVBoxLayout(code_card)
        code_layout.setContentsMargins(18, 18, 18, 18)
        code_layout.setSpacing(15)

        code_header = QHBoxLayout()
        code_title = QLabel("CODE")
        code_title.setStyleSheet("font-weight: bold; color: #8a8dbe; font-size: 13px; letter-spacing: 1px; background: transparent;")
        
        code_icon = self.create_image_icon("lock.png", 18, 18)
        
        code_header.addWidget(code_title)
        code_header.addStretch()
        code_header.addWidget(code_icon)
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
        """Helper method to load images safely from the project folder"""
        lbl = QLabel()
        lbl.setStyleSheet("background: transparent;")
        if os.path.exists(filename):
            pixmap = QPixmap(filename)
            scaled_pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl.setPixmap(scaled_pixmap)
        else:
            lbl.setText("?")
            lbl.setStyleSheet("color: #4b5563; font-weight: bold; background: transparent;")
        return lbl


class MastermindNeonUI(QMainWindow):
    """Main Application Window"""
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
        self.stacked_widget.setCurrentIndex(index)

    def add_glow_effect(self, widget, color_hex, radius=10):
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
