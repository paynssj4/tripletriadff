import pygame

def draw_text_with_outline(fenetre, text, font, color, outline_color, position):
    """Dessine du texte avec un contour plus épais pour un meilleur rendu."""
    text_surface = font.render(text, True, color)
    outline_surface = font.render(text, True, outline_color)
    x, y = position

    # Dessiner le contour avec une épaisseur plus grande
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
          if dx != 0 or dy != 0 :
                fenetre.blit(outline_surface, (x + dx, y + dy))

    # Dessiner le texte
    fenetre.blit(text_surface, position)

def afficher_message_fin(fenetre, message, largeur_fenetre, hauteur_fenetre, replay_option=True, new_game_option=False):
    """Affiche le message de fin avec des options pour rejouer, commencer une nouvelle partie ou quitter."""
    font = pygame.font.SysFont(None, 48, bold=True)
    text_color = (192, 192, 192)  # Gris métallisé
    outline_color = (0, 0, 0)  # Noir
    text_rect = font.render(message, True, text_color).get_rect(center=(largeur_fenetre // 2, hauteur_fenetre // 2 - 50))

    rejouer_rect = pygame.Rect(largeur_fenetre // 2 - 150, hauteur_fenetre // 2 + 50, 140, 50)
    nouvelle_partie_rect = pygame.Rect(largeur_fenetre // 2 - 200, hauteur_fenetre // 2 + 120, 240, 50)
    quitter_rect = pygame.Rect(largeur_fenetre // 2 + 10, hauteur_fenetre // 2 + 50, 140, 50)

    rejouer_text = font.render("Rejouer", True, (255, 255, 255))
    nouvelle_partie_text = font.render("Nouvelle Partie", True, (255, 255, 255))
    quitter_text = font.render("Quitter", True, (255, 255, 255))

    fenetre.fill((0, 0, 0))  # Effacer l'écran
    draw_text_with_outline(fenetre, message, font, text_color, outline_color, text_rect.topleft)

    # Dessiner les boutons si l'option de rejouer est activée.
    if replay_option:
        pygame.draw.rect(fenetre, (50, 50, 50), rejouer_rect)
        fenetre.blit(rejouer_text, (rejouer_rect.x + 10, rejouer_rect.y + 10))
    if new_game_option:
        pygame.draw.rect(fenetre, (50, 50, 50), nouvelle_partie_rect)
        fenetre.blit(nouvelle_partie_text, (nouvelle_partie_rect.x + 10, nouvelle_partie_rect.y + 10))
    pygame.draw.rect(fenetre, (50, 50, 50), quitter_rect)
    fenetre.blit(quitter_text, (quitter_rect.x + 10, quitter_rect.y + 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if replay_option and rejouer_rect.collidepoint(x, y):
                    return True
                elif new_game_option and nouvelle_partie_rect.collidepoint(x, y):
                    return "nouvelle_partie"  # Recommencer une nouvelle partie
                elif quitter_rect.collidepoint(x, y):
                    pygame.quit()
                    return False

