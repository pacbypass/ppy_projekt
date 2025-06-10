import time
from typing import List, Optional, Tuple
from database import get_random_word, save_game_result, update_user_stats

class HangmanGame:
    def __init__(self, player1: str, player2: str = None, game_mode: str = "classic", category: str = None):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.game_mode = game_mode
        self.category = category
        
        word_data = get_random_word(category)
        if not word_data:
            raise ValueError("Nie można pobrać słowa z bazy danych")
        
        self.word = word_data[0].upper()
        self.hint = word_data[1]
        self.guessed_letters = set()
        self.mistakes = 0
        self.max_mistakes = 6
        self.game_over = False
        self.winner = None
        self.start_time = time.time()
        self.hint_used = False
        
        if game_mode == "timed":
            self.time_limit = 120
        else:
            self.time_limit = None
    
    def get_display_word(self) -> str:
        return ''.join(char if char in self.guessed_letters else '_' for char in self.word)
    
    def guess_letter(self, letter: str) -> bool:
        letter = letter.upper()
        if letter in self.guessed_letters:
            return False
        
        self.guessed_letters.add(letter)
        
        if letter not in self.word:
            self.mistakes += 1
            if self.player2:
                self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        
        if self.mistakes >= self.max_mistakes:
            self.game_over = True
            self.winner = self.current_player if self.player2 else None
        elif self.is_word_guessed():
            self.game_over = True
            self.winner = self.current_player
        
        return letter in self.word
    
    def is_word_guessed(self) -> bool:
        return all(char in self.guessed_letters for char in self.word)
    
    def get_time_remaining(self) -> int:
        if not self.time_limit:
            return None
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        if remaining == 0 and not self.game_over:
            self.game_over = True
        return int(remaining)
    
    def use_hint(self) -> str:
        if not self.hint_used:
            self.hint_used = True
            return self.hint
        return None
    
    def save_result(self):
        save_game_result(self.player1, self.player2, self.word, self.winner, self.game_mode)
        
        if self.winner == self.player1:
            update_user_stats(self.player1, True)
            if self.player2:
                update_user_stats(self.player2, False)
        elif self.winner == self.player2:
            update_user_stats(self.player2, True)
            update_user_stats(self.player1, False)
        else:
            update_user_stats(self.player1, False)
            if self.player2:
                update_user_stats(self.player2, False) 