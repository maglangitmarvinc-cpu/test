"""Small SQLite repository for usernames and completed game scores."""
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DB_PATH = Path(__file__).with_name("snake_game.db")

class ScoreDatabase:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        self.initialize()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def initialize(self):
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    date_created TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS high_scores (
                    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(user_id),
                    score INTEGER NOT NULL CHECK(score >= 0),
                    game_mode TEXT NOT NULL CHECK(game_mode IN ('Solo','Multiplayer')),
                    date_achieved TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS scores_mode_score ON high_scores(game_mode, score DESC);
            """)

    @staticmethod
    def clean_username(username):
        value = " ".join(str(username).strip().split())
        if not value or len(value) > 20 or any(ord(ch) < 32 for ch in value):
            raise ValueError("Username must contain 1–20 visible characters.")
        return value

    def ensure_user(self, username):
        username = self.clean_username(username)
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO users(username,date_created) VALUES(?,?)",
                       (username, datetime.now(timezone.utc).isoformat(timespec="seconds")))
            row = db.execute("SELECT user_id, username FROM users WHERE username=?", (username,)).fetchone()
            return row

    def save_score(self, username, score, mode):
        if mode not in ("Solo", "Multiplayer"):
            raise ValueError("Unknown game mode")
        user_id, _ = self.ensure_user(username)
        with self.connect() as db:
            db.execute("INSERT INTO high_scores(user_id,score,game_mode,date_achieved) VALUES(?,?,?,?)",
                       (user_id, max(0, int(score)), mode, datetime.now(timezone.utc).isoformat(timespec="seconds")))

    def best_score(self, username, mode="Solo"):
        row = self.ensure_user(username)
        with self.connect() as db:
            result = db.execute("SELECT COALESCE(MAX(score),0) FROM high_scores WHERE user_id=? AND game_mode=?",
                                (row[0], mode)).fetchone()
            return result[0]

    def leaderboard(self, mode="Solo", limit=20):
        with self.connect() as db:
            return db.execute("""SELECT u.username, MAX(h.score) AS best, MAX(h.date_achieved)
                FROM high_scores h JOIN users u ON u.user_id=h.user_id
                WHERE h.game_mode=? GROUP BY u.user_id ORDER BY best DESC, u.username COLLATE NOCASE LIMIT ?""",
                (mode, int(limit))).fetchall()
