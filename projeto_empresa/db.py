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
        print("Iniciando banco de dados...")  # Debug
        self._initialize_db()
        self._create_product_table()
        print("Tabelas verificadas com sucesso!")  # Debug

    def get_all_products(self) -> list:
        """Retorna todos os produtos do estoque"""
        try:
            with sqlite3.connect(self.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM produtos ORDER BY data_cadastro DESC")
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao buscar produtos: {str(e)}")
            return []

    def _initialize_db(self) -> None:
        try:
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
                print("Tabela de usuários criada!")  # Debug
        except Exception as e:
            print(f"Erro ao criar tabela de usuários: {str(e)}")  # Debug

    def register_user(self, username: str, password: str) -> tuple:
        try:
            if len(username) < self.config.MIN_USERNAME_LENGTH:
                return (False, f"Nome de usuário muito curto (mínimo {self.config.MIN_USERNAME_LENGTH} caracteres)")
            
            if len(password) < self.config.MIN_PASSWORD_LENGTH:
                return (False, f"Senha muito curta (mínimo {self.config.MIN_PASSWORD_LENGTH} caracteres)")

            hashed_password = UserDB._hash_password(password)
            
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

    def _create_product_table(self):
        try:
            with sqlite3.connect(self.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco REAL NOT NULL,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                print(" Tabela 'produtos' criada/verificada!")
                conn.commit()
        except Exception as e:
            print(f" Erro na tabela produtos: {str(e)}")

    def register_product(self, nome: str, quantidade: int, preco: float) -> bool:
        try:
            with sqlite3.connect(self.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO produtos (nome, quantidade, preco)
                    VALUES (?, ?, ?)
                ''', (nome, quantidade, preco))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Erro no cadastro de produto: {str(e)}")
            return False
    
class AuthManager:
    def __init__(self, db):
        self.db = db  # Recebe a instância do UserDB
        
    def validate_credentials(self, username: str, password: str) -> bool:
        if not self._validate_input(username, self.db.config.MIN_USERNAME_LENGTH) or \
           not self._validate_input(password, self.db.config.MIN_PASSWORD_LENGTH):
            return False
        
        # Corrigido: usar o método de hash da classe UserDB
        hashed_password = UserDB._hash_password(password)  # ← Alteração aqui
        
        try:
            with sqlite3.connect(self.db.config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT password FROM {self.db.config.TABLE_NAME}
                    WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                return result and result[0] == hashed_password
        except Exception as e:
            logging.error(f"Erro na validação: {str(e)}")
            return False
    
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