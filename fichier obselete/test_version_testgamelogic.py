import random
from PyQt5.QtCore import pyqtSignal, QObject

class GameLogic(QObject):
    player_turn_signal = pyqtSignal(int, object)
    ai_turn_signal = pyqtSignal()

    def __init__(self, player_cards, ai_player, cells):
        super().__init__()
        self.player_cards = player_cards
        self.ai_player = ai_player
        self.cells = cells
        self.game_board = [None] * 9  # Initialiser le plateau avec 9 positions
        self.available_positions = list(range(9))  # Initialiser la liste des positions disponibles
        self.ai_cards = []  # Liste des cartes de l'IA
        self.triple_triad_game = cells  # Référence à l'instance de TripleTriadGame

    def start_game(self):
        # Initialiser la main du joueur et de l'IA
        self.player_cards = self.ai_player.initialize_hand()
        self.ai_cards = self.ai_player.initialize_hand()

        # Commencer le jeu
        self.next_turn()

    def ai_move(self):
        # Sélectionner une carte aléatoire de la main de l'IA
        ai_card = random.choice(self.ai_cards)

        # Sélectionner une position aléatoire sur le plateau
        position = random.choice(self.available_positions)

        # Vérifier si la position sélectionnée est valide
        if self.game_board[position] is None:
            # Placer la carte sur le plateau
            self.place_card(position, ai_card)

            # Mettre à jour l'affichage du plateau
            self.triple_triad_game.update_game_board(position, ai_card)
        else:
            # La position sélectionnée est déjà occupée, essayer une autre position
            self.ai_move()

    def next_turn(self):
        if self.current_turn == "player":
            # C'est au tour du joueur
            self.player_turn_signal.emit(self.current_turn, None)  # Émettre le signal player_turn
        else:
            # C'est au tour de l'IA
            self.ai_turn_signal.emit()  # Émettre le signal ai_turn

    def on_player_turn(self, position, card):
        # Logique pour le mouvement du joueur
        if position is not None and card is not None:
            # La carte a été placée avec succès
            self.place_card(position, card)
            self.update_game_board(position, card)
            self.player_cards.remove(card)  # Supprimer la carte de la liste de cartes du joueur
            self.available_positions.remove(position)  # Supprimer la position de la liste des positions disponibles

            # Vérifier si le joueur a gagné
            if self.check_winner():
                self.triple_triad_game.game_over_signal.emit("player")  # Émettre le signal game_over
                return

            # Passer au tour suivant
            self.next_turn()
        else:
            # La carte n'a pas été placée avec succès
            self.player_turn_signal.emit(self.current_turn, None)  # Émettre le signal player_turn

    def on_ai_turn(self):
        # Logique pour le mouvement de l'IA
        if len(self.ai_cards) > 0:
            # L'IA a des cartes à placer
            ai_card = random.choice(self.ai_cards)  # Sélectionner une carte aléatoire de la main de l'IA
            self.ai_cards.remove(ai_card)  # Supprimer la carte de la main de l'IA
            position = self.get_available_position()  # Sélectionner une position disponible sur le plateau
            self.place_card(position, ai_card)  # Placer la carte sur le plateau

            # Vérifier si l'IA a gagné
            if self.check_winner():
                self.triple_triad_game.game_over_signal.emit("ai")  # Émettre le signal game_over
                return

            # Mettre à jour l'affichage du plateau
            self.triple_triad_game.update_game_board(position, ai_card)

            # Passer au tour suivant
            self.next_turn()
        else:
            # L'IA n'a plus de cartes à placer
            self.next_turn()

    def place_card(self, position, card):
        # Placer la carte sur le plateau à la position spécifiée
        self.game_board[position] = card

        # Mettre à jour la liste des positions disponibles
        self.available_positions.remove(position)
