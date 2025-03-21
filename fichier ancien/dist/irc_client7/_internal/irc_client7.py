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
import asyncio
import zmq
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

# Obtenez le répertoire du script en cours d'exécution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) #Ajout de cette ligne pour obtenir le repertoire du fichier

#Constantes pour les chemins de fichiers et les paramètres (maintenant relatifs au script)
# Modification des paths pour qu'il soit en fonction du script
USERS_FILE = os.path.join(SCRIPT_DIR, 'users.json') # Modification
CARDS_FILE = os.path.join(SCRIPT_DIR, 'cards.json') # Modification
SELECTED_CARDS_FILE = os.path.join(SCRIPT_DIR, 'selected_cards.json') # Modification
TRIPLE_TRIAD_GAME_FILE = os.path.join(SCRIPT_DIR, 'test_jeux_tt2.py') # Modification
IMG_FOLDER = os.path.join(SCRIPT_DIR, 'Img') # Modification

class WebSocketClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroMQ Client")
        self.setGeometry(100, 100, 800, 600)

        self.username = self.authenticate_user()
        if not self.username:
            sys.exit(1)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.notebook = QTabWidget()
        self.layout.addWidget(self.notebook)

        self.main_tab = QWidget()
        self.notebook.addTab(self.main_tab, "Chat")
        self.initialize_main_tab()

        self.inventory_tab = QWidget()
        self.notebook.addTab(self.inventory_tab, "Inventaire")

        self.users = {}
        self.private_tabs = {}

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:5555")

        self.deck = []  # Initialisation de self.deck
        self.gold = 0  # Initialisation de self.gold
        self.gold_label = QLabel()  # Initialisation de self.gold_label

        self.initialize_inventory_tab()  # Appel après l'initialisation de self.gold_label

        self.listen_thread = threading.Thread(target=self.listen_to_server)
        self.listen_thread.start()

    def initialize_main_tab(self):
        """Initialise l'onglet principal (Chat)."""
        layout = QVBoxLayout(self.main_tab)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        self.message_entry = QLineEdit()
        layout.addWidget(self.message_entry)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

    def authenticate_user(self):
        username, ok = QInputDialog.getText(self, "Nom d'utilisateur", "Entrez votre nom d'utilisateur :")
        if ok and username:
            return username
        return None

    def load_user_deck(self):
        """Charge le deck de l'utilisateur à partir du fichier users.json."""
        try:
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
            user_data = users_data.get(self.username, {})
            self.deck = [Card(**card_data) for card_data in user_data.get('deck', [])]
            self.gold = user_data.get('gold', 0)  # Charger la valeur de gold
            logging.info(f"Deck chargé pour l'utilisateur {self.username}: {self.deck}")
        except FileNotFoundError:
            logging.error(f"Fichier {USERS_FILE} non trouvé.")
        except json.JSONDecodeError as e:
            logging.error(f"Erreur lors de la déserialisation JSON : {e}")
        except Exception as e:
            logging.error(f"Une erreur non prévue est survenue : {e}")

    def initialize_inventory_tab(self):
        layout = QVBoxLayout(self.inventory_tab)
        self.card_vars = {}
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

        self.gold_label.setText(f"Or : {self.gold}")  # Initialiser le texte de l'or
        layout.addWidget(self.gold_label)  # Ajouter le label de l'or en dehors de la liste

        self.load_user_deck()  # Charger le deck de l'utilisateur
        self.display_inventory()

        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_selection)
        layout.addWidget(save_button)

        clear_button = QPushButton("Effacer")
        clear_button.clicked.connect(self.clear_selection)
        layout.addWidget(clear_button)

        self.load_selected_cards()

        # Ajouter le bouton pour lancer une partie en solo
        start_solo_game_button = QPushButton("Démarrer une partie solo")
        start_solo_game_button.clicked.connect(self.start_solo_game)
        layout.addWidget(start_solo_game_button)

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
            card_label = QLabel()
            image_path = os.path.join(IMG_FOLDER, card.img_path)
            image = QPixmap(image_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Ajuster la taille des cartes

            # Utiliser Pygame pour dessiner les chiffres sur l'image
            pygame_image = pygame.image.load(image_path)
            pygame_image = pygame.transform.scale(pygame_image, (150, 150))
            card.draw_numbers(pygame_image, pygame.font.SysFont("Arial", 24, bold=True))

            # Convertir l'image Pygame en QImage
            pygame_image_data = pygame.image.tostring(pygame_image, "RGBA")
            qimage = QImage(pygame_image_data, 150, 150, QImage.Format_RGBA8888)

            # Convertir QImage en QPixmap
            image = QPixmap.fromImage(qimage)

            card_label.setPixmap(image)
            card_label.mousePressEvent = lambda event, c=card: self.update_selected_cards(c)  # Utiliser un clic pour sélectionner la carte
            self.scrollable_layout.addWidget(card_label)
            self.card_images[card.name] = image

    def update_selected_cards(self, card):
        """Met à jour la liste des cartes sélectionnées."""
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            if len(self.selected_cards) < 5:
                self.selected_cards.append(card)
            else:
                QMessageBox.warning(self, "Limite de sélection", "Vous ne pouvez sélectionner que 5 cartes maximum.")

        self.display_selected_cards()

    def display_selected_cards(self):
        """Affiche les cartes sélectionnées."""
        combined_width = len(self.selected_cards) * 160
        combined_image = QImage(combined_width, 150, QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        x_offset = 0
        for card in self.selected_cards:
            try:
                img = self.card_images[card.name].scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        else:
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
            subprocess.Popen(["python", TRIPLE_TRIAD_GAME_FILE])
        else:
            QMessageBox.warning(self, "Partie solo", "Aucune carte sélectionnée n'a été trouvée.")

    def send_message(self):
        message = self.message_entry.text()
        if message:
            self.socket.send_json({"type": "message", "content": message, "username": self.username})
            self.chat_area.append(f"[Vous]: {message}")
            self.message_entry.clear()

    def listen_to_server(self):
        while True:
            message = self.socket.recv_json()
            if message["type"] == "message":
                self.chat_area.append(f"[{message['username']}]: {message['content']}")

    def on_user_right_click(self, pos):
        item = self.user_list.itemAt(pos)
        if item:
            target = item.text()
            menu = QMenu(self.user_list)
            menu.addAction("Défier", lambda: self.defy_user(target))
            menu.exec_(self.user_list.mapToGlobal(pos))

    def defy_user(self, target):
        self.socket.send_json({"type": "challenge", "opponent": target, "username": self.username})

    def closeEvent(self, event):
        """Ferme proprement le contexte ZeroMQ et arrête le serveur."""
        self.socket.close()
        self.context.term()
        self.listen_thread.join()
        event.accept()

    def run(self):
        self.show()

def compile_with_pyinstaller():
    """Compile le script avec PyInstaller."""
    script_path = os.path.abspath(__file__)
    subprocess.call(['pyinstaller', '--onefile', script_path])

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'compile':
            compile_with_pyinstaller()
        else:
            app = QApplication(sys.argv)
            client = WebSocketClient()
            client.run()
            sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution principale : {e}")
        print(f"Erreur : {e}")