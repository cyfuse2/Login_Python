import tkinter as tk
from tkinter import messagebox
import logging
import hashlib
from pymongo import MongoClient
from dataclasses import dataclass

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

# Configurações do MongoDB
MONGODB_URI = "mongodb+srv://carlos:sYDh0xjIIIfGJO63@institutocaxingui.qipu1.mongodb.net/my_database?retryWrites=true&w=majority&appName=institutocaxingui"
client = MongoClient(MONGODB_URI)
db = client['institutocaxingui']
users_collection = db.users

@dataclass
class AppConfig:
    WINDOW_TITLE: str = "Sistema de Login"
    WINDOW_SIZE: str = "500x220"
    BG_COLOR: str = '#333333'
    TEXT_COLOR: str = '#FFFFFF'
    BUTTON_BG: str = '#4CAF50'
    ERROR_COLOR: str = '#FF0000'
    FONT: str = "Arial"
    FONT_SIZE: int = 12
    TITLE_FONT_SIZE: int = 20
    MIN_USERNAME_LENGTH: int = 3
    MIN_PASSWORD_LENGTH: int = 5

@dataclass
class DatabaseConfig:
    MIN_USERNAME_LENGTH: int
    MIN_PASSWORD_LENGTH: int

class UserDB:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.collection = users_collection

    def register_user(self, username: str, password: str) -> tuple:
        if len(username) < self.config.MIN_USERNAME_LENGTH:
            return (False, f"Nome de usuário muito curto (mínimo {self.config.MIN_USERNAME_LENGTH} caracteres)")
        if len(password) < self.config.MIN_PASSWORD_LENGTH:
            return (False, f"Senha muito curta (mínimo {self.config.MIN_PASSWORD_LENGTH} caracteres)")
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if self.collection.find_one({"username": username}):
            return (False, "Nome de usuário já está em uso")
        
        self.collection.insert_one({"username": username, "password": hashed_password})
        return (True, "Registro bem-sucedido!")

    def validate_user(self, username: str, password: str) -> bool:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = self.collection.find_one({"username": username})
        return user and user["password"] == hashed_password

class AuthManager:
    def __init__(self, db):
        self.db = db
        
    def validate_credentials(self, username: str, password: str) -> bool:
        return self.db.validate_user(username, password)

class LoginScreen(tk.Toplevel):
    def __init__(self, master, db, config):
        super().__init__(master)
        self.config = config
        self.db = db
        self.auth = AuthManager(db)
        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self):
        self.title(self.config.WINDOW_TITLE)
        self.geometry(self.config.WINDOW_SIZE)
        self.configure(bg=self.config.BG_COLOR)
        self.resizable(False, False)

    def _create_widgets(self):
        frame = tk.Frame(self, bg=self.config.BG_COLOR)
        frame.pack(expand=True, padx=20, pady=10)

        tk.Label(frame, text="Bem-vindo", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR,
                font=(self.config.FONT, self.config.TITLE_FONT_SIZE)).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Usuário:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=1, column=0, pady=5, sticky='e')
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Senha:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=2, column=0, pady=5, sticky='e')
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Login", command=self._handle_login, width=15,
                 bg=self.config.BUTTON_BG, fg=self.config.TEXT_COLOR).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Registrar", command=self._open_registration, width=15,
                 bg=self.config.BUTTON_BG, fg=self.config.TEXT_COLOR).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Sair", command=self.destroy, width=15,
                 bg=self.config.ERROR_COLOR, fg=self.config.TEXT_COLOR).pack(side='left', padx=5)

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.auth.validate_credentials(username, password):
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas")

    def _open_registration(self):
        Cadastro(self, self.db, self.config)

class Cadastro(tk.Toplevel):
    def __init__(self, master, db, config):
        super().__init__(master)
        self.db = db
        self.config = config
        self.title("Cadastro de Usuário")
        self.geometry("300x250")
        self.configure(bg=self.config.BG_COLOR)
        self._create_widgets()

    def _create_widgets(self):
        frame = tk.Frame(self, bg=self.config.BG_COLOR)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Cadastro", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR,
                font=(self.config.FONT, self.config.TITLE_FONT_SIZE)).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Usuário:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=1, column=0, pady=5)
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Senha:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=2, column=0, pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        tk.Button(frame, text="Registrar", command=self._executar_registro,
                 bg=self.config.BUTTON_BG, fg=self.config.TEXT_COLOR).grid(row=3, column=0, columnspan=2, pady=10)

    def _executar_registro(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        success, message = self.db.register_user(username, password)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.destroy()
        else:
            messagebox.showerror("Erro", message)

# Configuração do menu principal
janela = tk.Tk()
janela.title("Sistema de Menu")
janela.geometry("400x300")

# Configurações do banco de dados
config = AppConfig()
db_config = DatabaseConfig(
    MIN_USERNAME_LENGTH=config.MIN_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH=config.MIN_PASSWORD_LENGTH
)
db = UserDB(db_config)

# Frame principal
frame = tk.Frame(janela, padx=20, pady=20)
frame.pack(expand=True)

# Componentes do menu
tk.Label(frame, text="Menu Principal", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)

botoes = [
    ("Login", lambda: LoginScreen(janela, db, config)),
    ("Consulta", lambda: messagebox.showinfo("Consulta", "Função de consulta")),
    ("Relatório", lambda: messagebox.showinfo("Relatório", "Função de relatório")),
    ("Sair", janela.destroy)
]

for i, (texto, comando) in enumerate(botoes, start=1):
    tk.Button(frame, text=texto, width=15, height=2, command=comando).grid(row=i, column=0, pady=5, sticky="ew")

# Configuração de layout
for i in range(5):
    frame.grid_rowconfigure(i, weight=1)
frame.grid_columnconfigure(0, weight=1)

janela.mainloop()