import sqlite3
from contextlib import closing
from dataclasses import dataclass
import hashlib

@dataclass
class DatabaseConfig:
    DB_NAME: str = "users.db"
    TABLE_NAME: str = "users"
    MIN_USERNAME_LENGTH: int = 4
    MIN_PASSWORD_LENGTH: int = 6

class UserDB:
    def __init__(self, config: DatabaseConfig = DatabaseConfig()):
        self.config = config
        self._initialize_db()

    def _initialize_db(self) -> None:
        with closing(sqlite3.connect(self.config.DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.config.TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

    def register_user(self, username: str, password: str) -> bool:
        try:
            with closing(sqlite3.connect(self.config.DB_NAME)) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    INSERT INTO {self.config.TABLE_NAME} (username, password)
                    VALUES (?, ?)
                ''', (username, self._hash_password(password)))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username: str, password: str) -> bool:
        with closing(sqlite3.connect(self.config.DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT password FROM {self.config.TABLE_NAME}
                WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()
            return result and result[0] == self._hash_password(password)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()