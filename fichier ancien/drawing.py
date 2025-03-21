import pygame
import time

spinner = None
card_back = None

def load_images():
    global spinner, card_back
    spinner_path = 'D:/test jeux tt/Nouveau dossier/fichier ancien/Img/spinner.png'
    card_back_path = 'D:/test jeux tt/Nouveau dossier/fichier ancien/Img/card-back.png'
    spinner = pygame.image.load(spinner_path).convert_alpha()
    spinner = pygame.transform.scale(spinner, (35, 35))  # Redimensionner l'image du spinner à 35x35
    card_back = pygame.image.load(card_back_path).convert_alpha()

def dessiner_plateau(fenetre, largeur_fenetre, hauteur_fenetre):
    plateau_x = (largeur_fenetre - 3 * 150) // 2
    plateau_y = (hauteur_fenetre - 3 * 150) // 2
    for i in range(1, 3):
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x + 150 * i, plateau_y), (plateau_x + 150 * i, plateau_y + 3 * 150), 2)
        pygame.draw.line(fenetre, (0, 0, 0), (plateau_x, plateau_y + 150 * i), (plateau_x + 3 * 150, plateau_y + 150 * i), 2)

def dessiner_cartes(fenetre, cartes_joueur, cartes_ia, start_time, largeur_fenetre, hauteur_fenetre, selected_card_index=None, mouse_pos=None):
    elapsed_time = time.time() - start_time
    delay = 0.5
    # Afficher les cartes du joueur
    for i, card in enumerate(cartes_joueur):
        if elapsed_time > i * delay:
            if selected_card_index is not None and i == selected_card_index:
                continue  # Ne pas dessiner la carte sélectionnée dans la colonne en main
            y_pos = hauteur_fenetre - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            card.resize_for_hand(100, 100)
            card.x = 50
            card.y = y_pos

            # Vérifier si la souris survole la carte
            if mouse_pos and pygame.Rect(card.x, card.y, 100, 100).collidepoint(mouse_pos):
                card.y -= 20  # Lever légèrement la carte

            fenetre.blit(card.background, (card.x, card.y))  # Dessiner le fond
            fenetre.blit(card.image, (card.x, card.y))  # Dessiner l'image
            card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))  # Dessiner les chiffres

    # Afficher les cartes de l'IA
    for i, carte in enumerate(cartes_ia):
        if elapsed_time > i * delay:
            y_pos = hauteur_fenetre - 100 - i * 80 - (elapsed_time - i * delay) * 200
            y_pos = max(y_pos, 50 + i * 80)
            carte.resize_for_hand(100, 100)
            carte.x = largeur_fenetre - 150
            carte.y = y_pos
            fenetre.blit(carte.background, (carte.x, carte.y))
            fenetre.blit(carte.image, (carte.x, carte.y))
            carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))

def dessiner_jeu(fenetre, fond_fenetre, game_logic, largeur_fenetre, hauteur_fenetre, selected_card=None, mouse_pos=None, start_time=None, player_cards=None):
    fenetre.blit(fond_fenetre, (0, 0))
    dessiner_plateau(fenetre, largeur_fenetre, hauteur_fenetre)
    plateau_x = (largeur_fenetre - 3 * 150) // 2
    plateau_y = (hauteur_fenetre - 3 * 150) // 2
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

    dessiner_cartes(fenetre, player_cards, game_logic.ai_player.hand, start_time, largeur_fenetre, hauteur_fenetre, game_logic.selected_card_index, mouse_pos)

    if game_logic.current_turn == "player":
        spinner_x = 50
    else:
        spinner_x = largeur_fenetre - 150
    spinner_y = plateau_y - spinner.get_height() - 10
    fenetre.blit(spinner, (spinner_x, spinner_y))

    # Vérification de selected_card pour afficher les chiffres
    if selected_card and mouse_pos:
        # Calcul du centre de la carte
        card_center_x = mouse_pos[0]
        card_center_y = mouse_pos[1]

        # Dessin du fond et de l'image de la carte
        offset_x, offset_y = selected_card.width // 2, selected_card.height // 2
        fenetre.blit(selected_card.background, (card_center_x - offset_x, card_center_y - offset_y))
        fenetre.blit(selected_card.image, (card_center_x - offset_x, card_center_y - offset_y))
        #on appelle draw_number et on envoie en parametre les coordonnées du centre
        selected_card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True), card_center_x, card_center_y)

    pygame.display.flip()
