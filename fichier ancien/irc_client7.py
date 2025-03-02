import json
import logging
import os
import random
import socket
import subprocess
import sys
import threading
import pygame
import irc.client
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFrame,
                             QHBoxLayout, QInputDialog, QLabel,
                             QLineEdit, QListWidget, QMainWindow,
                             QMessageBox, QMenu, QPushButton,
                             QScrollArea, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from card import Card  # Assurez-vous que card.py est dans le même répertoire

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
pygame.init()
pygame.display.set_mode((1, 1))  # Crée une petite fenêtre invisible
# Constantes pour les chemins de fichiers et les paramètres
USERS_FILE = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/users.json'
CARDS_FILE = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/cards.json'  # Ou le chemin complet vers votre fichier cards.json
SELECTED_CARDS_FILE = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/selected_cards.json'
TRIPLE_TRIAD_GAME_FILE = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/test_jeux_tt2.py'  # Ou le chemin complet vers votre fichier test_jeux_tt2.py
IMG_FOLDER = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/Img'  # Ou le chemin complet vers votre dossier d'images


class IRCClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRC Client")
        self.setGeometry(100, 100, 800, 600)

        # Authentification de l'utilisateur
        self.username = self.authenticate_user()
        if not self.username:
            sys.exit(1)

        # Demander le pseudo IRC
        self.nickname, ok = QInputDialog.getText(self, "Pseudo IRC", "Entrez votre pseudo IRC :")
        if not ok or not self.nickname:
            QMessageBox.critical(self, "Erreur", "Un pseudo est requis.")
            sys.exit(1)

        # Paramètres IRC
        self.server = 'irc.libera.chat'
        self.port = 6667
        self.channel = '#Dialogues'

        # Initialiser l'interface utilisateur
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.notebook = QTabWidget()
        self.layout.addWidget(self.notebook)

        # Onglet principal (chat)
        self.main_tab = QWidget()
        self.notebook.addTab(self.main_tab, self.channel)
        self.initialize_main_tab()

        # Onglet inventaire
        self.inventory_tab = QWidget()
        self.notebook.addTab(self.inventory_tab, "Inventaire")
        self.initialize_inventory_tab()

        # Connecter au serveur IRC
        self.connect_to_server()

        # Socket pour la communication directe avec d'autres joueurs
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 0))
        self.socket.listen(1)
        self.port = self.socket.getsockname()
        threading.Thread(target=self.listen_for_connections, daemon=True).start()

    def authenticate_user(self):
        """Authentifie l'utilisateur (connexion ou création de compte)."""
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)

        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        response = QMessageBox.question(self, "Authentification", "Avez-vous un compte ?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            return self.login(users)
        else:
            return self.create_account(users)

    def login(self, users):
        """Connecte l'utilisateur à un compte existant."""
        username, ok = QInputDialog.getText(self, "Connexion", "Nom d'utilisateur :")
        if not ok or not username:
            return None
        password, ok = QInputDialog.getText(self, "Connexion", "Mot de passe :", QLineEdit.Password)
        if not ok or not password:
            return None

        if username in users and users[username]['password'] == password:
            QMessageBox.information(self, "Connexion", "Connexion réussie !")
            self.load_user_data(username, users)
            return username
        else:
            QMessageBox.critical(self, "Connexion", "Nom d'utilisateur ou mot de passe incorrect.")
            return self.authenticate_user()

    def create_account(self, users):
        """Crée un nouveau compte utilisateur."""
        username, ok = QInputDialog.getText(self, "Créer un compte", "Nom d'utilisateur :")
        if not ok or not username:
            return None
        password, ok = QInputDialog.getText(self, "Créer un compte", "Mot de passe :", QLineEdit.Password)
        if not ok or not password:
            return None

        if username in users:
            QMessageBox.critical(self, "Créer un compte", "Ce nom d'utilisateur existe déjà.")
            return self.authenticate_user()
        else:
            initial_deck = self.create_initial_deck()
            users[username] = {
                'password': password,
                'deck': [card.to_dict() for card in initial_deck],
                'gold': 100,
                'experience': 0,
                'level': 1
            }
            with open(USERS_FILE, 'w') as f:
                json.dump(users, f)
            QMessageBox.information(self, "Créer un compte", "Compte créé avec succès !")
            self.load_user_data(username, users)
            return username

    def load_user_data(self, username, users):
        """Charge les données de l'utilisateur (deck, or, etc.)."""
        logging.info(f"Début de load_user_data pour l'utilisateur : {username}")
        self.deck = []
        for card_data in users[username].get('deck', []):
            try:
                # Extraction des valeurs pour le constructeur de Card
                card = Card(
                    name=card_data.get('name', ''),
                    attribute=card_data.get('attribute', ''),
                    numbers=card_data.get('numbers', [0, 0, 0, 0]),
                    background=card_data.get('background', 'cardbleu.png'),
                    img_path=card_data.get('img_path', '')
                )
                self.deck.append(card)
                logging.info(f"Carte chargée : {card.name} avec l'image : {card.img_path}")

            except Exception as e:
                logging.error(f"Erreur lors du chargement de la carte {card_data.get('name', 'inconnue')} : {e}")

        self.gold = users[username].get('gold', 100)
        self.experience = users[username].get('experience', 0)
        self.level = users[username].get('level', 1)
        logging.info(f"Fin de load_user_data : {len(self.deck)} cartes chargées")





    def create_initial_deck(self, deck_size=25):
        """Crée un deck initial aléatoire pour un nouveau joueur."""
        logging.info("Début de create_initial_deck")
        with open(CARDS_FILE, 'r') as f:
            all_cards_data = json.load(f)

        all_cards = []
        for card_data in all_cards_data:
            if "numbers" in card_data and len(card_data["numbers"]) == 4:
                try:
                    card = Card(
                        name=card_data.get("name", ""),
                        attribute=card_data.get("attribute", ""),
                        numbers=card_data["numbers"],
                        background="cardbleu.png",
                        img_path=card_data.get("img_path", "")
                    )

                    all_cards.append(card)
                    logging.info(f"Carte ajouté : {card.name} avec l'image : {card.img_path}")
                except Exception as e:
                    logging.error(f"Erreur lors de la création de la carte {card_data.get('name', 'inconnue')} : {e}")
            else:
                logging.error(f"Carte incomplète détectée : {card_data.get('name', 'inconnue')}")

        # Dupliquer les cartes si le nombre est insuffisant
        if len(all_cards) < deck_size and all_cards:
            while len(all_cards) < deck_size:
                all_cards.append(random.choice(all_cards))
                logging.info(f"Carte dupliquer car le deck n'a pas la bonne taille.")
        elif not all_cards:
            logging.error("Aucune carte valide trouvée dans cards.json.")
            return []  # Retourner un deck vide si aucune carte n'est valide.
        deck = random.sample(all_cards, min(deck_size, len(all_cards)))  # Utiliser min pour éviter une erreur si moins de 25 cartes
        logging.info(f"Fin de create_initial_deck {len(deck)} carte crée.")
        return deck






    def initialize_main_tab(self):
        """Initialise l'onglet principal (chat)."""
        layout = QVBoxLayout(self.main_tab)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        self.message_entry = QLineEdit()
        layout.addWidget(self.message_entry)
        self.message_entry.returnPressed.connect(self.send_message)

        send_button = QPushButton("Envoyer")
        layout.addWidget(send_button)
        send_button.clicked.connect(self.send_message)

        self.solo_game_button = QPushButton("Jouer en solo")
        layout.addWidget(self.solo_game_button)
        self.solo_game_button.clicked.connect(self.start_solo_game)

        self.status_label = QLabel("Connexion...")
        layout.addWidget(self.status_label)

        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        self.user_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_list.customContextMenuRequested.connect(self.on_user_right_click)

        self.users = {}
        self.private_tabs = {}

    def initialize_inventory_tab(self):
        """Initialise l'onglet inventaire."""
        layout = QHBoxLayout(self.inventory_tab)

        self.card_vars = {}
        self.card_checkboxes = {}
        self.card_images = {}
        self.selected_cards = []

        self.scrolled_frame = QScrollArea()
        self.scrolled_frame.setWidgetResizable(True)
        self.scrollable_frame = QFrame()
        self.scrolled_frame.setWidget(self.scrollable_frame)
        self.scrollable_layout = QVBoxLayout(self.scrollable_frame)
        layout.addWidget(self.scrolled_frame)

        self.selected_cards_area = QLabel()
        self.selected_cards_area.setAlignment(Qt.AlignTop)
        layout.addWidget(self.selected_cards_area)

        self.display_inventory()

        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_selection)
        layout.addWidget(save_button)

        clear_button = QPushButton("Effacer")
        clear_button.clicked.connect(self.clear_selection)
        layout.addWidget(clear_button)

        self.load_selected_cards()

    def display_inventory(self):
        """Affiche l'inventaire des cartes du joueur."""
        logging.info("Début de display_inventory")
        # Nettoyer le layout existant
        for i in reversed(range(self.scrollable_layout.count())):
            widget = self.scrollable_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        inventory_label = QLabel("Vos cartes")
        self.scrollable_layout.addWidget(inventory_label)

        # Vérifier et afficher les cartes
        logging.info(f"Nombre de cartes dans self.deck : {len(self.deck)}")
        if not self.deck:
            logging.warning("Le deck du joueur est vide.")
            no_cards_label = QLabel("Aucune carte dans votre deck.")
            self.scrollable_layout.addWidget(no_cards_label)
            return

        for card in self.deck:
            logging.info(f"Affichage de la carte : {card.name} avec l'image: {card.img_path}")
            card_var = QCheckBox(str(card.name))
            self.card_vars[card.name] = card_var
            self.scrollable_layout.addWidget(card_var)

            try:
                # Charger l'image avec QPixmap
                image_path = os.path.join(IMG_FOLDER, card.img_path)
                logging.info(f"Chargement de l'image : {image_path}")
                image = QPixmap(image_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)                
                self.card_images[card.name] = image
                label = QLabel()
                label.setPixmap(image)
                self.scrollable_layout.addWidget(label)
            except FileNotFoundError:
                logging.error(f"Fichier image non trouvé : {card.img_path}")
                label = QLabel("Image non trouvée")
                self.scrollable_layout.addWidget(label)
            except Exception as e:
                 logging.error(f"Erreur non prevue : {e}")

            card_var.stateChanged.connect(lambda state, c=card, v=card_var: self.update_selected_cards(c, v))

        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.display_inventory)
        self.scrollable_layout.addWidget(refresh_button)

        self.gold_label = QLabel(f"Or : {self.gold}")
        self.scrollable_layout.addWidget(self.gold_label)

    def update_selected_cards(self, card, card_var):
        """Met à jour la liste des cartes sélectionnées."""
        if card_var.isChecked():
            if len(self.selected_cards) < 5:
                self.selected_cards.append(card)
            else:
                QMessageBox.warning(self, "Limite de sélection", "Vous ne pouvez sélectionner que 5 cartes maximum.")
                card_var.setChecked(False)
        else:
            if card in self.selected_cards:
                self.selected_cards.remove(card)

        self.display_selected_cards()

    def display_selected_cards(self):
        """Affiche les cartes sélectionnées."""
        combined_width = len(self.selected_cards) * 60
        combined_image = QImage(combined_width, 50, QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        x_offset = 0
        for card in self.selected_cards:
            try:
                img = self.card_images[card.name]
                painter.drawPixmap(x_offset, 0, img)
                x_offset += img.width() + 10
            except KeyError:
                pass
        painter.end()
        pixmap = QPixmap.fromImage(combined_image)
        self.selected_cards_area.setPixmap(pixmap)

    def save_selection(self):
        """Sauvegarde la sélection actuelle de cartes."""
        logging.info("Début de save_selection")
        selected_cards_data = []
        for card in self.selected_cards:
            try:
                card_data = card.to_dict()
                card_data['background'] = card.background_path  # Ajouter le background ici
                selected_cards_data.append(card_data)
                logging.info(f"carte selectionner et sauvegarder : {card.name}")
            except Exception as e:
                logging.error(f"Erreur lors de la sauvegarde de la selection : {e}")

        with open(SELECTED_CARDS_FILE, 'w') as f:
            json.dump(selected_cards_data, f)
        logging.info("Fin de save_selection")
        QMessageBox.information(self, "Sauvegarde", "Les cartes sélectionnées ont été sauvegardées.")

 
 
    def load_selected_cards(self):
        """Charge la sélection de cartes sauvegardée."""
        logging.info("Début de load_selected_cards")
        self.selected_cards = []
        if os.path.exists(SELECTED_CARDS_FILE):
            try:
                with open(SELECTED_CARDS_FILE, 'r') as f:
                    selected_cards_data = json.load(f)
                for card_data in selected_cards_data:
                        card = Card(
                            name=card_data.get('name', ''),
                            attribute=card_data.get('attribute', ''),
                            numbers=card_data.get('numbers', [0, 0, 0, 0]),
                            background=card_data.get('background', 'cardbleu.png'),
                            img_path=card_data.get('img_path', '')
                        )
                        self.selected_cards.append(card)
                        logging.info(f"Carte selectionner et charger : {card.name}")
                self.display_selected_cards()

            except json.JSONDecodeError as e:
                logging.error(f"Erreur lors de la déserialisation JSON : {e}")
            except Exception as e:
                logging.error(f"Une erreur non prévue est survenue : {e}")
        else :
            logging.warning("fichier selected_cards.json non trouvé")
        logging.info("Fin de load_selected_cards")

    def clear_selection(self):
        """Efface la sélection actuelle de cartes."""
        for card_var in self.card_vars.values():
            card_var.setChecked(False)
        self.selected_cards = []
        self.display_selected_cards()

    def start_solo_game(self):
        """Démarre une partie en solo contre l'IA."""
        if os.path.exists(SELECTED_CARDS_FILE):
            subprocess.Popen(["python3", TRIPLE_TRIAD_GAME_FILE])
        else:
            QMessageBox.warning(self, "Partie solo", "Aucune carte sélectionnée n'a été trouvée.")

    def listen_for_connections(self):
        """Écoute les connexions entrantes pour les défis de jeu."""
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
        """Se connecte au serveur IRC."""
        self.reactor = irc.client.Reactor()
        try:
            self.connection = self.reactor.server().connect(self.server, self.port, self.nickname)
            self.connection.add_global_handler("welcome", self.on_connect)
            self.connection.add_global_handler("pubmsg", self.on_pubmsg)
            self.connection.add_global_handler("privmsg", self.on_privmsg)
            self.connection.add_global_handler("join", self.on_join)
            self.connection.add_global_handler("part", self.on_part)
            self.connection.add_global_handler("quit", self.on_quit)
            self.connection.add_global_handler("nick", self.on_nick)
            self.connection.add_global_handler("namreply", self.on_names)
            logging.info("Connecté au serveur")
        except irc.client.ServerConnectionError as e:
            logging.error(f"Impossible de se connecter au serveur : {e}")
            self.status_label.setText("Connexion échouée")
            self.status_label.setStyleSheet("color: red;")

    def on_connect(self, connection, event):
        """Gère l'événement de connexion au serveur."""
        connection.join(self.channel)
        self.status_label.setText("Connecté")
        self.status_label.setStyleSheet("color: green;")
        logging.info("Rejoint le canal")

    def on_pubmsg(self, connection, event):
        """Gère les messages publics reçus."""
        message = f"[{event.target}] {event.source.nick}: {event.arguments}"
        self.display_message(self.chat_area, message)
        logging.info(f"Message reçu : {message}")

    def on_privmsg(self, connection, event):
        """Gère les messages privés reçus."""
        sender = event.source.nick
        message = f"[Privé] {sender}: {event.arguments}"
        if sender not in self.private_tabs:
            self.create_private_tab(sender)
        self.display_message(self.private_tabs[sender]['chat_area'], message)

        # Accepter un défi de jeu
        if event.arguments.strip() == "/accept":
            self.accept_defy(sender)
        logging.info(f"Message privé reçu : {message}")

    def send_private_message(self, target):
        """Envoie un message privé à un utilisateur."""
        message, ok = QInputDialog.getText(self, "Message privé", f"Entrez votre message pour {target} :")
        if ok and message:
            self.connection.privmsg(target, message)
            if target not in self.private_tabs:
                self.create_private_tab(target)
            self.display_message(self.private_tabs[target]['chat_area'], f"[Privé à {target}]: {message}")
            logging.info(f"Message privé envoyé à {target} : {message}")

    def display_message(self, chat_area, message):
        """Affiche un message dans la zone de chat spécifiée."""
        chat_area.append(message)
        chat_area.verticalScrollBar().setValue(chat_area.verticalScrollBar().maximum())

    def on_join(self, connection, event):
        """Gère l'événement de connexion d'un utilisateur au canal."""
        logging.info(f"{event.source.nick} a rejoint le canal")
        self.users[event.source.nick] = event.source.nick
        self.update_user_list()

    def on_part(self, connection, event):
        """Gère l'événement de départ d'un utilisateur du canal."""
        logging.info(f"{event.source.nick} a quitté le canal")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_quit(self, connection, event):
        """Gère l'événement de déconnexion d'un utilisateur du serveur."""
        logging.info(f"{event.source.nick} a quitté le serveur")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_nick(self, connection, event):
        """Gère l'événement de changement de pseudo d'un utilisateur."""
        logging.info(f"{event.source.nick} a changé de pseudo pour {event.target}")
        if event.source.nick in self.users:
            self.users[event.target] = self.users.pop(event.source.nick)
            self.update_user_list()

    def on_names(self, connection, event):
        """Gère la réception de la liste des utilisateurs du canal."""
        logging.info("Liste des utilisateurs reçue")
        users = event.arguments.split()
        for user in users:
            self.users[user] = user
        self.update_user_list()

    def update_user_list(self):
        """Met à jour la liste des utilisateurs affichée."""
        self.user_list.clear()
        for user in sorted(self.users.keys()):
            self.user_list.addItem(user)

    def on_user_right_click(self, pos):
        """Gère le clic droit sur un utilisateur dans la liste."""
        item = self.user_list.itemAt(pos)
        if item:
            target = item.text()
            menu = QMenu(self.user_list)
            menu.addAction("Envoyer un message privé", lambda: self.send_private_message(target))
            menu.addAction("Défier", lambda: self.defy_user(target))
            menu.exec_(self.user_list.mapToGlobal(pos))

    def defy_user(self, target):
        """Envoie un défi de jeu à un utilisateur."""
        self.connection.privmsg(target, f"Je vous défie à une partie de Triple Triad !\nTapez '/accept' pour accepter.")
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', self.port))
            s.sendall(f'DEFY:{json.dumps(selected_cards_data)}'.encode('utf-8'))

    def accept_defy(self, opponent):
        """Accepte un défi de jeu."""
        if os.path.exists(SELECTED_CARDS_FILE):
            with open(SELECTED_CARDS_FILE, 'r') as f:
                selected_cards_data = json.load(f)
            player_cards = [Card(**card_data) for card_data in selected_cards_data]
            # Démarrer le jeu ici, en passant player_cards et opponent_cards comme arguments
            subprocess.Popen(["python3", TRIPLE_TRIAD_GAME_FILE])
        else:
            QMessageBox.warning(self, "Défi", "Aucune carte sélectionnée n'a été trouvée.")

    def create_private_tab(self, user):
        """Crée un onglet pour les messages privés avec un utilisateur."""
        if user in self.private_tabs:
            return

        private_tab = QWidget()
        self.notebook.addTab(private_tab, f"Privé - {user}")

        layout = QVBoxLayout(private_tab)
        chat_area = QTextEdit()
        chat_area.setReadOnly(True)
        layout.addWidget(chat_area)

        self.private_tabs[user] = {'frame': private_tab, 'chat_area': chat_area}

    def send_message(self):
        """Envoie un message public au canal."""
        message = self.message_entry.text()
        if message:
            self.connection.privmsg(self.channel, message)
            self.display_message(self.chat_area, f"[Vous]: {message}")
            self.message_entry.clear()
            logging.info(f"Message envoyé : {message}")

    def run(self):
        """Lance l'application."""
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = IRCClient()
    client.run()
    sys.exit(app.exec_())