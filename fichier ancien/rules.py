import pygame

class BaseRule:
    def __init__(self, game_logic):
        self.game_logic = game_logic

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

    def apply_rule(self, position, card, fenetre, dessiner_jeu, capture_sound):
        """Méthode par défaut pour appliquer une règle."""
        pass  # Ne rien faire par défaut

class ComboRule(BaseRule):
    def __init__(self, game_logic):
        super().__init__(game_logic)

    def apply_rule(self, position, card, fenetre, dessiner_jeu, capture_sound):
        """Applique la règle 'Combo' de manière itérative."""
        captures = []  # Liste pour stocker les captures.
        for pos, carte in self.game_logic.capture_manager.calculate_captures(position):
            captures.append((pos, carte))

        # Liste pour stocker les nouvelles captures
        new_captures = []
        # On parcourt chaque capture de base
        for pos, carte in captures:
            # On regarde toutes les cartes adjacentes pour faire l'application du combo
            for pos_temp, card_temp in self.game_logic.capture_manager.calculate_captures(pos):
                # On ajoute les cartes dans une nouvelle liste de capture.
                new_captures.append((pos_temp, card_temp))
            # On capture les nouvelles cartes
        if len(new_captures) > 0:
            self.game_logic.capture_adjacent_cards(list(new_captures), fenetre, dessiner_jeu, capture_sound, 'cardbleu.png' if self.game_logic.current_turn == "player" else 'cardrouge.png')
            self.game_logic.afficher_message_combo(fenetre, dessiner_jeu, pygame.image.load('D:/test jeux tt/Nouveau dossier/fichier ancien/Img/board-mat.jpg').convert())

class IdentiqueRule(BaseRule):
    def __init__(self, game_logic):
        super().__init__(game_logic)

    def apply_rule(self, position, card, fenetre, dessiner_jeu, capture_sound):
        """Applique la règle 'Identique'."""
        adjacent_positions = self.game_logic.get_adjacent_positions(position)
        captures = []  # Liste pour stocker les captures
        matching_pairs = 0

        for adj_pos in adjacent_positions:
            adj_card = self.game_logic.game_board[adj_pos]
            if adj_card:
                if adj_pos == position - 1 and card.numbers[1] == adj_card.numbers[3]:  # Gauche
                    matching_pairs += 1
                elif adj_pos == position + 1 and card.numbers[3] == adj_card.numbers[1]:  # Droite
                    matching_pairs += 1
                elif adj_pos == position - 3 and card.numbers[0] == adj_card.numbers[2]:  # Haut
                    matching_pairs += 1
                elif adj_pos == position + 3 and card.numbers[2] == adj_card.numbers[0]:  # Bas
                    matching_pairs += 1
                if matching_pairs >= 2:
                    captures.append((adj_pos, adj_card))

        # Capturer les cartes si au moins deux paires ont été trouvées
        if len(captures) >= 2:
            for adj_pos, adj_card in captures:
                # On appelle la fonction pour capturer la carte
                self.game_logic.capture_adjacent_cards([(adj_pos, adj_card)], fenetre, dessiner_jeu, capture_sound, 'cardbleu.png' if self.game_logic.current_turn == "player" else 'cardrouge.png')
            # Afficher le message identique
            self.game_logic.afficher_message_regle(fenetre, "Identique")

class PlusRule(BaseRule):
    def __init__(self, game_logic):
        super().__init__(game_logic)

    def apply_rule(self, position, card, fenetre, dessiner_jeu, capture_sound):
        """Applique la règle 'Plus'."""
        adjacent_positions = self.game_logic.get_adjacent_positions(position)
        captures = []
        sums = {}  # Dictionnaire pour stocker les sommes
        
        for adj_pos in adjacent_positions:
            adj_card = self.game_logic.game_board[adj_pos]
            if adj_card:
                if adj_pos == position - 1:  # Gauche
                    sums[adj_pos] = card.numbers[1] + adj_card.numbers[3]
                elif adj_pos == position + 1:  # Droite
                    sums[adj_pos] = card.numbers[3] + adj_card.numbers[1]
                elif adj_pos == position - 3:  # Haut
                    sums[adj_pos] = card.numbers[0] + adj_card.numbers[2]
                elif adj_pos == position + 3:  # Bas
                    sums[adj_pos] = card.numbers[2] + adj_card.numbers[0]
        
        # Vérifier si au moins deux paires adjacentes ont la même somme
        if len(sums) >= 2 and len(set(sums.values())) < len(sums.values()):
            sum_values = list(sums.values())
            for i in range(len(sum_values)):
                for j in range(i + 1, len(sum_values)):
                    if sum_values[i] == sum_values[j]:
                        captures.append((list(sums.keys())[i], self.game_logic.game_board[list(sums.keys())[i]]))
                        captures.append((list(sums.keys())[j], self.game_logic.game_board[list(sums.keys())[j]]))
        
        # Capturer les cartes si nécessaire
        if len(set(captures)) > 1:
            self.game_logic.afficher_message_regle(fenetre, "Plus")
            for pos, card in captures:
                self.game_logic.capture_adjacent_cards([(pos, card)], fenetre, dessiner_jeu, capture_sound, 'cardbleu.png' if self.game_logic.current_turn == "player" else 'cardrouge.png')

