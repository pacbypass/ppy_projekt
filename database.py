import sqlite3
import random
from typing import List, Optional, Tuple
from config import DATABASE_PATH
from encryption import hash_password, verify_password

def init_database():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                category TEXT NOT NULL,
                hint TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1 TEXT NOT NULL,
                player2 TEXT,
                word TEXT NOT NULL,
                winner TEXT,
                game_mode TEXT NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM words")
        if cursor.fetchone()[0] == 0:
            words_data = [
                ("SŁOŃ", "Zwierzęta", "Największe zwierzę lądowe"),
                ("ŻYRAFA", "Zwierzęta", "Najwyższe zwierzę na świecie"),
                ("PINGWIN", "Zwierzęta", "Ptak który nie lata ale pływa"),
                ("POLSKA", "Kraje", "Nasz kraj"),
                ("FRANCJA", "Kraje", "Kraj wieży Eiffla"),
                ("CHINY", "Kraje", "Produkuje wszystko "),
                ("PIZZA", "Jedzenie", "Włoska potrawa z ciastem"),
                ("SUSHI", "Jedzenie", "Japońska potrawa z ryżem"),
                ("PIEROGI", "Jedzenie", "Tradycyjne polskie danie"),
                ("PIŁKA", "Sport", "Podstawowy sprzęt w wielu sportach"),
                ("TENIS", "Sport", "Gra z rakietą"),
                ("KOMPUTER", "Nauka", "Urządzenie elektroniczne"),
                ("INTERNET", "Nauka", "Globalna sieć"),
                ("ATOM", "Nauka", "Podstawowa jednostka materii")
            ]
            cursor.executemany("INSERT INTO words (word, category, hint) VALUES (?, ?, ?)", words_data)
        
        conn.commit()

def create_user(username: str, password: str) -> bool:
    try:
        password_hash_result = hash_password(password)
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash_result))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username: str, password: str) -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row and verify_password(password, row[0])

def get_user_stats(username: str) -> Tuple[int, int]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT games_played, games_won FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row if row else (0, 0)

def update_user_stats(username: str, won: bool):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET games_played = games_played + 1, games_won = games_won + ? WHERE username = ?",
            (1 if won else 0, username)
        )
        conn.commit()

def get_categories() -> List[str]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM words ORDER BY category")
        return [row[0] for row in cursor.fetchall()]

def get_random_word(category: str = None) -> Optional[Tuple[str, str]]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT word, hint FROM words WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT word, hint FROM words")
        rows = cursor.fetchall()
        if rows:
            return random.choice(rows)
        return None

def save_game_result(player1: str, player2: str, word: str, winner: str, game_mode: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO game_history (player1, player2, word, winner, game_mode) VALUES (?, ?, ?, ?, ?)",
            (player1, player2, word, winner, game_mode)
        )
        conn.commit()

def get_user_history(username: str) -> List[Tuple]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT word, game_mode, winner FROM game_history WHERE player1 = ? OR player2 = ? ORDER BY id DESC LIMIT 10",
            (username, username)
        )
        return cursor.fetchall()

init_database() 