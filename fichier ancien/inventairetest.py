from PyQt5.QtGui import QPixmap  # Import QPixmap from PyQt5.QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QCheckBox, QPushButton, QMessageBox, QFrame, QVBoxLayout, QScrollArea, QApplication  # Correction ici

from card import Card
import json
import os



class InventoryManager(QScrollArea):
    def __init__(self, parent, deck):
        super().__init__(parent)
        self.parent = parent
        self.deck = deck
        self.selected_cards = []
        self.card_vars = {}
        self.card_images = {}

        self.setWidgetResizable(True)
        self.scrollable_frame = QFrame()
        self.setWidget(self.scrollable_frame)
        self.scrollable_layout = QVBoxLayout(self.scrollable_frame)

        self.load_selected_cards()
        self.display_inventory()

    def display_inventory(self):
        # Effacer le contenu actuel de l'inventaire
        for i in reversed(range(self.scrollable_layout.count())):
            widget = self.scrollable_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Afficher l'étiquette "Your Cards"
        inventory_label = QLabel("Your Cards", self.scrollable_frame)
        self.scrollable_layout.addWidget(inventory_label)

        # Afficher les cartes de l'inventaire
        for card in self.deck:
            card_var = QCheckBox(str(card), self.scrollable_frame)
            self.card_vars[card.name] = card_var
            self.scrollable_layout.addWidget(card_var)

            try:
                # Charger l'image de la carte
                img = QPixmap(card.image).scaled(100, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.card_images[card.name] = img
                label = QLabel(self.scrollable_frame)
                label.setPixmap(img)
                self.scrollable_layout.addWidget(label)
            except FileNotFoundError:
                # Afficher un message si l'image n'est pas trouvée
                label = QLabel("Image not found", self.scrollable_frame)
                self.scrollable_layout.addWidget(label)

            # Connecter l'état de la case à cocher à la fonction update_selected_cards
            card_var.stateChanged.connect(lambda state, c=card, v=card_var: self.update_selected_cards(c, v))

        # Bouton pour rafraîchir l'inventaire
        refresh_button = QPushButton("Refresh", self.scrollable_frame)
        refresh_button.clicked.connect(self.display_inventory)
        self.scrollable_layout.addWidget(refresh_button)

        # Afficher l'or du joueur
        self.gold_label = QLabel(f"Gold: {self.parent.gold}", self.scrollable_frame)
        self.scrollable_layout.addWidget(self.gold_label)

    def update_selected_cards(self, card, card_var):
        # Mettre à jour la liste des cartes sélectionnées
        if card_var.isChecked():
            if len(self.selected_cards) < 5:
                self.selected_cards.append(card)
            else:
                QMessageBox.warning(self.parent, "Selection Limit", "You can only select up to 5 cards.")
                card_var.setChecked(False)
        else:
            if card in self.selected_cards:
                self.selected_cards.remove(card)

        # Sauvegarder les cartes sélectionnées
        self.save_selected_cards()

    def save_selected_cards(self):
        # Sauvegarder les cartes sélectionnées dans un fichier JSON
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with open('selected_cards.json', 'w') as f:
            json.dump(selected_cards_data, f)

    def load_selected_cards(self):
        # Charger les cartes sélectionnées depuis un fichier JSON
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                try:
                    selected_cards_data = json.load(f)
                    self.selected_cards = [Card(**card_data) for card_data in selected_cards_data]
                    for card in self.selected_cards:
                        if card.name in self.card_vars:
                            self.card_vars[card.name].setChecked(True)
                except json.JSONDecodeError:
                    pass