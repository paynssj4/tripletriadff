import pygame
import random
import os
import time
from ai_logic import AIPlayer #Import the AIPlayer

# Chemin du dossier des images
img_folder = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/Img'

# Police pour dessiner les nombres sur les cartes
font = pygame.font.SysFont(None, 24)

# Dimensions de la fenêtre (doivent être les mêmes que dans le fichier principal)
LARGEUR_FENETRE = 950
HAUTEUR_FENETRE = 554

# Charger les images de fond (doivent être les mêmes que dans le fichier principal)
fond_carte_joueur = pygame.image.load(os.path.join(img_folder, 'cardbleu.png')).convert_alpha()
fond_carte_ia = pygame.image.load(os.path.join(img_folder, 'cardrouge.png')).convert_alpha()
fond_fenetre = pygame.image.load(os.path.join(img_folder, 'board-mat.jpg')).convert()
spinner = pygame.image.load(os.path.join(img_folder, 'spinner.png')).convert_alpha()

# Redimensionner les images des cartes et du spinner
fond_carte_joueur = pygame.transform.scale(fond_carte_joueur, (100, 100))
fond_carte_ia = pygame.transform.scale(fond_carte_ia, (100, 100))
spinner = pygame.transform.scale(spinner, (50, 50))

class Card:
    def __init__(self, name, attribute, numbers, image, background):
        self.name = name
        self.attribute = attribute
        self.numbers = numbers
        self.image_path = os.path.join(img_folder, image)
        self.background_path = os.path.join(img_folder, background)
        if os.path.exists(self.image_path):
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.image, (100, 100))
            self.image = self.original_image
            self.background = pygame.image.load(self.background_path).convert_alpha()
            self.original_background = pygame.transform.scale(self.background, (100, 100))
            self.background = self.original_background
            self.draw_numbers()
        else:
            raise FileNotFoundError(f"No file '{self.image_path}' found in working directory")

    def draw_numbers(self):
        if int(self.name) >= 18:
            positions = [(50, 5), (5, 50), (50, 85), (85, 50)]
            for number, pos in zip(self.numbers, positions):
                text = font.render(str(number), True, (255, 255, 255))
                self.image.blit(text, pos)

    def resize_for_cell(self, width, height):
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.background = pygame.transform.scale(self.original_background, (width, height))

class GameLogic:
    def __init__(self, player_cards, ai_player, difficulty="easy"): #Add the difficulty parameter
        self.player_cards = player_cards
        self.ai_player = ai_player
        self.game_board = [None] * 9
        self.current_turn = "player"
        self.ai_timer = None
        self.difficulty = difficulty

    def start_game(self):
        self.next_turn()

    def next_turn(self):
        if self.current_turn == "player":
            self.current_turn = "ai"
            self.ai_timer = time.time()
        else:
            self.current_turn = "player"
            self.ai_timer = None

    def player_move(self, position, card):
        if self.current_turn == "player" and self.game_board[position] is None:
            card.resize_for_cell(150, 150)
            self.game_board[position] = card
            self.player_cards.remove(card)
            self.next_turn()

    def ai_move(self):
        if self.current_turn == "ai" and self.ai_timer and time.time() - self.ai_timer >= 5:
            position, card = self.ai_player.play_card(self)
            if position is not None and card is not None:
                self.next_turn()
                return position, card
        return None, None

def dessiner_plateau(fenetre):
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i in range(1, 3):
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x + 150 * i, plateau_y), (plateau_x + 150 * i, plateau_y + 3 * 150), 2)
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x, plateau_y + 150 * i), (plateau_x + 3 * 150, plateau_y + 150 * i), 2)

def dessiner_cartes(fenetre, cartes_joueur, cartes_ia, start_time):
    elapsed_time = time.time() - start_time
    delay = 0.5
    for i, carte in enumerate(cartes_joueur):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            fenetre.blit(fond_carte_joueur, (50, y_pos))
            fenetre.blit(carte.image, (50, y_pos))
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            fenetre.blit(fond_carte_ia, (LARGEUR_FENETRE - 150, y_pos))
            fenetre.blit(carte.image, (LARGEUR_FENETRE - 150, y_pos))

def dessiner_jeu(fenetre, game_logic, selected_card=None, mouse_pos=None, start_time=None):
    fenetre.blit(fond_fenetre, (0, 0))
    dessiner_plateau(fenetre)
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i, card in enumerate(game_logic.game_board):
        if card is not None:
            x = plateau_x + (i % 3) * 150
            y = plateau_y + (i // 3) * 150
            fenetre.blit(card.background, (x, y))
            fenetre.blit(card.image, (x, y))
    dessiner_cartes(fenetre, game_logic.player_cards, game_logic.ai_player.hand, start_time)
    if game_logic.current_turn == "player":
        spinner_x = 50
    else:
        spinner_x = LARGEUR_FENETRE - 150
    spinner_y = plateau_y - spinner.get_height() - 10
    fenetre.blit(spinner, (spinner_x, spinner_y))
    if selected_card and mouse_pos:
        offset_x, offset_y = 5, 5
        fenetre.blit(selected_card.background, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
        fenetre.blit(selected_card.image, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
    pygame.display.flip()
