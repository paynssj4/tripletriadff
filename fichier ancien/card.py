import pygame
import os

# Définir les dimensions de la fenêtre
LARGEUR_FENETRE = 950  # Ajuster si nécessaire
HAUTEUR_FENETRE = 554  # Ajuster si nécessaire

# Définir le dossier où les images sont stockées
img_folder = "/home/greg/Documents/test jeux/test jeux tt/Nouveau dossier/fichier ancien/Img"  # Ajuster ce chemin si nécessaire

class Card:
    def __init__(self, name, attribute, numbers, background, img_path=None):
        self.name = name
        self.attribute = attribute
        self.numbers = numbers
        self.element = ""  # Attribut par défaut
        self.background_path = background
        self.img_path = img_path
        if self.img_path:
            self.image = pygame.image.load(os.path.join(img_folder, self.img_path)).convert_alpha()
        else:
            self.image = None
        self.background = pygame.image.load(os.path.join(img_folder, self.background_path)).convert_alpha()
        self.x = 0
        self.y = 0

    def resize_for_cell(self, cell_width, cell_height):
        """Redimensionne l'image de la carte et son fond pour s'adapter à une cellule."""
        if self.image:
            self.image = pygame.transform.scale(self.image, (cell_width, cell_height))
        self.background = pygame.transform.scale(self.background, (cell_width, cell_height))

    def resize_for_hand(self, hand_width, hand_height):
        """Redimensionne l'image de la carte et son fond pour s'adapter à la main du joueur."""
        if self.image:
            self.image = pygame.transform.scale(self.image, (hand_width, hand_height))
        self.background = pygame.transform.scale(self.background, (hand_width, hand_height))

    def change_background(self, new_background):
        """Change l'image de fond de la carte."""
        self.background_path = new_background
        self.background = pygame.image.load(os.path.join(img_folder, self.background_path)).convert_alpha()

    def draw_numbers(self, fenetre, font):
        """Dessine les chiffres sur les cartes."""
        width, height = self.image.get_size()  # Obtenir la taille de l'image de la carte
        positions = [
            (width // 2, 10),  # Nord
            (10, height // 2),  # Ouest
            (width // 2, height - 20),  # Sud
            (width - 20, height // 2)  # Est
        ]
        font_bold = pygame.font.SysFont("Arial", 24, bold=True)  # Police en gras
        for i, number in enumerate(self.numbers):
            text = font_bold.render(str(number), True, (255, 255, 255))  # Couleur blanche pour les chiffres
            text_rect = text.get_rect(center=positions[i])
            fenetre.blit(text, (self.x + text_rect.x, self.y + text_rect.y)) #Afficher les chiffre sur fenetre et non sur background.

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
