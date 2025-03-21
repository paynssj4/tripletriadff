from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QInputDialog, QMessageBox, QTabWidget, QScrollArea, QFrame, QCheckBox, QMenu
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage  # Importer QImage
import irc.client
import logging
import threading
import json
import os
import random
import socket
import sys
from ai import AIPlayer
from card import Card
from triple_triad_game import TripleTriadGame

logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
CARDS_FILE = '/media/greg/FE1812A418125BC9/test jeux tt/Nouveau dossier/fichier ancien/cards.json'

# Créer une instance de QApplication
qt_app = QApplication(sys.argv)

class IRCClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRC Client")
        self.setGeometry(100, 100, 800, 600)

        self.username = self.authenticate_user()
        if not self.username:
            return

        self.nickname, ok = QInputDialog.getText(self, "Create IRC Nickname", "Enter your IRC nickname:")
        if not ok or not self.nickname:
            QMessageBox.critical(self, "Error", "Nickname is required.")
            self.close()
            return

        self.channel = '#Dialogues'

        self.notebook = QTabWidget(self)
        self.main_tab = QWidget()
        self.notebook.addTab(self.main_tab, self.channel)

        self.inventory_tab = QWidget()
        self.notebook.addTab(self.inventory_tab, "Inventaire")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.notebook)

        self.initialize_user_interface()
        self.connect_to_server()

        # Initialiser le socket pour la communication entre les joueurs
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 0))  # Bind to any available port
        self.socket.listen(1)
        self.port = self.socket.getsockname()[1]

        # Démarrer le thread pour écouter les connexions entrantes
        threading.Thread(target=self.listen_for_connections, daemon=True).start()

    def authenticate_user(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)

        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        response = QMessageBox.question(self, "Authentication", "Do you have an account?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            username, ok = QInputDialog.getText(self, "Login", "Enter your username:")
            password, ok = QInputDialog.getText(self, "Login", "Enter your password:", QLineEdit.Password)

            if username in users and users[username]['password'] == password:
                QMessageBox.information(self, "Login", "Login successful!")
                self.deck = [Card(**card_data) for card_data in users[username]['deck']]
                self.gold = users[username].get('gold', 100)
                self.experience = users[username].get('experience', 0)
                self.level = users[username].get('level', 1)
                return username
            else:
                QMessageBox.critical(self, "Login", "Invalid username or password.")
                return self.authenticate_user()
        else:
            username, ok = QInputDialog.getText(self, "Create Account", "Enter your username:")
            password, ok = QInputDialog.getText(self, "Create Account", "Enter your password:", QLineEdit.Password)

            if username in users:
                QMessageBox.critical(self, "Create Account", "Username already exists.")
                return self.authenticate_user()
            else:
                initial_deck = create_initial_deck(CARDS_FILE)

        users[username] = {
            'password': password,
            'deck': [card.to_dict() for card in initial_deck],
            'gold': 100,
            'experience': 0,
            'level': 1
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        QMessageBox.information(self, "Create Account", "Account created successfully!")
        self.deck = initial_deck
        self.gold = 100
        self.experience = 0
        self.level = 1
        return username

    def initialize_user_interface(self):
        self.initialize_main_tab()
        self.initialize_inventory_tab()

    def initialize_main_tab(self):
        layout = QVBoxLayout(self.main_tab)

        self.chat_area = QTextEdit(self.main_tab)
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        self.message_entry = QLineEdit(self.main_tab)
        layout.addWidget(self.message_entry)
        self.message_entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send", self.main_tab)
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_message)

        self.solo_game_button = QPushButton("Start Solo Game", self.main_tab)
        layout.addWidget(self.solo_game_button)
        self.solo_game_button.clicked.connect(self.start_solo_game)

        self.status_label = QLabel("Connecting...", self.main_tab)
        layout.addWidget(self.status_label)

        self.user_list = QListWidget(self.main_tab)
        layout.addWidget(self.user_list)
        self.user_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_list.customContextMenuRequested.connect(self.on_user_right_click)

        self.users = {}
        self.private_tabs = {}

    def initialize_inventory_tab(self):
        layout = QHBoxLayout(self.inventory_tab)

        self.card_vars = {}
        self.card_checkbuttons = []
        self.card_images = {}
        self.selected_cards = []

        self.scrolled_frame = QScrollArea(self.inventory_tab)
        self.scrolled_frame.setWidgetResizable(True)
        self.scrollable_frame = QFrame()
        self.scrolled_frame.setWidget(self.scrollable_frame)
        self.scrollable_layout = QVBoxLayout(self.scrollable_frame)
        layout.addWidget(self.scrolled_frame)

        self.selected_scrolled_frame = QScrollArea(self.inventory_tab)
        self.selected_scrolled_frame.setWidgetResizable(True)
        self.selected_scrollable_frame = QFrame()
        self.selected_scrolled_frame.setWidget(self.selected_scrollable_frame)
        self.selected_scrollable_layout = QVBoxLayout(self.selected_scrollable_frame)
        layout.addWidget(self.selected_scrolled_frame)

        self.display_inventory()
        self.load_selected_cards()

    def display_inventory(self):
        for i in reversed(range(self.scrollable_layout.count())):
            widget = self.scrollable_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        inventory_label = QLabel("Your Cards", self.scrollable_frame)
        self.scrollable_layout.addWidget(inventory_label)

        for card in self.deck:
            card_var = QCheckBox(str(card), self.scrollable_frame)
            self.card_vars[card.name] = card_var
            self.scrollable_layout.addWidget(card_var)

            try:
                # Charger l'image avec QImage
                image = QImage(card.image)
                # Convertir QImage en QPixmap
                img = QPixmap.fromImage(image).scaled(100, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.card_images[card.name] = img
                label = QLabel(self.scrollable_frame)
                label.setPixmap(img)
                self.scrollable_layout.addWidget(label)
            except FileNotFoundError:
                logging.error(f"Image file not found: {card.image}")
                label = QLabel("Image not found", self.scrollable_frame)
                self.scrollable_layout.addWidget(label)

            card_var.stateChanged.connect(lambda state, c=card, v=card_var: self.update_selected_cards(c, v))

        refresh_button = QPushButton("Refresh", self.scrollable_frame)
        refresh_button.clicked.connect(self.display_inventory)
        self.scrollable_layout.addWidget(refresh_button)

        self.gold_label = QLabel(f"Gold: {self.gold}", self.scrollable_frame)
        self.scrollable_layout.addWidget(self.gold_label)

    def update_selected_cards(self, card, card_var):
        if card_var.isChecked():
            if len(self.selected_cards) < 5:
                self.selected_cards.append(card)
            else:
                QMessageBox.warning(self, "Selection Limit", "You can only select up to 5 cards.")
                card_var.setChecked(False)
        else:
            if card in self.selected_cards:
                self.selected_cards.remove(card)

        self.display_selected_cards()
        self.save_selected_cards()

    def display_selected_cards(self):
        for i in reversed(range(self.selected_scrollable_layout.count())):
            widget = self.selected_scrollable_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        selected_label = QLabel("Selected Cards", self.selected_scrollable_frame)
        self.selected_scrollable_layout.addWidget(selected_label)

        for card in self.selected_cards:
            try:
                img = self.card_images[card.name]
                label = QLabel(self.selected_scrollable_frame)
                label.setPixmap(img)
                label.setText(str(card))
                label.setAlignment(Qt.AlignCenter)
                self.selected_scrollable_layout.addWidget(label)
            except KeyError:
                label = QLabel(str(card), self.selected_scrollable_frame)
                self.selected_scrollable_layout.addWidget(label)

    def save_selected_cards(self):
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with open('selected_cards.json', 'w') as f:
            json.dump(selected_cards_data, f)
        QMessageBox.information(self, "Save Selected Cards", "Selected cards have been saved successfully!")

    def load_selected_cards(self):
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                selected_cards_data = json.load(f)
            self.selected_cards = [Card(**card_data) for card_data in selected_cards_data]
            self.display_selected_cards()
        else:
            QMessageBox.warning(self, "Load Selected Cards", "No saved selected cards found.")

    def start_solo_game(self):
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                selected_cards_data = json.load(f)
            player_cards = [Card(**card_data) for card_data in selected_cards_data]

            ai_deck = create_initial_deck(CARDS_FILE)
            ai_player = AIPlayer(ai_deck)

            game = TripleTriadGame(player_cards, ai_player.hand, ai_player)
            game.show()
        else:
            QMessageBox.warning(self, "Solo Game", "No saved selected cards found.")

    def listen_for_connections(self):
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(1024)
            if data:
                message = data.decode('utf-8')
                if message.startswith('DEFY'):
                    opponent, cards_json = message.split(':', 1)
                    opponent_cards = json.loads(cards_json)
                    self.accept_defy(opponent, opponent_cards)

    def connect_to_server(self):
        self.server = 'irc.libera.chat'
        self.port = 6667

        self.reactor = irc.client.Reactor()
        try:
            self.connection = self.reactor.server().connect(self.server, self.port, self.nickname)
            self.connection.encoding = 'utf-8'
            self.connection.errors = 'ignore'
            self.connection.add_global_handler("welcome", self.on_connect)
            self.connection.add_global_handler("pubmsg", self.on_pubmsg)
            self.connection.add_global_handler("privmsg", self.on_privmsg)
            self.connection.add_global_handler("join", self.on_join)
            self.connection.add_global_handler("part", self.on_part)
            self.connection.add_global_handler("quit", self.on_quit)
            self.connection.add_global_handler("nick", self.on_nick)
            self.connection.add_global_handler("namreply", self.on_names)
            logging.info("Connected to the server")
        except irc.client.ServerConnectionError as e:
            logging.error(f"Could not connect to server: {e}")
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: red;")

    def on_connect(self, connection, event):
        logging.info("Server connection established.")
        connection.join(self.channel)
        self.status_label.setText("Connected")
        self.status_label.setStyleSheet("color: green;")
        logging.info("Joined channel")

    def on_pubmsg(self, connection, event):
        message = f"[{event.target}] {event.source.nick}: {event.arguments[0]}"
        self.display_message(self.chat_area, message)
        logging.info(f"Message received: {message}")

    def on_privmsg(self, connection, event):
        sender = event.source.nick
        message = f"[Private] {sender}: {event.arguments[0]}"
        if sender not in self.private_tabs:
            self.create_private_tab(sender)
        self.display_message(self.private_tabs[sender]['chat_area'], message)

        if event.arguments[0].strip() == "/accept":
            self.initiate_defy(sender)
        logging.info(f"Private message received: {message}")

    def send_message(self):
        message = self.message_entry.text()
        if message:
            self.connection.privmsg(self.channel, message)
            self.display_message(self.chat_area, f"[You]: {message}")
            self.message_entry.clear()
            logging.info(f"Message sent: {message}")

    def send_private_message(self, target):
        message, ok = QInputDialog.getText(self, "Private Message", f"Enter message to {target}:")
        if ok and message:
            self.connection.privmsg(target, message)
            if target not in self.private_tabs:
                self.create_private_tab(target)
            self.display_message(self.private_tabs[target]['chat_area'], f"[Private to {target}]: {message}")
            logging.info(f"Private message sent to {target}: {message}")

    def display_message(self, chat_area, message):
        chat_area.append(message)
        chat_area.verticalScrollBar().setValue(chat_area.verticalScrollBar().maximum())

    def on_join(self, connection, event):
        logging.info(f"{event.source.nick} joined the channel")
        self.users[event.source.nick] = event.source.nick
        self.update_user_list()

    def on_part(self, connection, event):
        logging.info(f"{event.source.nick} left the channel")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_quit(self, connection, event):
        logging.info(f"{event.source.nick} quit the channel")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_nick(self, connection, event):
        logging.info(f"{event.source.nick} changed nick to {event.target}")
        if event.source.nick in self.users:
            self.users[event.target] = self.users.pop(event.source.nick)
            self.update_user_list()

    def on_names(self, connection, event):
        logging.info("Received names list")
        users = event.arguments[2].split()
        for user in users:
            self.users[user] = user
        self.update_user_list()

    def update_user_list(self):
        self.user_list.clear()
        for user in sorted(self.users.keys()):
            self.user_list.addItem(user)

    def on_user_right_click(self, pos):
        item = self.user_list.itemAt(pos)
        if item:
            target = item.text()
            menu = QMenu(self.user_list)
            menu.addAction("Send Private Message", lambda: self.send_private_message(target))
            menu.addAction("Defy", lambda: self.defy_user(target))
            menu.exec_(self.user_list.mapToGlobal(pos))

    def defy_user(self, target):
        self.connection.privmsg(target, f"I challenge you to a Triple Triad game!\nType '/accept' to accept.")
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', self.port))
            s.sendall(f'DEFY:{json.dumps(selected_cards_data)}'.encode('utf-8'))

    def accept_defy(self, opponent, opponent_cards):
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                selected_cards_data = json.load(f)
            player_cards = [Card(**card_data) for card_data in selected_cards_data]

            game = TripleTriadGame(player_cards, opponent_cards)
            game.show()
        else:
            QMessageBox.warning(self, "Defy", "No saved selected cards found.")

    def create_private_tab(self, user):
        if user in self.private_tabs:
            return

        private_tab = QWidget()
        self.notebook.addTab(private_tab, f"Private - {user}")

        layout = QVBoxLayout(private_tab)
        chat_area = QTextEdit(private_tab)
        chat_area.setReadOnly(True)
        layout.addWidget(chat_area)

        self.private_tabs[user] = {'frame': private_tab, 'chat_area': chat_area}

    def run(self):
        self.show()

def create_initial_deck(cards_file: str, deck_size: int = 40):
    with open(cards_file, 'r') as f:
        all_cards_data = json.load(f)

    all_cards = [Card(card_data["name"], card_data["attribute"], card_data["numbers"], card_data["image"]) for card_data in all_cards_data]

    if len(all_cards) < deck_size:
        while len(all_cards) < deck_size:
            all_cards.append(random.choice(all_cards))

    deck = random.sample(all_cards, deck_size)
    return deck

def main():
    client = IRCClient()
    client.run()
    sys.exit(qt_app.exec_())

if __name__ == "__main__":
    main()