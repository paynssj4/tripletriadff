import pygame
import json
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time
from ai_logic import AIPlayer
from card import Card
from gamelogic import GameLogic
from drawing import dessiner_plateau, dessiner_cartes, dessiner_jeu, load_images
from capture_manager import CaptureManager
from utils import draw_text_with_outline, afficher_message_fin  # the import must be like this
from rules import BaseRule, ComboRule, IdentiqueRule, PlusRule

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('D:/test jeux tt/Nouveau dossier/fichier ancien/bgm.mp3')
pygame.mixer.music.play(-1)

capture_sound = pygame.mixer.Sound('D:/test jeux tt/Nouveau dossier/fichier ancien/sound-turn.wav')

LARGEUR_FENETRE = 950
HAUTEUR_FENETRE = 554
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Triple Triad")

load_images()  # Charger les images après l'initialisation de Pygame

with open('D:/test jeux tt/Nouveau dossier/fichier ancien/selected_cards.json', 'r') as f:
    selected_cards_data = json.load(f)
with open('D:/test jeux tt/Nouveau dossier/fichier ancien/cards.json', 'r') as f:
    all_cards_data = json.load(f)

img_folder = 'D:/test jeux tt/Nouveau dossier/fichier ancien/Img'

fond_fenetre = pygame.image.load(os.path.join(img_folder, 'board-mat.jpg')).convert()
fond_carte_joueur = pygame.image.load(os.path.join(img_folder, 'cardbleu.png')).convert_alpha()
fond_carte_ia = pygame.image.load(os.path.join(img_folder, 'cardrouge.png')).convert_alpha()
spinner = pygame.image.load(os.path.join(img_folder, 'spinner.png')).convert_alpha()

fond_carte_joueur = pygame.transform.scale(fond_carte_joueur, (100, 100))
fond_carte_ia = pygame.transform.scale(fond_carte_ia, (100, 100))
spinner = pygame.transform.scale(spinner, (50, 50))

def choisir_regle():
    """Affiche une interface pour choisir la règle du jeu."""
    font = pygame.font.SysFont(None, 48)
    base_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2 - 100, 300, 50)
    identique_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2, 300, 50)
    plus_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2 + 100, 300, 50)
    aleatoire_combo_rect = pygame.Rect(LARGEUR_FENETRE // 2 - 150, HAUTEUR_FENETRE // 2 + 200, 300, 50)

    while True:
        fenetre.fill((0, 0, 0))
        text = font.render("Choisissez une règle:", True, (255, 255, 255))
        text_rect = text.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2 - 150))
        fenetre.blit(text, text_rect)

        pygame.draw.rect(fenetre, (50, 50, 50), base_rect)
        pygame.draw.rect(fenetre, (50, 50, 50), identique_rect)
        pygame.draw.rect(fenetre, (50, 50, 50), plus_rect)
        pygame.draw.rect(fenetre, (50, 50, 50), aleatoire_combo_rect)

        base_text = font.render("Base", True, (255, 255, 255))
        identique_text = font.render("Identique", True, (255, 255, 255))
        plus_text = font.render("Plus", True, (255, 255, 255))
        aleatoire_combo_text = font.render("Aléatoire + Combo", True, (255, 255, 255))

        fenetre.blit(base_text, (base_rect.x + 75, base_rect.y + 10))
        fenetre.blit(identique_text, (identique_rect.x + 50, identique_rect.y + 10))
        fenetre.blit(plus_text, (plus_rect.x + 75, plus_rect.y + 10))
        fenetre.blit(aleatoire_combo_text, (aleatoire_combo_rect.x + 10, aleatoire_combo_rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None  # Ajouter pour arrêter le jeu si l'on ferme la fenêtre.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if base_rect.collidepoint(x, y):
                    return "base"
                elif identique_rect.collidepoint(x, y):
                    return "identique"
                elif plus_rect.collidepoint(x, y):
                    return "plus"
                elif aleatoire_combo_rect.collidepoint(x, y):
                    return "aleatoire_combo"

def afficher_regle_choisie(fenetre, regle):
    # ... (Your afficher_regle_choisie function - no changes needed)
    pass

def select_random_cards():
    """Sélectionne aléatoirement des cartes avec des chiffres <= 6."""
    valid_cards = [card for card in all_cards_data if all(num <= 6 for num in card['numbers'])]
    if len(valid_cards) < 5:
        print(f"Erreur: pas assez de carte pour selectionné les cartes des joueurs. taille de la liste: {len(valid_cards)}")
        return []  # On retourne une liste vide s'il n'y a pas assez de cartes
    else:
        return random.sample(valid_cards, 5)

def select_random_ai_cards(all_cards_data):
    """Sélectionne aléatoirement 5 cartes pour l'IA avec des chiffres <= 6."""
    valid_cards = [card for card in all_cards_data if all(num <= 6 for num in card['numbers'])]
    if len(valid_cards) < 5:
        print(f"Erreur: pas assez de carte pour selectionné les cartes de l'ia. taille de la liste: {len(valid_cards)}")
        return []  # On retourne une liste vide s'il n'y a pas assez de cartes
    else:
        return random.sample(valid_cards, 5)

def update_score_display(fenetre, player_wins, ai_wins, LARGEUR_FENETRE, HAUTEUR_FENETRE):
    """Met à jour l'affichage du score des parties gagnées."""
    font = pygame.font.SysFont(None, 36)  # On instancie la police.
    score_text = font.render(f"Parties gagnées - Joueur: {player_wins} | IA: {ai_wins}", True, (255, 255, 255))

    # Calcul de la position pour centrer horizontalement et placer en bas de l'écran
    text_x = LARGEUR_FENETRE // 2 - score_text.get_width() // 2
    text_y = HAUTEUR_FENETRE - 40 

    # Effacer l'ancienne zone de texte en dessinant un rectangle noir.
    pygame.draw.rect(fenetre, (0, 0, 0), (text_x, text_y, score_text.get_width(), score_text.get_height()))  # On efface l'ancienne ligne
    
    # On affiche le nouveau texte
    fenetre.blit(score_text, (text_x, text_y))
    # Note: remove pygame.display.flip from here! we will call it later
    # pygame.display.flip()

def main(regle_initiale=None, player_wins=0, ai_wins=0):
    """Fonction principale du jeu."""
    # ... (Rest of your main function until the game loop is the same)
    if regle_initiale is None:
        regle = choisir_regle()
        if not regle:
            return False
        afficher_regle_choisie(fenetre, regle)
    else:
        regle = regle_initiale
        afficher_regle_choisie(fenetre, regle)

    if regle in ["aleatoire_combo", "plus", "identique"]:
        player_cards_data = select_random_cards()
    else:
        player_cards_data = selected_cards_data  # Utiliser les cartes sélectionnées dans l'inventaire

    player_cards = [Card(
        name=card_data['name'],
        attribute=card_data['attribute'],
        numbers=card_data['numbers'],
        background='cardbleu.png',
        img_path=card_data.get('img_path', '')
    ) for card_data in player_cards_data]
    
    ai_cards_data = select_random_ai_cards(all_cards_data)
    ai_deck = [Card(
        name=card_data['name'],
        attribute=card_data['attribute'],
        numbers=card_data['numbers'],
        background='cardrouge.png',
        img_path=card_data.get('img_path', '')
    ) for card_data in ai_cards_data]
    ai_player = AIPlayer(ai_deck)
    game_logic = GameLogic(player_cards, ai_player, regle)
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
    
    message = ""  # Variable ajoutée ici afin qu'elle existe en dehors de la boucle.
    # Afficher le score initial
    font = pygame.font.SysFont(None, 36)
    update_score_display(fenetre, player_wins, ai_wins, LARGEUR_FENETRE, HAUTEUR_FENETRE)  # On affiche le score initial
    last_player_wins = -1  # Initialiser à une valeur différente pour forcer le premier affichage
    last_ai_wins = -1
    
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
    selected_card_offset = (0,0)

    while running and not game_logic.check_game_over():
        mouse_pos = pygame.mouse.get_pos()
        if game_logic.current_turn == "ai" and not ia_play:
            # Correction ici, on doit envoyer les arguments attendus par ai_move
            position, card = game_logic.ai_move(fenetre, dessiner_jeu, capture_sound) 
            if position is not None and card is not None:
                print(f"AI placed {card.name} at position {position}")
                ia_play = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and game_logic.current_turn == "player":
                x, y = event.pos
                # Sélection de la carte
                if game_logic.selected_card is None:
                    for i, card in enumerate(player_cards):
                        card_rect = pygame.Rect(50, 50 + i * 80, 100, 100)
                        if card_rect.collidepoint(x, y):
                            game_logic.selected_card_index = i
                            game_logic.selected_card = card
                            card.selected = True  # Marquer la carte comme sélectionnée

                            # Calcul de l'offset pour centrer la carte sur la souris
                            selected_card_offset = (x - card.x, y - card.y)
                            break

                else:
                    # Placement de la carte
                    card_redeposited = False
                    for cell_name, coords in cell_coords.items():
                        cell_rect = pygame.Rect(
                            int(coords["x"] * scale_x),
                            int(coords["y"] * scale_y),
                            int(coords["width"] * scale_x),
                            int(coords["height"] * scale_y)
                        )
                        if cell_rect.collidepoint(event.pos):
                            if game_logic.selected_card_index is not None and len(player_cards) > game_logic.selected_card_index and game_logic.selected_card == player_cards[game_logic.selected_card_index]:
                                game_logic.player_move(list(cell_coords.keys()).index(cell_name), game_logic.selected_card, fenetre, dessiner_jeu, capture_sound)
                            game_logic.selected_card_index = None
                            game_logic.selected_card.selected = False  # Réinitialiser l'état de sélection
                            game_logic.selected_card = None
                            ia_play = False
                            card_redeposited = True
                            selected_card_offset = (0,0)
                            break

                    # Redéposer la carte à son emplacement d'origine si elle n'a pas été placée sur le plateau
                    if not card_redeposited:
                        game_logic.selected_card.x = 50
                        game_logic.selected_card.y = 50 + game_logic.selected_card_index * 80
                        game_logic.selected_card_index = None
                        game_logic.selected_card.selected = False
                        game_logic.selected_card = None
                        selected_card_offset = (0,0)

            elif event.type == pygame.MOUSEMOTION and game_logic.selected_card is not None:
                #si la carte est selectionnée on suit la position de la souris
                game_logic.selected_card.x = mouse_pos[0] - selected_card_offset[0]
                game_logic.selected_card.y = mouse_pos[1] - selected_card_offset[1]
                #limite le depassement de la carte
                game_logic.selected_card.x = max(0, min(game_logic.selected_card.x, LARGEUR_FENETRE - game_logic.selected_card.width))
                game_logic.selected_card.y = max(0, min(game_logic.selected_card.y, HAUTEUR_FENETRE - game_logic.selected_card.height))

        if game_logic.check_game_over():
            dessiner_jeu(fenetre, fond_fenetre, game_logic, LARGEUR_FENETRE, HAUTEUR_FENETRE, game_logic.selected_card, mouse_pos, start_time, player_cards)  # afficher une dernière fois les cartes
            # Afficher les chiffres sur les cartes sur le plateau

            # Afficher les chiffres sur les cartes sur le plateau
            for i, carte in enumerate(game_logic.game_board):
                if carte is not None:
                    carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
            
            # On met à jour le score une fois avant d'afficher le message de fin.
            if "Le joueur a gagné !" in message:
                message = game_logic.get_winner()  # On actualise la variable message
                player_wins += 1
            elif "L'IA a gagné !" in message:
                message = game_logic.get_winner()  # On actualise la variable message
                ai_wins += 1
            update_score_display(fenetre, player_wins, ai_wins, LARGEUR_FENETRE, HAUTEUR_FENETRE)
            pygame.display.flip()
            
            time.sleep(1)  # Ajouter un délai de 1 secondes
            message = game_logic.get_winner()

            # On affiche le nouveau score de parties gagnées
            
            # On affiche le message de fin
            choix = afficher_message_fin(fenetre, message, LARGEUR_FENETRE, HAUTEUR_FENETRE, replay_option=True, new_game_option=True)  # corrected line
            if choix == "nouvelle_partie":
                return main(player_wins=player_wins, ai_wins=ai_wins)
            elif choix == True:
                return main(regle_initiale=regle, player_wins=player_wins, ai_wins=ai_wins)  # On relance la même partie.
            elif choix == None or choix == False:
                return False  # On quitte le jeu.

        dessiner_jeu(fenetre, fond_fenetre, game_logic, LARGEUR_FENETRE, HAUTEUR_FENETRE, game_logic.selected_card, mouse_pos, start_time, player_cards)

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        if not main():
            break
    pygame.quit()
