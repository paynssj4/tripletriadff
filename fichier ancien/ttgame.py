import sys
import random
import json
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QFrame, QGridLayout
from PyQt5.QtGui import QPixmap, QPainter, QFont, QImage
from PyQt5.QtCore import Qt, QTimer
from card import Card  # Assurez-vous d'importer correctement la classe Card

logging.basicConfig(level=logging.INFO)

class TripleTriadGame(QWidget):
    def __init__(self, player_cards, opponent_cards, ai_player=None):
        super().__init__()
        self.player_cards = player_cards
        self.opponent_cards = opponent_cards
        self.ai_player = ai_player
        self.game_board = [None] * 9  # Un tableau pour représenter le plateau de jeu
        self.selected_card = None
        self.current_turn = "player" if random.choice([True, False]) else "opponent"

        self.load_images()
        self.load_coordinates()
        self.initUI()

    def load_images(self):
        self.card_back_blue = QPixmap("path/to/cardbleu.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.card_back_red = QPixmap("path/to/cardrouge.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.board_image = QPixmap("path/to/board-mat.jpg").scaled(1258, 734, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def load_coordinates(self):
        try:
            with open("path/to/coordinates.json", 'r') as f:
                self.coordinates = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error loading coordinates: {e}")
            self.coordinates = {}

    def initUI(self):
        self.setWindowTitle('Triple Triad Game')
        self.setGeometry(100, 100, 1258, 734)

        # Set background image
        self.background = QLabel(self)
        self.background.setPixmap(self.board_image)
        self.background.setGeometry(0, 0, 1258, 734)

        # Create layout
        main_layout = QVBoxLayout()

        # Create turn indicator
        self.turn_indicator = QLabel('Your Turn', self)
        self.turn_indicator.setFont(QFont("Arial", 16))
        self.turn_indicator.setStyleSheet("color: red; background-color: rgba(255, 255, 255, 0);")
        self.turn_indicator.setAlignment(Qt.AlignCenter)
        self.turn_indicator.setGeometry(600, 10, 200, 30)

        # Create player and opponent card areas
        user_column = self.coordinates.get("user_column", {"x": 0, "y": 0, "width": 319, "height": 736})
        self.player_area = QScrollArea(self)
        self.player_area.setGeometry(user_column["x"], user_column["y"], user_column["width"], user_column["height"])
        self.player_area.setWidgetResizable(True)
        self.player_area.setStyleSheet("background: transparent; border: none;")
        self.player_frame = QFrame()
        self.player_frame.setStyleSheet("background: transparent;")
        self.player_area.setWidget(self.player_frame)
        self.player_layout = QVBoxLayout(self.player_frame)

        ai_column = self.coordinates.get("opponent_column", {"x": 937, "y": 2, "width": 317, "height": 730})
        self.opponent_area = QScrollArea(self)
        self.opponent_area.setGeometry(ai_column["x"], ai_column["y"], ai_column["width"], ai_column["height"])
        self.opponent_area.setWidgetResizable(True)
        self.opponent_area.setStyleSheet("background: transparent; border: none;")
        self.opponent_frame = QFrame()
        self.opponent_frame.setStyleSheet("background: transparent;")
        self.opponent_area.setWidget(self.opponent_frame)
        self.opponent_layout = QVBoxLayout(self.opponent_frame)

        # Create game board
        self.board_frame = QFrame(self)
        self.board_frame.setGeometry(319, 50, 619, 630)
        self.board_frame.setStyleSheet("background: transparent;")
        self.board_layout = QGridLayout(self.board_frame)

        self.update_turn_indicator()
        self.display_board()
        self.display_player_cards()
        self.display_opponent_cards()

        self.setLayout(main_layout)

    def display_board(self):
        self.cells = []
        for i in range(1, 10):
            cell_coords = self.coordinates.get(f"cell_{i}", {"x": 0, "y": 0, "width": 206, "height": 210})
            cell = QLabel(self.board_frame)
            cell.setFixedSize(cell_coords["width"], cell_coords["height"])
            cell.setStyleSheet("border: 2px solid black; background-color: rgba(255, 255, 255, 0);")
            cell.mousePressEvent = lambda event, idx=i-1: self.place_player_card(idx // 3, idx % 3)
            self.board_layout.addWidget(cell, (i-1)//3, (i-1)%3)
            self.cells.append(cell)

    def display_player_cards(self):
        player_label = QLabel("Your Cards", self.player_frame)
        player_label.setFont(QFont("Arial", 16))
        player_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.player_layout.addWidget(player_label)

        for card in self.player_cards:
            img = QPixmap(card.get_image()).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            combined_img = QPixmap(self.card_back_blue.size())
            painter = QPainter(combined_img)
            painter.drawPixmap(0, 0, self.card_back_blue)
            painter.drawPixmap(0, 0, img)
            painter.end()
            card_label = QLabel(self.player_frame)
            card_label.setPixmap(combined_img)
            card_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
            card_label.mousePressEvent = lambda event, c=card, cl=card_label: self.select_card(event, c, cl)
            self.player_layout.addWidget(card_label)

    def display_opponent_cards(self):
        opponent_label = QLabel("Opponent's Cards", self.opponent_frame)
        opponent_label.setFont(QFont("Arial", 16))
        opponent_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.opponent_layout.addWidget(opponent_label)

        for card in self.opponent_cards:
            img = QPixmap(card.get_image()).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            combined_img = QPixmap(self.card_back_red.size())
            painter = QPainter(combined_img)
            painter.drawPixmap(0, 0, self.card_back_red)
            painter.drawPixmap(0, 0, img)
            painter.end()
            card_label = QLabel(self.opponent_frame)
            card_label.setPixmap(combined_img)
            card_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
            self.opponent_layout.addWidget(card_label)

    def select_card(self, event, card, card_label):
        if self.current_turn == "player":
            self.selected_card = card
            self.selected_card_label = card_label
            card_label.raise_()  # Apporter la carte sélectionnée au premier plan

    def place_player_card(self, row, col):
        if self.selected_card and self.current_turn == "player":
            index = row * 3 + col
            if self.game_board[index] is None:
                self.game_board[index] = self.selected_card
                self.update_board_ui()
                self.selected_card_label.hide()
                self.selected_card = None
                self.selected_card_label = None
                self.current_turn = "opponent"
                self.update_turn_indicator()
                QTimer.singleShot(5000, self.ai_turn)  # Attendre 5 secondes avant que l'IA ne joue

    def ai_turn(self):
        if self.current_turn == "opponent":
            position, card = self.ai_player.make_move(self.game_board)
            logging.info(f"AI's hand before playing: {self.opponent_cards}")
            if card in self.opponent_cards:
                self.opponent_cards.remove(card)  # Retirer la carte de la main de l'IA
                logging.info(f"AI played card: {card}. Remaining cards: {len(self.opponent_cards)}")
            else:
                logging.error(f"Error: Card {card} not found in AI's hand.")

            self.game_board[position] = card
            self.update_board_ui()
            self.current_turn = "player"
            self.update_turn_indicator()

    def update_board_ui(self):
        for i, card in enumerate(self.game_board):
            if card is not None:
                img = QPixmap(card.get_image()).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                combined_img = QPixmap(self.card_back_blue.size())
                painter = QPainter(combined_img)
                if card in self.player_cards:
                    painter.drawPixmap(0, 0, self.card_back_blue)
                else:
                    painter.drawPixmap(0, 0, self.card_back_red)
                painter.drawPixmap(0, 0, img)
                painter.end()
                self.cells[i].setPixmap(combined_img)

    def update_turn_indicator(self):
        if self.current_turn == "player":
            self.turn_indicator.setText("Your Turn")
        else:
            self.turn_indicator.setText("Opponent's Turn")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player_cards = []  # Add sample card objects here for testing
    opponent_cards = []  # Add sample card objects here for testing
    game = TripleTriadGame(player_cards, opponent_cards)
    game.show()
    sys.exit(app.exec_())
