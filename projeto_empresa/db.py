import sqlite3
import hashlib
import logging
from dataclasses import dataclass
from config import DatabaseConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

class UserDB:
    def __init__(self, config: DatabaseConfig = DatabaseConfig()):
        self.config = config
        self._initialize_db()

    def _initialize_db(self) -> None:
        with sqlite3.connect(self.config.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.config.TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

    def register_user(self, username: str, password: str) -> tuple:
        try:
            if len(username) < self.config.MIN_USERNAME_LENGTH:
                return (False, f"Nome de usuário muito curto (mínimo {self.config.MIN_USERNAME_LENGTH} caracteres)")
            
            if len(password) < self.config.MIN_PASSWORD_LENGTH:
                return (False, f"Senha muito curta (mínimo {self.config.MIN_PASSWORD_LENGTH} caracteres)")

            hashed_password = self._hash_password(password)
            
            with sqlite3.connect(self.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    INSERT INTO {self.config.TABLE_NAME} (username, password)
                    VALUES (?, ?)
                ''', (username, hashed_password))
                conn.commit()
                return (True, "Registro bem-sucedido!")
                
        except sqlite3.IntegrityError:
            return (False, "Nome de usuário já está em uso")
            
        except Exception as e:
            logging.error(f"Erro crítico no registro: {str(e)}")
            return (False, f"Erro interno: {str(e)}")

    def validate_user(self, username: str, password: str) -> bool:
        try:
            hashed_password = self._hash_password(password)
            with sqlite3.connect(self.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT password FROM {self.config.TABLE_NAME}
                    WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                return result and result[0] == hashed_password
        except Exception as e:
            logging.error(f"Erro na validação: {str(e)}")
            return False

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def search_users(self, search_term: str) -> list:
            """Busca usuários que começam com o termo fornecido"""
            try:
                with sqlite3.connect(self.config.DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f'''
                        SELECT username FROM {self.config.TABLE_NAME}
                        WHERE username LIKE ? || '%'
                        ORDER BY username
                        LIMIT 10
                    ''', (search_term,))
                    return [row[0] for row in cursor.fetchall()]
            except Exception as e:
                logging.error(f"Erro na busca de usuários: {str(e)}")
                return []

class AuthManager:
    def __init__(self, db):
        self.db = db
        
    def validate_credentials(self, username: str, password: str) -> bool:
        if not self._validate_input(username, self.db.config.MIN_USERNAME_LENGTH) or \
           not self._validate_input(password, self.db.config.MIN_PASSWORD_LENGTH):
            return False
        return self.db.validate_user(username, password)
    
    @staticmethod
    def _validate_input(value: str, min_length: int) -> bool:
        value = value.strip()
        if len(value) < min_length:
            logging.warning(f"Entrada muito curta: {value}")
            return False
        if any(char.isspace() for char in value):
            logging.warning("Entrada contém espaços")
            return False
        return True