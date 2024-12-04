import pygame
import sys
import maze_game
from climb_wall import run_game as run_climber_game

pygame.init()


WIDTH = 1150
HEIGHT = 640

WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
HOVER_BLUE = (150, 150, 255)
RED = (255, 100, 100)
HOVER_RED = (255, 150, 150)

class Button:
    def __init__(self, x, y, width, height, text, text_size=50, color=BLUE, hover_color=HOVER_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, text_size)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(128)
        s.fill(color)
        surface.blit(s, (self.rect.x, self.rect.y))

        pygame.draw.rect(surface, WHITE, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

def init_display():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    background = pygame.image.load('background.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    return screen, background

def main_menu():
    screen, background = init_display()
    clock = pygame.time.Clock()

    maze_button = Button(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 60, "Play Maze Game")
    climber_button = Button(WIDTH//2 - 150, HEIGHT//2, 300, 60, "Play Wall Climber")
    quit_button = Button(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60, "Quit", color=RED, hover_color=HOVER_RED)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if maze_button.handle_event(event):
                maze_game.run_game()
                screen, background = init_display()

            if climber_button.handle_event(event):
                run_climber_game()
                screen, background = init_display()

            if quit_button.handle_event(event):
                pygame.quit()
                sys.exit()

        screen.blit(background, (0, 0))
        maze_button.draw(screen)
        climber_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()