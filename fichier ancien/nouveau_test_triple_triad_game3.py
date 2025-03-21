import pygame
import json
import random
import os
import time
from ai_logic import AIPlayer  # Importer la classe AIPlayer
from card import Card  # Importer la classe Card

# Initialisation de Pygame
pygame.init()

# Charger la musique de fond
pygame.mixer.music.load('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/bgm.mp3')

# Charger les sons
capture_sound = pygame.mixer.Sound('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/sound-turn.wav')

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

# Police pour dessiner les nombres sur les cartes
font = pygame.font.SysFont(None, 24)

# --- Classes et fonctions ---









class GameLogic:
    def __init__(self, player_cards, ai_player):
        self.player_cards = player_cards
        self.ai_player = ai_player
        self.game_board = [None] * 9  # Initialiser le plateau avec 9 positions
        self.current_turn = random.choice(["player", "ai"])  # Choisir aléatoirement qui commence
        self.ai_timer = None  # Timer pour le délai de l'IA
        self.start_time = time.time()  # Temps de début pour le placement des cartes

    def start_game(self):
        pygame.mixer.music.play(-1)  # Lancer la musique en boucle
        if self.current_turn == "ai":
            self.ai_timer = time.time()  # Démarrer le timer pour l'IA
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
            self.capture_adjacent_cards(card, position, 'cardbleu.png')  # Capturer les cartes adjacentes
            self.next_turn()



    def get_adjacent_positions(self, position):
        adjacent_positions = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }
        return adjacent_positions[position]

    def can_capture(self, card, adj_card, position, adj_pos):
        if adj_pos == position - 1:  # Gauche
            return card.numbers[1] > adj_card.numbers[3]
        elif adj_pos == position + 1:  # Droite
            return card.numbers[3] > adj_card.numbers[1]
        elif adj_pos == position - 3:  # Haut
            return card.numbers[0] > adj_card.numbers[2]
        elif adj_pos == position + 3:  # Bas
            return card.numbers[2] > adj_card.numbers[0]
        return False

    def ai_move(self):
        if self.current_turn == "ai" and self.ai_timer and time.time() - self.ai_timer >= 5:
            position, card = self.ai_player.play_card(self)
            if position is not None and card is not None:
                self.capture_adjacent_cards(card, position, 'cardrouge.png')  # Capturer les cartes adjacentes
                self.next_turn()
                return position, card
        return None, None  # Retourner None si ce n'est pas le tour de l'IA



    def get_winner(self):
        player_score = sum(1 for card in self.game_board if card and card.background_path.endswith('cardbleu.png'))
        ai_score = sum(1 for card in self.game_board if card and card.background_path.endswith('cardrouge.png'))
        if player_score > ai_score:
            return "Vous avez gagné!"
        elif ai_score > player_score:
            return "Vous avez perdu!"
        else:
            return "Match nul!"

    def check_game_over(self):
        # Vérifie si toutes les cellules du plateau sont occupées
        return all(cell is not None for cell in self.game_board)


    def check_game_over(self):
        # Vérifie si toutes les cellules du plateau sont occupées
        return all(cell is not None for cell in self.game_board)

    def capture_adjacent_cards(self, card, position, new_background):
        adjacent_positions = self.get_adjacent_positions(position)
        for adj_pos in adjacent_positions:
            adj_card = self.game_board[adj_pos]
            if adj_card is not None and adj_card.background_path != new_background:
                if self.can_capture(card, adj_card, position, adj_pos):
                    # Mettre à jour la carte dans le plateau avant de lancer l'animation
                    adj_card.change_background(new_background)
                    self.game_board[adj_pos] = adj_card  # Mettre à jour la carte capturée
                    cell_x = (adj_pos % 3) * 150 + ((950 - 3 * 150) // 2) #950 = LARGEUR_FENETRE
                    cell_y = (adj_pos // 3) * 150 + ((554 - 3 * 150) // 2) #554 = HAUTEUR_FENETRE
                    adj_card.resize_for_cell(150, 150)  # Redimensionner la carte capturée
                    adj_card.rotate(fenetre, cell_x, cell_y, dessiner_plateau, self.game_board) # Lancer l'animation de rotation
                    capture_sound.play()  # Jouer le son de capture

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
            fenetre.blit(carte.background, (50, y_pos))  # Dessiner le fond de la carte
            fenetre.blit(carte.image, (50, y_pos))  # Dessiner l'image de la carte par-dessus
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)  # Limiter la position y pour qu'elle ne dépasse pas la position finale
            fenetre.blit(carte.background, (LARGEUR_FENETRE - 150, y_pos))  # Dessiner le fond de la carte
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
    

def afficher_message_fin(fenetre, message):
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2 - 50))  # Ajuster la position verticale

    # Créer les boutons
    rejouer_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2 + 50, 140, 50)
    quitter_rect = pygame.Rect(LARGEUR_FENETRE // 2 + 10, HAUTEUR_FENETRE // 2 + 50, 140, 50)
    rejouer_text = font.render("Rejouer", True, (255, 255, 255))
    quitter_text = font.render("Quitter", True, (255, 255, 255))

    # Afficher le texte et les boutons
    fenetre.blit(text, text_rect)
    pygame.draw.rect(fenetre, (50, 50, 50), rejouer_rect)
    pygame.draw.rect(fenetre, (50, 50, 50), quitter_rect)
    fenetre.blit(rejouer_text, (rejouer_rect.x + 10, rejouer_rect.y + 10))
    fenetre.blit(quitter_text, (quitter_rect.x + 10, quitter_rect.y + 10))


    # Boucle pour attendre un clic sur un bouton
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quitter le jeu
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rejouer_rect.collidepoint(x, y):
                    return True  # Rejouer
                elif quitter_rect.collidepoint(x, y):
                    return False  # Quitter le jeu




# Créer les cartes du joueur et de l'IA
player_cards = [Card(**card_data, background='cardbleu.png') for card_data in selected_cards_data]
ai_deck = [Card(**card_data, background='cardrouge.png') for card_data in all_cards_data]
ai_player = AIPlayer(ai_deck)

# Initialiser la logique du jeu
game_logic = GameLogic(player_cards, ai_player)
game_logic.start_game()  # Démarrer le jeu

# --- Boucle principale du jeu ---
# --- Boucle principale du jeu ---
def main():
    # Créer les cartes du joueur et de l'IA
    player_cards = [Card(**card_data, background='cardbleu.png') for card_data in selected_cards_data]
    ai_deck = [Card(**card_data, background='cardrouge.png') for card_data in all_cards_data]
    ai_player = AIPlayer(ai_deck)

    # Initialiser la logique du jeu
    game_logic = GameLogic(player_cards, ai_player)
    game_logic.start_game()  # Démarrer le jeu

    selected_card_index = None  # Variable pour savoir quelle carte le joueur a sélectionnée.
    start_time = time.time()
    running = True

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
    # Boucle du jeux
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quitter le jeu
            elif event.type == pygame.MOUSEBUTTONDOWN and game_logic.current_turn == "player":
                x, y = event.pos

                # Vérifier si le clic est sur une carte du joueur
                for i, card in enumerate(player_cards):
                    card_rect = pygame.Rect(50, 50 + i * 80, 100, 100)  # Chevauchement vertical
                    if card_rect.collidepoint(x, y):
                        selected_card_index = i
                        break

                # Vérifier si le clic est sur une cellule du plateau
                for cell_name, coords in cell_coords.items():
                    cell_rect = pygame.Rect(
                        int(coords["x"] * scale_x),
                        int(coords["y"] * scale_y),
                        int(coords["width"] * scale_x),
                        int(coords["height"] * scale_y)
                    )
                    if cell_rect.collidepoint(x, y) and selected_card_index is not None:
                        game_logic.player_move(list(cell_coords.keys()).index(cell_name), player_cards[selected_card_index])
                        selected_card_index = None
                        break

        if game_logic.current_turn == "ai" and time.time() - game_logic.start_time > 5:  # Vérifier si c'est le tour de l'IA après le délai
            position, card = game_logic.ai_move()
            if position is not None and card is not None:
                print(f"AI placed {card.name} at position {position}")

        if game_logic.check_game_over():
            message = game_logic.get_winner()
            if not afficher_message_fin(fenetre, message):
                return False # Quitter le jeux
            else:
                return True  # relancer le jeux

        selected_card = player_cards[selected_card_index] if selected_card_index is not None else None
        dessiner_jeu(fenetre, game_logic, selected_card, mouse_pos, start_time)
    pygame.display.flip()


# Appel de la fonction main pour lancer le jeu
if __name__ == "__main__":
    while True:
        if not main():
           break
    pygame.quit()


