import time
import random
import pygame
from capture_manager import CaptureManager
from rules import BaseRule, ComboRule

class GameLogic:
    def __init__(self, player_cards, ai_player, regle="base"):
        """
        Initialise la logique du jeu.
        """
        self.player_cards = player_cards
        self.ai_player = ai_player
        self.game_board = [None] * 9  # Plateau de jeu (9 cases)
        self.current_turn = random.choice(["player", "ai"])  # Choisir aléatoirement qui commence
        self.ai_timer = None  # Timer pour le délai de l'IA
        self.start_time = time.time()  # Temps de début pour le placement des cartes
        self.selected_card = None
        self.selected_card_index = None
        self.regle = regle
        self.capture_manager = CaptureManager(self)  # Créer une instance de CaptureManager
        self.set_rule(regle)  # Définir la règle

    def set_rule(self, regle):
        """Définit la règle du jeu."""
        if regle == "aleatoire_combo":
            self.rule = ComboRule(self)
        else:
            self.rule = BaseRule(self)

    def calculate_captures(self, position):
        """Calcule les cartes à capturer sans lancer d'animation."""
        return self.capture_manager.calculate_captures(position)

    def capture_adjacent_cards(self, captures, fenetre, dessiner_jeu, capture_sound, new_background_path):
        """Capture les cartes adjacentes."""
        return self.capture_manager.capture_adjacent_cards(captures, fenetre, dessiner_jeu, capture_sound, new_background_path)

    def start_game(self):
        """Démarre le jeu."""
        if self.current_turn == "ai":
            self.ai_timer = time.time()

    def next_turn(self):
        """Passe au tour suivant."""
        if self.current_turn == "player":
            self.current_turn = "ai"
            self.ai_timer = time.time()
        else:
            self.current_turn = "player"
            self.ai_timer = None

    def player_move(self, position, card, fenetre, dessiner_jeu, capture_sound):
        """Gère le mouvement du joueur."""
        if self.current_turn == "player" and self.game_board[position] is None:
            card.resize_for_cell(150, 150)
            self.game_board[position] = card
            self.player_cards.remove(card)
            # Charger l'image du fond
            fond_fenetre = pygame.image.load('D:/test jeux tt/Nouveau dossier/fichier ancien/Img/board-mat.jpg').convert()
            dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)
            pygame.display.flip()
            pygame.time.delay(500)  # Attendre un moment avant de lancer l'animation de capture
            initial_captures = self.calculate_captures(position)  # Calcule les captures
            self.capture_adjacent_cards(initial_captures, fenetre, dessiner_jeu, capture_sound, 'cardbleu.png')  # Animation des captures

            if self.regle == "aleatoire_combo":
                self.rule.apply_rule(position, card, fenetre, dessiner_jeu, capture_sound)
            self.next_turn()

    def get_adjacent_positions(self, position):
        """Retourne les positions adjacentes à une position donnée sur le plateau."""
        adjacent_positions = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }
        return adjacent_positions[position]

    def animate_card_capture(self, adj_card, fenetre, cell_x, cell_y, dessiner_jeu, new_background_path):
        """Anime la capture d'une carte avec une rotation et changement de couleur."""
        card_back_path = 'D:/test jeux tt/Nouveau dossier/fichier ancien/Img/card-back.png'
        card_back = pygame.image.load(card_back_path).convert_alpha()
        card_back = pygame.transform.scale(card_back, (150, 150))  # Redimensionner l'image du dos de carte
        fond_fenetre = pygame.image.load('D:/test jeux tt/Nouveau dossier/fichier ancien/Img/board-mat.jpg').convert()
        dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)

        # Animation de rotation du dos de la carte
        for angle in range(0, 91, 10):
            rotated_image = pygame.transform.rotate(card_back, angle)
            rotated_rect = rotated_image.get_rect(center=(cell_x + 75, cell_y + 75))
            fenetre.blit(rotated_image, rotated_rect.topleft)
            pygame.display.flip()
            pygame.time.delay(30)  # Animation fluide

        # Afficher le dos de la carte
        fenetre.blit(card_back, (cell_x, cell_y))
        pygame.display.flip()
        pygame.time.delay(200)  # Pause avant de continuer la rotation
        
        adj_card.change_background(new_background_path)
        adj_card.resize_for_cell(150, 150)
        dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)
        fenetre.blit(adj_card.background, (cell_x, cell_y))
        fenetre.blit(adj_card.image, (cell_x, cell_y))
        adj_card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True, italic=True))
        pygame.display.flip()

    def animate_ai_card_capture(self, adj_card, fenetre, cell_x, cell_y, dessiner_jeu, new_background_path):
        """Anime la capture d'une carte par l'IA avec une rotation et changement de couleur."""
        card_back_path = 'D:/test jeux tt/Nouveau dossier/fichier ancien/Img/card-back.png'
        card_back = pygame.image.load(card_back_path).convert_alpha()
        card_back = pygame.transform.scale(card_back, (150, 150))  # Redimensionner l'image du dos de carte
        fond_fenetre = pygame.image.load('D:/test jeux tt/Nouveau dossier/fichier ancien/Img/board-mat.jpg').convert()

        dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)
        # Animation de rotation
        for angle in range(0, 91, 10):
            rotated_image = pygame.transform.rotate(card_back, angle)
            rotated_rect = rotated_image.get_rect(center=(cell_x + 75, cell_y + 75))
            fenetre.blit(rotated_image, rotated_rect.topleft)
            pygame.display.flip()
            pygame.time.delay(30)  # Animation fluide

         # Afficher le dos de la carte
        fenetre.blit(card_back, (cell_x, cell_y))
        pygame.display.flip()
        pygame.time.delay(200)  # Pause avant de continuer la rotation

        adj_card.change_background(new_background_path)
        adj_card.resize_for_cell(150, 150)
        dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)
        fenetre.blit(adj_card.background, (cell_x, cell_y))
        fenetre.blit(adj_card.image, (cell_x, cell_y))
        adj_card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True, italic=True))
        pygame.display.flip()

    def ai_move(self, fenetre, dessiner_jeu, capture_sound):
        """Gère le mouvement de l'IA avec animation."""
        if self.current_turn == "ai":
            if self.ai_timer is None:
                self.ai_timer = time.time()
            elif time.time() - self.ai_timer >= 1:  # Délai d'une seconde pour faire réfléchir l'IA
                position, card = self.ai_player.play_card(self, fenetre, dessiner_jeu, capture_sound)
                if position is not None and card is not None:
                    # Placer la carte directement sur le plateau
                    card.resize_for_cell(150, 150)
                    card.x = (position % 3) * 150 + ((950 - 3 * 150) // 2)
                    card.y = (position // 3) * 150 + ((554 - 3 * 150) // 2)
                    self.game_board[position] = card
                    self.ai_player.hand.remove(card)
                    # Charger l'image du fond
                    fond_fenetre = pygame.image.load('D:/test jeux tt/Nouveau dossier/fichier ancien/Img/board-mat.jpg').convert()
                    # Dessiner la carte avec les chiffres avant de lancer les captures.
                    dessiner_jeu(fenetre, fond_fenetre, self, 950, 554, None, None, self.start_time, self.player_cards)
                    card.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
                    pygame.display.flip()
                    initial_captures = self.calculate_captures(position)
                    self.capture_adjacent_cards(initial_captures, fenetre, dessiner_jeu, capture_sound, 'cardrouge.png')

                    if self.regle == "aleatoire_combo":
                        self.rule.apply_rule(position, card, fenetre, dessiner_jeu, capture_sound)
                    self.next_turn()
                    return position, card
        return None, None

    def place_card(self, card, cell_index, fenetre, dessiner_jeu, capture_sound, player_cards):
        """Place une carte sur le plateau de jeu."""
        if 0 <= cell_index < 9 and self.game_board[cell_index] is None:
            if self.current_turn == "player":
                card.owner = "player"
                player_cards.remove(card) #on retire la carte de la main du joueur
            elif self.current_turn == "ai":
                card.owner = "ai"
                self.ai_player.hand.remove(card)
            self.game_board[cell_index] = card

            #pas besoin de calculer ou de lancer les captures ici, car c'est géré par player_move et ai_move
           
        else:
            print("Erreur : La carte ne peut pas être placée ici.")

    def switch_turn(self):
        """Change le tour du joueur actuel."""
        if self.current_turn == "player":
            self.current_turn = "ai"
        else:
            self.current_turn = "player"

    def check_game_over(self):
        """Vérifie si le jeu est terminé (toutes les cases sont remplies)."""
        return all(cell is not None for cell in self.game_board)

    def get_winner(self):
        """Détermine le gagnant à la fin du jeu."""
        player_score = 0
        ai_score = 0
        for cell in self.game_board:
            if cell is not None:
                if cell.background_path == "cardbleu.png":
                    player_score += 1
                elif cell.background_path == "cardrouge.png":
                    ai_score += 1
        if player_score > ai_score:
            return "Le joueur a gagné !"
        elif ai_score > player_score:
            return "L'IA a gagné !"
        else:
            return "Match nul !"

    def afficher_message_combo(self, fenetre, dessiner_jeu, fond_fenetre):
        font = pygame.font.SysFont(None, 72, bold=True, italic=True)
        text = font.render("Combo", True, (128, 128, 128))  # Gris métallique
        text_rect = text.get_rect(center=(fenetre.get_width() // 2, fenetre.get_height() // 2))

        # Effet cel shading (contour noir)
        outline_font = pygame.font.SysFont(None, 72, bold=True, italic=True)
        outline_color = (0, 0, 0)
        
        # Dessiner les contours
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                outline_text = outline_font.render("Combo", True, outline_color)
                fenetre.blit(outline_text, (text_rect.x + dx, text_rect.y + dy))
         # Dessiner le contour noir avec une épaisseur
        outline_text = outline_font.render("Combo", True, outline_color)
        fenetre.blit(outline_text, (text_rect.x - 1, text_rect.y))
        fenetre.blit(outline_text, (text_rect.x + 1, text_rect.y))
        fenetre.blit(outline_text, (text_rect.x, text_rect.y - 1))
        fenetre.blit(outline_text, (text_rect.x, text_rect.y + 1))
        # Dessiner le texte principal
        fenetre.blit(text, text_rect)

        pygame.display.flip()
        pygame.time.delay(1000)  # On affiche pendant 1 seconde.
