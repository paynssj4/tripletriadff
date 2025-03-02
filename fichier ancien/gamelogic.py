import time
import random
import pygame

class GameLogic:
    def __init__(self, player_cards, ai_player):
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

    def start_game(self):
        """Démarre le jeu."""
        if self.current_turn == "ai":
            self.ai_timer = time.time()
        self.next_turn()

    def next_turn(self):
        """Passe au tour suivant."""
        if self.current_turn == "player":
            self.current_turn = "ai"
            self.ai_timer = time.time()
        else:
            self.current_turn = "player"
            self.ai_timer = None

    def player_move(self, position, card, fenetre, dessiner_plateau, capture_sound):
        """Gère le mouvement du joueur."""
        if self.current_turn == "player" and self.game_board[position] is None:
            card.resize_for_cell(150, 150)
            self.game_board[position] = card
            self.player_cards.remove(card)
            self.capture_adjacent_cards(position, fenetre, dessiner_plateau, capture_sound)
            self.next_turn()

    def get_adjacent_positions(self, position):
        """Retourne les positions adjacentes à une position donnée sur le plateau."""
        adjacent_positions = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }
        return adjacent_positions[position]

    def can_capture(self, card, adj_card, position, adj_pos):
        """Vérifie si une carte peut capturer une carte adjacente."""
        if adj_card.background_path == card.background_path:
            return False

        if adj_pos == position - 1:
            return card.numbers[1] > adj_card.numbers[3]
        elif adj_pos == position + 1:
            return card.numbers[3] > adj_card.numbers[1]
        elif adj_pos == position - 3:
            return card.numbers[0] > adj_card.numbers[2]
        elif adj_pos == position + 3:
            return card.numbers[2] > adj_card.numbers[0]
        return False

    def capture_adjacent_cards(self, position, fenetre, dessiner_plateau, capture_sound):
        """Capture les cartes adjacentes avec animation de rotation et de changement de couleur en même temps."""
        card = self.game_board[position]
        if card is None:
            return

        adjacent_positions = self.get_adjacent_positions(position)
        for adj_pos in adjacent_positions:
            adj_card = self.game_board[adj_pos]
            if adj_card is not None and adj_card.background_path != card.background_path:
                if self.can_capture(card, adj_card, position, adj_pos):
                    cell_x = (adj_pos % 3) * 150 + ((950 - 3 * 150) // 2)
                    cell_y = (adj_pos // 3) * 150 + ((554 - 3 * 150) // 2)
                    
                    # Lancer la rotation en parallèle au changement de couleur
                    for angle in range(0, 181, 10):
                        rotated_image = pygame.transform.rotate(adj_card.image, angle)
                        rotated_rect = rotated_image.get_rect(center=(cell_x + 75, cell_y + 75))
                        rotated_background = pygame.transform.rotate(adj_card.background, angle)
                        rotated_background_rect = rotated_background.get_rect(center=(cell_x + 75, cell_y + 75))
                        
                        dessiner_plateau(fenetre)
                        fenetre.blit(rotated_background, rotated_background_rect.topleft)
                        fenetre.blit(rotated_image, rotated_rect.topleft)
                        pygame.display.flip()
                        pygame.time.delay(30)  # Animation fluide
                    
                    # Changement de couleur après l'animation
                    adj_card.change_background(card.background_path)
                    adj_card.resize_for_cell(150, 150)
                    
                    # Mise à jour finale
                    dessiner_plateau(fenetre)
                    pygame.display.flip()
                    capture_sound.play()

    def ai_move(self, fenetre, dessiner_plateau, capture_sound):
        """Gère le mouvement de l'IA avec animation correcte."""
        if self.current_turn == "ai" and self.ai_timer and time.time() - self.ai_timer >= 5:
            position, card = self.ai_player.play_card(self)
            if position is not None and card is not None:
                card.resize_for_cell(150, 150)
                self.game_board[position] = card
                dessiner_plateau(fenetre)
                pygame.display.flip()
                pygame.time.delay(500)
                
                # Capture avec animation visible
                self.capture_adjacent_cards(position, fenetre, dessiner_plateau, capture_sound)
                
                self.next_turn()
                return position, card
        return None, None

    def get_winner(self):
        """Détermine le vainqueur de la partie."""
        player_score = sum(1 for card in self.game_board if card and card.background_path == 'cardbleu.png')
        ai_score = sum(1 for card in self.game_board if card and card.background_path == 'cardrouge.png')
        if player_score > ai_score:
            return "Vous avez gagné!"
        elif ai_score > player_score:
            return "Vous avez perdu!"
        else:
            return "Match nul!"

    def check_game_over(self):
        """Vérifie si la partie est terminée."""
        return all(cell is not None for cell in self.game_board)