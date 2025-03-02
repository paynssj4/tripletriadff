import pygame
import json
import random
import os
import time
from ai_logic import AIPlayer
from card import Card
from gamelogic import GameLogic

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/bgm.mp3')
pygame.mixer.music.play(-1)

capture_sound = pygame.mixer.Sound('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/sound-turn.wav')

LARGEUR_FENETRE = 950
HAUTEUR_FENETRE = 554
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Triple Triad")

with open('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/selected_cards.json', 'r') as f:
    selected_cards_data = json.load(f)
with open('/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/cards.json', 'r') as f:
    all_cards_data = json.load(f)

img_folder = '/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/Img'

fond_fenetre = pygame.image.load(os.path.join(img_folder, 'board-mat.jpg')).convert()
fond_carte_joueur = pygame.image.load(os.path.join(img_folder, 'cardbleu.png')).convert_alpha()
fond_carte_ia = pygame.image.load(os.path.join(img_folder, 'cardrouge.png')).convert_alpha()
spinner = pygame.image.load(os.path.join(img_folder, 'spinner.png')).convert_alpha()

fond_carte_joueur = pygame.transform.scale(fond_carte_joueur, (100, 100))
fond_carte_ia = pygame.transform.scale(fond_carte_ia, (100, 100))
spinner = pygame.transform.scale(spinner, (50, 50))

def dessiner_plateau(fenetre):
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i in range(1, 3):
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x + 150 * i, plateau_y), (plateau_x + 150 * i, plateau_y + 3 * 150), 2)
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x, plateau_y + 150 * i), (plateau_x + 3 * 150, plateau_y + 150 * i), 2)

def dessiner_cartes(fenetre, cartes_joueur, cartes_ia, start_time, selected_card_index=None):
    elapsed_time = time.time() - start_time
    delay = 0.5
    #afficher les cartes du joueur
    for i, card in enumerate(cartes_joueur):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            card.resize_for_hand(100, 100)
            card.x = 50
            card.y = y_pos
            fenetre.blit(card.background, (card.x, card.y))  # Draw the background
            fenetre.blit(card.image, (card.x, card.y))  # Draw the image
            card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True)) # Draw the numbers

    #afficher les cartes de l'ia
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = HAUTEUR_FENETRE - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            carte.resize_for_hand(100, 100)
            carte.x = LARGEUR_FENETRE - 150
            carte.y = y_pos
            fenetre.blit(carte.background, (carte.x, carte.y))
            fenetre.blit(carte.image, (carte.x, carte.y))
            carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))

def dessiner_jeu(fenetre, game_logic, selected_card=None, mouse_pos=None, start_time=None, player_cards=None): #ajouter player_cards dans les parametre
    fenetre.blit(fond_fenetre, (0, 0))
    dessiner_plateau(fenetre)
    plateau_x = (LARGEUR_FENETRE - 3 * 150) // 2
    plateau_y = (HAUTEUR_FENETRE - 3 * 150) // 2
    for i, card in enumerate(game_logic.game_board):
        if card is not None:
            x = plateau_x + (i % 3) * 150
            y = plateau_y + (i // 3) * 150
            card.resize_for_cell(150, 150)
            card.x = x
            card.y = y
            fenetre.blit(card.background, (x, y))
            fenetre.blit(card.image, (x, y))
            card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))

    dessiner_cartes(fenetre, player_cards, game_logic.ai_player.hand, start_time, game_logic.selected_card_index) # remplacer game_logic.player_cards par player_cards
    if game_logic.current_turn == "player":
        spinner_x = 50
    else:
        spinner_x = LARGEUR_FENETRE - 150
    spinner_y = plateau_y - spinner.get_height() - 10
    fenetre.blit(spinner, (spinner_x, spinner_y))

    #vérification de selected_card pour afficher les chiffres
    if selected_card and mouse_pos:
        offset_x, offset_y = 5, 5
        fenetre.blit(selected_card.background, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
        fenetre.blit(selected_card.image, (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y))
        selected_card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
    pygame.display.flip()

def afficher_message_fin(fenetre, message):
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2 - 50))
    rejouer_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2 + 50, 140, 50)
    quitter_rect = pygame.Rect(LARGEUR_FENETRE // 2 + 10, HAUTEUR_FENETRE // 2 + 50, 140, 50)
    rejouer_text = font.render("Rejouer", True, (255, 255, 255))
    quitter_text = font.render("Quitter", True, (255, 255, 255))
    fenetre.blit(text, text_rect)
    pygame.draw.rect(fenetre, (50, 50, 50), rejouer_rect)
    pygame.draw.rect(fenetre, (50, 50, 50), quitter_rect)
    fenetre.blit(rejouer_text, (rejouer_rect.x + 10, rejouer_rect.y + 10))
    fenetre.blit(quitter_text, (quitter_rect.x + 10, quitter_rect.y + 10))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rejouer_rect.collidepoint(x, y):
                    return True
                elif quitter_rect.collidepoint(x, y):
                    pygame.quit()
                    return False

def main():
    player_cards = [Card(**card_data) for card_data in selected_cards_data]
    ai_deck = [Card(**card_data, background='cardrouge.png') for card_data in all_cards_data]
    ai_player = AIPlayer(ai_deck)
    game_logic = GameLogic(player_cards, ai_player)
    game_logic.start_game()
    start_time = time.time()
    running = True
    ia_play = False

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
    while running and not game_logic.check_game_over():
        mouse_pos = pygame.mouse.get_pos()
        if game_logic.current_turn == "ai" and not ia_play :
            position, card = game_logic.ai_move(fenetre, dessiner_plateau, capture_sound)
            if position is not None and card is not None:
                print(f"AI placed {card.name} at position {position}")
                ia_play = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and game_logic.current_turn == "player":
                x, y = event.pos
                # Selection de la carte
                for i, card in enumerate(player_cards):
                        card_rect = pygame.Rect(50, 50 + i * 80, 100, 100)
                        if card_rect.collidepoint(x, y):
                            game_logic.selected_card_index = i
                            game_logic.selected_card = card
                            break
                if game_logic.selected_card is not None :
                    # Placement de la carte
                    for cell_name, coords in cell_coords.items():
                        cell_rect = pygame.Rect(
                            int(coords["x"] * scale_x),
                            int(coords["y"] * scale_y),
                            int(coords["width"] * scale_x),
                            int(coords["height"] * scale_y)
                        )
                        if cell_rect.collidepoint(x, y):
                            if game_logic.selected_card_index is not None and len(player_cards) > game_logic.selected_card_index and game_logic.selected_card == player_cards[game_logic.selected_card_index]:
                                game_logic.player_move(list(cell_coords.keys()).index(cell_name), game_logic.selected_card, fenetre, dessiner_plateau, capture_sound)
                                
                            game_logic.selected_card_index = None
                            game_logic.selected_card = None
                            ia_play = False
                            break

        if game_logic.check_game_over():
            dessiner_jeu(fenetre, game_logic, game_logic.selected_card, mouse_pos, start_time, player_cards) # afficher une derniere fois les carte
            time.sleep(2)  # Ajouter un délai de 2 secondes
            message = game_logic.get_winner()
            if not afficher_message_fin(fenetre, message):
                return False
            else:
                return True

        if game_logic.selected_card is not None:
            game_logic.selected_card.resize_for_cell(100, 100)

        dessiner_jeu(fenetre, game_logic, game_logic.selected_card, mouse_pos, start_time, player_cards) # ajouter player_cards a la fonction

if __name__ == "__main__":
    while True:
        if not main():
            break
    pygame.quit()
