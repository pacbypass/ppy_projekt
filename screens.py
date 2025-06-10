import pygame
import csv
from datetime import datetime
from components import Button, InputField, HangmanDrawing, AlphabetGrid
from database import create_user, authenticate_user, get_user_stats, get_categories, get_user_history
from hangman_game import HangmanGame
from config import *

class LoginScreen:
    def __init__(self, game_app):
        self.game_app = game_app
        self.mode = "login"
        self.message = ""
        
        self.username_field = InputField(400, 300, 200, 40, "Nazwa użytkownika")
        self.password_field = InputField(400, 350, 200, 40, "Hasło")
        
        self.action_btn = Button(400, 420, 200, 40, "Zaloguj", self._handle_action)
        self.switch_btn = Button(400, 480, 200, 30, "Przełącz na rejestrację", self._switch_mode)
    
    def handle_event(self, event):
        self.username_field.handle_event(event)
        self.password_field.handle_event(event)
        self.action_btn.handle_event(event)
        self.switch_btn.handle_event(event)
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.action_btn.update(mouse_pos)
        self.switch_btn.update(mouse_pos)
    
    def draw(self, screen):
        title = FONTS['TITLE'].render("Gra w Wisielca", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        screen.blit(title, title_rect)
        
        self.username_field.draw(screen)
        self.password_field.draw(screen)
        self.action_btn.draw(screen)
        self.switch_btn.draw(screen)
        
        if self.message:
            msg_surface = FONTS['DEFAULT'].render(self.message, True, COLORS['TEXT'])
            msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH // 2, 550))
            screen.blit(msg_surface, msg_rect)
    
    def _handle_action(self):
        username = self.username_field.text.strip()
        password = self.password_field.text
        
        if not username or not password:
            self.message = "Wypełnij wszystkie pola!"
            return
        
        if self.mode == "login":
            if authenticate_user(username, password):
                self.game_app.current_user = username
                self.game_app.set_screen("menu")
            else:
                self.message = "Nieprawidłowe dane logowania!"
        else:
            if len(password) < 4:
                self.message = "Hasło musi mieć co najmniej 4 znaki!"
                return
            
            if create_user(username, password):
                self.message = "Konto utworzone! Możesz się zalogować."
                self._switch_mode()
            else:
                self.message = "Użytkownik już istnieje!"
    
    def _switch_mode(self):
        self.mode = "register" if self.mode == "login" else "login"
        self.action_btn.text = "Rejestruj" if self.mode == "register" else "Zaloguj"
        self.switch_btn.text = "Przełącz na logowanie" if self.mode == "register" else "Przełącz na rejestrację"
        self.username_field.text = ""
        self.password_field.text = ""
        self.message = ""

class MenuScreen:
    def __init__(self, game_app):
        self.game_app = game_app
        
        self.single_btn = Button(400, 250, 200, 50, "Gra 1 gracz", self._single_game)
        self.two_btn = Button(400, 320, 200, 50, "Gra 2 graczy", self._two_game)
        self.stats_btn = Button(400, 390, 200, 50, "Statystyki", self._stats)
        self.logout_btn = Button(400, 460, 200, 50, "Wyloguj", self._logout)
    
    def handle_event(self, event):
        self.single_btn.handle_event(event)
        self.two_btn.handle_event(event)
        self.stats_btn.handle_event(event)
        self.logout_btn.handle_event(event)
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.single_btn.update(mouse_pos)
        self.two_btn.update(mouse_pos)
        self.stats_btn.update(mouse_pos)
        self.logout_btn.update(mouse_pos)
    
    def draw(self, screen):
        welcome = FONTS['LARGE'].render(f"Witaj, {self.game_app.current_user}!", True, COLORS['TEXT'])
        welcome_rect = welcome.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(welcome, welcome_rect)
        
        self.single_btn.draw(screen)
        self.two_btn.draw(screen)
        self.stats_btn.draw(screen)
        self.logout_btn.draw(screen)
    
    def _single_game(self):
        self.game_app.set_screen("game", players=1)
    
    def _two_game(self):
        self.game_app.set_screen("game", players=2)
    
    def _stats(self):
        games_played, games_won = get_user_stats(self.game_app.current_user)
        win_rate = (games_won / games_played * 100) if games_played > 0 else 0
        
        filename = f"stats_{self.game_app.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Użytkownik', 'Rozegrane gry', 'Wygrane gry', 'Współczynnik wygranych'])
            writer.writerow([self.game_app.current_user, games_played, games_won, f"{win_rate:.1f}%"])
            writer.writerow([])
            writer.writerow(['Słowo', 'Tryb gry', 'Wynik'])
            
            history = get_user_history(self.game_app.current_user)
            for word, mode, winner in history:
                result = "Wygrana" if winner == self.game_app.current_user else "Przegrana"
                writer.writerow([word, mode, result])
    
    def _logout(self):
        self.game_app.current_user = None
        self.game_app.set_screen("login")

class GameScreen:
    def __init__(self, game_app):
        self.game_app = game_app
        self.game = None
        self.hangman_drawing = HangmanDrawing(100, 100)
        self.alphabet_grid = AlphabetGrid(400, 450)
        self.message = ""
        self.players = 1
        
        self.hint_btn = Button(50, 50, 100, 40, "Podpowiedź", self._use_hint)
        self.menu_btn = Button(850, 50, 100, 40, "Menu", self._back_to_menu)
        
        categories = get_categories()
        self.category = categories[0] if categories else "Zwierzęta"
        self.mode = "classic"
    
    def reset(self, **kwargs):
        self.players = kwargs.get('players', 1)
        self.game = None
        self.message = ""
        self.alphabet_grid.selected_letters.clear()
        self._start_game()
    
    def _start_game(self):
        player2 = f"{self.game_app.current_user}_2" if self.players == 2 else None
        
        try:
            self.game = HangmanGame(
                self.game_app.current_user,
                player2,
                self.mode,
                self.category
            )
        except ValueError as e:
            self.message = str(e)
    
    def handle_event(self, event):
        if self.game and not self.game.game_over:
            self.alphabet_grid.handle_event(event, self._guess_letter)
            self.hint_btn.handle_event(event)
        self.menu_btn.handle_event(event)
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.hint_btn.update(mouse_pos)
        self.menu_btn.update(mouse_pos)
    
    def draw(self, screen):
        if not self.game:
            return
        
        word_display = " ".join(self.game.get_display_word())
        word_surface = FONTS['LARGE'].render(word_display, True, COLORS['TEXT'])
        screen.blit(word_surface, (400, 200))
        
        info_text = f"Błędy: {self.game.mistakes}/{self.game.max_mistakes} | Tryb: {self.mode}"
        if self.players == 2:
            info_text += f" | Gracz: {self.game.current_player}"
        if self.game.game_mode == "timed":
            time_left = self.game.get_time_remaining()
            if time_left is not None:
                info_text += f" | Czas: {time_left}s"
        
        info_surface = FONTS['DEFAULT'].render(info_text, True, COLORS['TEXT'])
        screen.blit(info_surface, (400, 250))
        
        self.hangman_drawing.draw(screen, self.game.mistakes)
        
        self.alphabet_grid.draw(screen)
        
        if not self.game.hint_used:
            self.hint_btn.draw(screen)
        self.menu_btn.draw(screen)
        
        if self.game.game_over:
            if self.game.winner:
                end_text = f"Wygrywa: {self.game.winner}!"
            else:
                end_text = f"Przegrana! Słowo to: {self.game.word}"
            
            end_surface = FONTS['LARGE'].render(end_text, True, COLORS['TEXT'])
            end_rect = end_surface.get_rect(center=(WINDOW_WIDTH // 2, 350))
            screen.blit(end_surface, end_rect)
        
        if self.message:
            msg_surface = FONTS['DEFAULT'].render(self.message, True, COLORS['TEXT'])
            screen.blit(msg_surface, (400, 580))
    
    def _guess_letter(self, letter):
        if self.game and not self.game.game_over:
            self.game.guess_letter(letter)
            
            if self.game.game_over:
                self.game.save_result()
    
    def _use_hint(self):
        if self.game:
            hint = self.game.use_hint()
            if hint:
                self.message = f"Podpowiedź: {hint}"
    
    def _back_to_menu(self):
        self.game_app.set_screen("menu") 