import pygame

class CaptureManager:
    def __init__(self, game_logic):
        self.game_logic = game_logic

    def calculate_captures(self, position):
        """Calcule les cartes à capturer sans lancer d'animation."""
        card = self.game_logic.game_board[position]
        if card is None:
            return []  # Retourne une liste vide s'il n'y a pas de carte à cette position

        adjacent_positions = self.game_logic.get_adjacent_positions(position)
        captures = set()  # Utiliser un set pour stocker les valeurs uniques
        for adj_pos in adjacent_positions:
            adj_card = self.game_logic.game_board[adj_pos]
            if adj_card is not None and adj_card.background_path != card.background_path:
                if self.game_logic.rule.can_capture(card, adj_card, position, adj_pos):
                    captures.add((adj_pos, adj_card))  # Stocker la position et la carte capturable
        return list(captures)  # Transformer le set en liste à la fin

    def capture_adjacent_cards(self, captures, fenetre, dessiner_jeu, capture_sound, new_background_path):
        """Gère la capture des cartes adjacentes."""
        if not captures:
            return False  # Sortir si aucune capture

        capture_sound.play()
        new_captures = []  # on crée une liste afin de rajouter les nouvelles captures
        for adj_pos, adj_card in captures:  # on rajoute une boucle afin de parcourir les cartes.
            cell_x = (adj_pos % 3) * 150 + ((950 - 3 * 150) // 2)
            cell_y = (adj_pos // 3) * 150 + ((554 - 3 * 150) // 2)
            
            if self.game_logic.current_turn == "player":
                self.game_logic.animate_card_capture(adj_card, fenetre, cell_x, cell_y, dessiner_jeu, new_background_path)
            elif self.game_logic.current_turn == "ai":
                self.game_logic.animate_ai_card_capture(adj_card, fenetre, cell_x, cell_y, dessiner_jeu, new_background_path)
            self.game_logic.game_board[adj_pos].change_background(new_background_path)
            new_captures.extend(self.calculate_captures(adj_pos))  # on recalcule les nouvelles captures

        if len(new_captures) > 0:
            for adj_pos, adj_card in new_captures:
                self.capture_adjacent_cards([(adj_pos, adj_card)], fenetre, dessiner_jeu, capture_sound, new_background_path)
        
        if self.game_logic.regle == "aleatoire_combo":
            self.game_logic.rule.apply_rule(position=0, card=None, fenetre=fenetre, dessiner_jeu=dessiner_jeu, capture_sound=capture_sound)

        return True
