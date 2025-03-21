import pygame
import os
import logging

# Définir les dimensions de la fenêtre
LARGEUR_FENETRE = 950  # Ajuster si nécessaire
HAUTEUR_FENETRE = 554  # Ajuster si nécessaire

# Définir le dossier où les images sont stockées
img_folder = "D:/test jeux tt/Nouveau dossier/fichier ancien/Img"  # Ajuster ce chemin si nécessaire

class Card:
    def __init__(self, name, attribute, numbers, background, img_path=None):
        self.name = name
        self.attribute = attribute
        self.numbers = numbers
        self.element = ""  # Attribut par défaut
        self.background_path = background
        self.img_path = img_path.replace('\\', '/') if img_path else None  # Corriger les chemins d'accès
        if self.img_path:
            self.image = self.load_image(self.img_path)
        else:
            self.image = None
        self.background = self.load_image(self.background_path)
        self.x = 0
        self.y = 0
        self.selected = False  # Ajout de l'attribut selected
        self.width = 150  # Largeur par défaut
        self.height = 150  # Hauteur par défaut

    def load_image(self, image_path):
        """Charge une image et gère les erreurs."""
        if not image_path:
            return None
        full_path = os.path.join(img_folder, image_path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            return image
        except pygame.error as e:
            logging.error(f"Erreur lors du chargement de l'image '{image_path}': {e}")
            # Utiliser une image par défaut existante si l'image spécifiée n'est pas trouvée
            default_path = os.path.join(img_folder, 'cardrouge.png')
            try:
                image = pygame.image.load(default_path).convert_alpha()
                return image
            except pygame.error as e:
                logging.error(f"Erreur lors du chargement de l'image de défaut: '{default_path}': {e}")
                return None

    def resize_for_cell(self, cell_width, cell_height):
        """Redimensionne l'image de la carte et son fond pour s'adapter à une cellule."""
        if self.image:
            self.image = pygame.transform.scale(self.image, (cell_width, cell_height))
        self.background = pygame.transform.scale(self.background, (cell_width, cell_height))
        self.width = cell_width
        self.height = cell_height

    def resize_for_hand(self, hand_width, hand_height):
        """Redimensionne l'image de la carte et son fond pour s'adapter à la main du joueur."""
        if self.image:
            self.image = pygame.transform.scale(self.image, (hand_width, hand_height))
        self.background = pygame.transform.scale(self.background, (hand_width, hand_height))
        self.width = hand_width
        self.height = hand_height

    def change_background(self, new_background):
        self.background_path = new_background
        self.background = self.load_image(self.background_path)

    def draw_numbers(self, fenetre, font = None, center_x = None, center_y = None):
        """Dessine les chiffres sur les cartes avec un contour noir."""
        if self.image:
            width, height = self.width, self.height
            if center_x is None:
                x_offset = self.x
            else:
                x_offset = center_x - width // 2

            if center_y is None:
                y_offset = self.y
            else:
                y_offset = center_y - height // 2

            positions = [
                (width // 2, 10),  # Nord
                (10, height // 2),  # Ouest
                (width // 2, height - 20),  # Sud
                (width - 20, height // 2)  # Est
            ]
            if font is None:
                font_bold_italic = pygame.font.SysFont("Arial", 24, bold=True, italic=True)  # Police en gras et italique
            else:
                font_bold_italic = font

            for i, number in enumerate(self.numbers):
                # Dessiner le contour noir
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        text_outline = font_bold_italic.render(str(number), True, (0, 0, 0))  # Noir pour le contour
                        text_outline_rect = text_outline.get_rect(center=positions[i])
                        fenetre.blit(text_outline, (x_offset + text_outline_rect.x + dx, y_offset + text_outline_rect.y + dy))
                        
                 # Dessiner le contour noir avec une épaisseur
                text_outline = font_bold_italic.render(str(number), True, (0, 0, 0))  # Noir pour le contour
                text_outline_rect = text_outline.get_rect(center=positions[i])
                fenetre.blit(text_outline, (x_offset + text_outline_rect.x -1, y_offset + text_outline_rect.y))
                fenetre.blit(text_outline, (x_offset + text_outline_rect.x + 1, y_offset + text_outline_rect.y))
                fenetre.blit(text_outline, (x_offset + text_outline_rect.x , y_offset + text_outline_rect.y -1))
                fenetre.blit(text_outline, (x_offset + text_outline_rect.x , y_offset + text_outline_rect.y +1))

                # Dessiner le texte principal (vert)
                text = font_bold_italic.render(str(number), True, (0, 255, 0))  # Couleur verte pour les chiffres
                text_rect = text.get_rect(center=positions[i])
                fenetre.blit(text, (x_offset + text_rect.x, y_offset + text_rect.y))

    def rotate(self, fenetre, cell_x, cell_y, dessiner_plateau, game_board):
        """Fait pivoter la carte."""
        original_center = self.image.get_rect(topleft=(cell_x, cell_y)).center
        for angle in range(0, 181, 10):
            rotated_image = pygame.transform.rotate(self.image, angle)
            rotated_rect = rotated_image.get_rect(center=original_center)
            rotated_background = pygame.transform.rotate(self.background, angle)
            rotated_background_rect = rotated_background.get_rect(center=original_center)
            fenetre.blit(rotated_background, rotated_background_rect.topleft)
            fenetre.blit(rotated_image, rotated_rect.topleft)
            dessiner_plateau(fenetre)
            for i, carte in enumerate(game_board):
                if carte is not None:
                    if carte.name == self.name:
                        carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
                    else:
                        carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
            pygame.display.flip()
            pygame.time.delay(50)
        for angle in range(180, 361, 10):
            rotated_image = pygame.transform.rotate(self.image, angle)
            rotated_rect = rotated_image.get_rect(center=original_center)
            rotated_background = pygame.transform.rotate(self.background, angle)
            rotated_background_rect = rotated_background.get_rect(center=original_center)
            fenetre.blit(rotated_background, rotated_background_rect.topleft)
            fenetre.blit(rotated_image, rotated_rect.topleft)
            dessiner_plateau(fenetre)
            for i, carte in enumerate(game_board):
                if carte is not None:
                    if carte.name == self.name:
                        carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
                    else:
                        carte.draw_numbers(fenetre, pygame.font.SysFont("Arial", 24, bold=True))
            pygame.display.flip()
            pygame.time.delay(50)

    def to_dict(self):
        """Convertit la carte en un dictionnaire pour la sérialisation JSON."""
        return {
            "name": self.name,
            "attribute": self.attribute,
            "numbers": self.numbers,
            "background": self.background_path,
            "img_path": self.img_path
        }

    def get_numbers_rect(self):
        """Retourne le rectangle englobant les chiffres de la carte."""
        numbers_surface = pygame.Surface((0, 0), pygame.SRCALPHA) # Surface temporaire
        font_bold = pygame.font.SysFont("Arial", 24, bold=True)

        max_width = 0
        total_height = 0

        for number in self.numbers:
            text = font_bold.render(str(number), True, (255, 255, 255))
            text_rect = text.get_rect()

            max_width = max(max_width, text_rect.width)
            total_height += text_rect.height


        return pygame.Rect(0,0,max_width,total_height)
