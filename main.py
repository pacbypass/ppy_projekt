import pygame
import sys
from config import *
from screens import LoginScreen, MenuScreen, GameScreen

class HangmanGameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Gra w Wisielca")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.current_screen = "login"
        self.current_user = None
        self.screens = {
            "login": LoginScreen(self),
            "menu": MenuScreen(self),
            "game": GameScreen(self)
        }
    
    def set_screen(self, screen_name, **kwargs):
        self.current_screen = screen_name
        if hasattr(self.screens[screen_name], 'reset'):
            self.screens[screen_name].reset(**kwargs)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.screens[self.current_screen].handle_event(event)
            
            self.screens[self.current_screen].update(dt)
            
            self.screen.fill(COLORS['BACKGROUND'])
            self.screens[self.current_screen].draw(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = HangmanGameApp()
    app.run() 