import random
from card import Card  # Assurez-vous que cette importation est correcte en fonction de l'endroit où votre classe Card est définie

class AIPlayer:
    def __init__(self, deck):
        self.deck = deck
        self.hand = self.select_hand()

    def select_hand(self):
        # Sélectionner aléatoirement 5 cartes du deck pour la main de l'IA
        return random.sample(self.deck, 5)

    def make_move(self, game_board):
        # Implémenter la logique de l'IA pour choisir un mouvement
        # Pour simplifier, l'IA choisit un emplacement aléatoire vide et une carte aléatoire de sa main
        card = self.hand[0]  # Choisir une carte directement dans self.hand
        position = game_board.index(None)  # Trouver le premier emplacement libre
        return position, card