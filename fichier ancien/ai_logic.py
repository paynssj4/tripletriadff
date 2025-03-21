import random
from card import Card  # Importer la classe Card

class AIPlayer:
    def __init__(self, deck):
        if len(deck) < 5:
            raise ValueError("Le deck de l'IA contient moins de 5 cartes.")
        self.hand = random.sample(deck, 5)

    def play_card(self, game_logic, fenetre, dessiner_plateau, capture_sound):
        best_position = None
        best_card = None
        best_score = -1  # Initialiser le score à -1 pour éviter de jouer une carte sans capture

        for position in [i for i, x in enumerate(game_logic.game_board) if x is None]:  # Parcourir les positions libres
            for card in self.hand:  # Parcourir les cartes de la main de l'IA
                score = self.evaluate_move(game_logic, card, position)  # Évaluer le score du mouvement
                if score > best_score:  # Mettre à jour la meilleure carte et la meilleure position si le score est meilleur
                    best_score = score
                    best_position = position
                    best_card = card

        if best_position is not None and best_card is not None:  # Jouer la carte si une capture est possible
            return best_position, best_card
        return None, None  # Ne pas jouer de carte si aucune capture n'est possible

    def evaluate_move(self, game_logic, card, position):
        score = 0
        adjacent_positions = self.get_adjacent_positions(position)  # Obtenir les positions adjacentes

        for adj_pos in adjacent_positions:
            adj_card = game_logic.game_board[adj_pos]
            if adj_card is not None and adj_card.background_path.endswith('cardbleu.png'):  # Vérifier si la carte adjacente appartient au joueur
                if self.can_capture(card, adj_card, position, adj_pos):  # Vérifier si la carte peut capturer la carte adjacente
                    score += 1  # Augmenter le score pour chaque capture possible

        return score

    def get_adjacent_positions(self, position):
        # Retourne la liste des positions adjacentes à la position donnée
        adjacent_positions = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }
        return adjacent_positions[position]

    def can_capture(self, card, adj_card, position, adj_pos):
        # Vérifie si la carte peut capturer la carte adjacente en fonction de leurs positions et de leurs valeurs
        if adj_pos == position - 1:  # Gauche
            return card.numbers[1] > adj_card.numbers[3]
        elif adj_pos == position + 1:  # Droite
            return card.numbers[3] > adj_card.numbers[1]
        elif adj_pos == position - 3:  # Haut
            return card.numbers[0] > adj_card.numbers[2]
        elif adj_pos == position + 3:  # Bas
            return card.numbers[2] > adj_card.numbers[0]
        return False