import pygame
from typing import Callable, Optional
from config import COLORS, FONTS


class Button:
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 onclick: Callable = None, color: tuple = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.onclick = onclick
        self.color = color or COLORS['PRIMARY']
        self.hover_color = tuple(min(255, c + 30) for c in self.color)
        self.is_hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.onclick:
                self.onclick()
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['TEXT'], self.rect, 2)
        
        text_surface = FONTS['LARGE'].render(self.text, True, COLORS['TEXT'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class InputField:
    
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    
    def draw(self, screen):
        color = COLORS['PRIMARY'] if self.active else COLORS['SECONDARY']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['TEXT'], self.rect, 2)
        
        display_text = self.text or self.placeholder
        text_color = COLORS['TEXT'] if self.text else COLORS['GRAY']
        text_surface = FONTS['LARGE'].render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))


class HangmanDrawing:
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def draw(self, screen, mistakes: int):
        parts = [
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x, self.y + 200), (self.x + 100, self.y + 200), 5),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 20, self.y + 200), (self.x + 20, self.y), 5),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 20, self.y), (self.x + 80, self.y), 5),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y), (self.x + 80, self.y + 30), 5),
            lambda: pygame.draw.circle(screen, COLORS['TEXT'], (self.x + 80, self.y + 45), 15, 3),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y + 60), (self.x + 80, self.y + 140), 5),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y + 100), (self.x + 60, self.y + 80), 3),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y + 100), (self.x + 100, self.y + 80), 3),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y + 140), (self.x + 60, self.y + 170), 3),
            lambda: pygame.draw.line(screen, COLORS['TEXT'], (self.x + 80, self.y + 140), (self.x + 100, self.y + 170), 3)
        ]
        
        for i in range(min(mistakes, len(parts))):
            parts[i]()


class AlphabetGrid:
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.alphabet = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPQRSŚTUVWXYZŹŻ"
        self.button_size = 40
        self.button_spacing = 45
        self.buttons = []
        self.selected_letters = set()
        
        for i, letter in enumerate(self.alphabet):
            row = i // 8
            col = i % 8
            button_x = self.x + col * self.button_spacing
            button_y = self.y + row * self.button_spacing
            self.buttons.append({
                'letter': letter,
                'rect': pygame.Rect(button_x, button_y, self.button_size, self.button_size)
            })
    
    def handle_event(self, event, callback):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button['rect'].collidepoint(event.pos):
                    letter = button['letter']
                    if letter not in self.selected_letters:
                        self.selected_letters.add(letter)
                        callback(letter)
    
    def draw(self, screen):
        for button in self.buttons:
            letter = button['letter']
            rect = button['rect']
            
            if letter in self.selected_letters:
                color = COLORS['GRAY']
            else:
                color = COLORS['PRIMARY']
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS['TEXT'], rect, 1)
            
            text_surface = FONTS['DEFAULT'].render(letter, True, COLORS['TEXT'])
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect) 