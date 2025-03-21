import pygame

def draw_tooltip(fenetre, text, position):
    """Dessine une bulle d'explication."""
    font = pygame.font.SysFont(None, 24)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    tooltip_rect = pygame.Rect(position[0], position[1], text_rect.width + 10, text_rect.height + 10)
    pygame.draw.rect(fenetre, (255, 255, 255), tooltip_rect)
    pygame.draw.rect(fenetre, (0, 0, 0), tooltip_rect, 1)
    fenetre.blit(text_surface, (position[0] + 5, position[1] + 5))
