import pygame
import json
import random
import os
import time
from ai_logic import AIPlayer  # Importer la classe AIPlayer depuis le nouveau fichier
from card import Card  # Importer la classe Card

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
LARGEUR_FENETRE = 950
HAUTEUR_FENETRE = 554
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Triple Triad")

# Charger les données JSON
with open('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/selected_cards.json', 'r') as f:
    selected_cards_data = json.load(f)
with open('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/cards.json', 'r') as f:
    all_cards_data = json.load(f)

# Chemin du dossier des images
img_folder = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/Img'

# Charger les images de fond
fond_fenetre = pygame.image.load(os.path.join(img_folder, 'board-mat.jpg')).convert()
fond_carte_joueur = pygame.image.load(os.path.join(img_folder, 'cardbleu.png')).convert_alpha()
fond_carte_ia = pygame.image.load(os.path.join(img_folder, 'cardrouge.png')).convert_alpha()
spinner = pygame.image.load(os.path.join(img_folder, 'spinner.png')).convert_alpha()

# Redimensionner les images des cartes et du spinner
fond_carte_joueur = pygame.transform.scale(fond_carte_joueur, (100, 100))
fond_carte_ia = pygame.transform.scale(fond_carte_ia, (100, 100))
spinner = pygame.transform.scale(spinner, (50, 50))

# --- Classes et fonctions ---

class Card:
    def __init__(self, name, attribute, numbers, image, background):
        self.name = name
        self.attribute = attribute
        self.numbers = numbers
        self.image_path = os.path.join(img_folder, image)
        self.background_path = os.path.join(img_folder, background)
        if os.path.exists(self.image_path):
            self.image = pygame.image.load(self.image_path).convert_alpha()  # Charger l'image avec Pygame
            self.original_image = pygame.transform.scale(self.image, (100, 100))  # Image originale
            self.image = self.original_image  # Utiliser l'image originale par défaut
            self.background = pygame.image.load(self.background_path).convert_alpha()
            self.original_background = pygame.transform.scale(self.background, (100, 100))
            self.background = self.original_background
        else:
            raise FileNotFoundError(f"No file '{self.image_path}' found in working directory")

    def resize_for_cell(self, width, height):
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.background = pygame.transform.scale(self.original_background, (width, height))

class AIPlayer:
    def __init__(self, deck):
        self.hand = random.sample(deck, 5)

    def play_card(self, game_logic):
        available_positions = [i for i, x in enumerate(game_logic.game_board) if x is None]
        if available_positions and self.hand:
            position = random.choice(available_positions)
            card = random.choice(self.hand)
            card.resize_for_cell(150, 150)  # Redimensionner la carte pour la cellule
            game_logic.game_board[position] = card
            self.hand.remove(card)  # Retirer la carte de la main de l'IA
            return position, card
        return None, None

class GameLogic:
    def __init__(self, player_cards, ai_player):
        self.player_cards = player_cards
        self.ai_player = ai_player
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
            card.resize_for_cell(150, 150)  # Redimensionner la carte pour la cellule
            self.game_board[position] = card
            self.player_cards.remove(card)  # Supprimer la carte de la main du joueur
            self.next_turn()

    def ai_move(self):
        if self.current_turn == "ai" and self.ai_timer and time.time() - self.ai_timer >= 5:
            position, card = self.ai_player.play_card(self)
            if position is not None and card is not None:
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
            fenetre.blit(fond_carte_joueur, (50, y_pos))  # Chevauchement vertical
            fenetre.blit(carte.image, (50, y_pos))  # Dessiner l'image de la carte par-dessus
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)  # Limiter la position y pour qu'elle ne dépasse pas la position finale
            fenetre.blit(fond_carte_ia, (LARGEUR_FENETRE - 150, y_pos))  # Chevauchement vertical
            fenetre.blit(carte.image, (LARGEUR_FENETRE - 150, y_pos))  # Dessiner l'image de la carte par-dessus

def dessiner_jeu(fenetre, game_logic, selected_card=None, mouse_pos=None, start_time=None):
    fenetre.blit(fond_fenetre, (0, 0))  # Dessiner le fond de la fenêtre
    dessiner_plateau(fenetre)
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i, card in enumerate(game_logic.game_board):
        if card is not None:
            x = plateau_x + (i % 3) * 150
            y = plateau_y + (i // 3) * 150
            fenetre.blit(card.background, (x, y))  # Dessiner l'image de fond de la carte
            fenetre.blit(card.image, (x, y))  # Dessiner l'image de la carte par-dessus
    dessiner_cartes(fenetre, game_logic.player_cards, game_logic.ai_player.hand, start_time)
    
    # Dessiner le spinner pour indiquer le tour
    if game_logic.current_turn == "player":
        spinner_x = 50  # Position au-dessus de la colonne du joueur
    else:
        spinner_x = LARGEUR_FENETRE - 150  # Position au-dessus de la colonne de l'IA
    spinner_y = plateau_y - spinner.get_height() - 10
    fenetre.blit(spinner, (spinner_x, spinner_y))
    
    # Dessiner la carte sélectionnée avec un léger mouvement
    if selected_card and mouse_pos:
        offset_x, offset_y = 5, 5  # Déplacement léger
        fenetre.blit(selected_card.background, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
        fenetre.blit(selected_card.image, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
    
    pygame.display.flip()

# Créer les cartes du joueur et de l'IA
player_cards = [Card(**card_data, background='cardbleu.png') for card_data in selected_cards_data]
ai_deck = [Card(**card_data, background='cardrouge.png') for card_data in all_cards_data]
ai_player = AIPlayer(ai_deck)

# Initialiser la logique du jeu
game_logic = GameLogic(player_cards, ai_player)

# --- Boucle principale du jeu ---
running = True
selected_card_index = None  # Variable pour savoir quelle carte le joueur a sélectionnée.
start_time = time.time()

# Coordonnées des cellules adaptées à la nouvelle taille de la fenêtre
original_width = 1258
original_height = 734
new_width = LARGEUR_FENETRE
new_height = HAUTEUR_FENETRE
scale_x = new_width / original_width
scale_y = new_height / original_height

cell_coords = {
    "cell_1": {"x": 319, "y": 50, "width": 150, "height": 150},
    "cell_2": {"x": 525, "y": 50, "width": 150, "height": 150},
    "cell_3": {"x": 731, "y": 50, "width": 150, "height": 150},
    "cell_4": {"x": 319, "y": 260, "width": 150, "height": 150},
    "cell_5": {"x": 525, "y": 260, "width": 150, "height": 150},
    "cell_6": {"x": 731, "y": 260, "width": 150, "height": 150},
    "cell_7": {"x": 319, "y": 470, "width": 150, "height": 150},
    "cell_8": {"x": 525, "y": 470, "width": 150, "height": 150},
    "cell_9": {"x": 731, "y": 470, "width": 150, "height": 150},
}

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game_logic.current_turn == "player":
            x, y = event.pos

            # Vérifier si le clic est sur une carte du joueur
            for i, card in enumerate(player_cards):
                card_rect = pygame.Rect(50, 50 + i * 80, 100, 100)  # Chevauchement vertical
                if card_rect.collidepoint(x, y):
                    selected_card_index = i

            # Vérifier si le clic est sur une cellule du plateau
            for cell_name, coords in cell_coords.items():
                cell_rect = pygame.Rect(
                    int(coords["x"] * scale_x),
                    int(coords["y"] * scale_y),
                    int(coords["width"] * scale_x),
                    int(coords["height"] * scale_y)
                )
                if cell_rect.collidepoint(x, y) and selected_card_index is not None:
                    print(f"Clic sur {cell_name}")
                    # Placer la carte sélectionnée sur la cellule
                    card = player_cards[selected_card_index]
                    game_logic.player_move(list(cell_coords.keys()).index(cell_name), card)
                    selected_card_index = None

    if game_logic.current_turn == "ai":
        position, card = game_logic.ai_move()
        if position is not None and card is not None:
            print(f"AI placed {card.name} at position {position}")

    selected_card = player_cards[selected_card_index] if selected_card_index is not None else None
    dessiner_jeu(fenetre, game_logic, selected_card, mouse_pos, start_time)

pygame.quit()