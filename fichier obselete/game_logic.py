import pygame
import random
import time

class GameLogic:
    def __init__(self):
        self.player_cards = []
        self.ai_cards = []
        self.game_board = [None] * 9  # Initialiser le plateau avec 9 positions
        self.current_turn = "player"  # Le joueur commence
        self.ai_timer = None  # Timer pour le délai de l'IA

    def start_game(self):
        self.next_turn()

    def next_turn(self):
        if self.current_turn == "player":
            self.current_turn = "ai"
            self.ai_timer = time.time()  # Démarrer le timer pour l'IA
        else:
            self.current_turn = "player"
            self.ai_timer = None  # Réinitialiser le timer

    def player_move(self, position, card):
        if self.current_turn == "player" and self.game_board[position] is None:
            self.game_board[position] = card
            self.player_cards.remove(card)  # Supprimer la carte de la main du joueur
            self.next_turn()

    def ai_move(self):
        if self.current_turn == "ai" and self.ai_timer and time.time() - self.ai_timer >= 5:
            available_positions = [i for i, x in enumerate(self.game_board) if x is None]
            if available_positions:
                position = random.choice(available_positions)
                card = random.choice(self.ai_cards)
                self.game_board[position] = card
                self.ai_cards.remove(card)
                self.next_turn()
                return position, card
        return None, None

def dessiner_plateau(fenetre):
    # Centrer le plateau dans la fenêtre
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2

    # Dessiner les lignes du plateau (simplifié)
    for i in range(1, 3):
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x + 150 * i, plateau_y), (plateau_x + 150 * i, plateau_y + 3 * 150), 2)  # Verticales
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x, plateau_y + 150 * i), (plateau_x + 3 * 150, plateau_y + 150 * i), 2)  # Horizontales

def dessiner_cartes(fenetre, cartes_joueur, cartes_ia, start_time):
    elapsed_time = time.time() - start_time
    delay = 0.5  # Délai entre chaque carte

    # Positionner les colonnes des cartes du joueur et de l'IA avec chevauchement
    for i, carte in enumerate(cartes_joueur):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)  # Limiter la position y pour qu'elle ne dépasse pas la position finale
            fenetre.blit(carte.image, (50, y_pos))  # Chevauchement vertical
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)  # Limiter la position y pour qu'elle ne dépasse pas la position finale
            fenetre.blit(carte.image, (LARGEUR_FENETRE - 150, y_pos))  # Chevauchement vertical

def dessiner_jeu(fenetre, game_logic, selected_card=None, mouse_pos=None, start_time=None):
    fenetre.fill((0, 0, 0))  # Remplir la fenêtre avec une couleur noire
    dessiner_plateau(fenetre)
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i, card in enumerate(game_logic.game_board):
        if card is not None:
            x = plateau_x + (i % 3) * 150
            y = plateau_y + (i // 3) * 150
            fenetre.blit(card.image, (x, y))  # Dessiner l'image de la carte par-dessus
    dessiner_cartes(fenetre, game_logic.player_cards, game_logic.ai_cards, start_time)
    
    # Dessiner le spinner pour indiquer le tour
    if game_logic.current_turn == "player":
        spinner_x = 50  # Position au-dessus de la colonne du joueur
    else:
        spinner_x = LARGEUR_FENETRE - 150  # Position au-dessus de la colonne de l'IA
    spinner_y = plateau_y - 50  # Ajuster la position du spinner
    pygame.draw.circle(fenetre, (255, 0, 0), (spinner_x, spinner_y), 10)  # Dessiner un cercle rouge pour le spinner
    
    # Dessiner la carte sélectionnée avec un léger mouvement
    if selected_card and mouse_pos:
        offset_x, offset_y = 5, 5  # Déplacement léger
        fenetre.blit(selected_card.image, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
    
    pygame.display.flip()