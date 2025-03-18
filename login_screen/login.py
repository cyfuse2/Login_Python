import tkinter as tk
from tkinter import messagebox
import logging
import hashlib
from pymongo import MongoClient
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

MONGODB_URI = "mongodb+srv://carlos:sYDh0xjIIIfGJO63@institutocaxingui.qipu1.mongodb.net/my_database?retryWrites=true&w=majority&appName=institutocaxingui"

# Conexão com o MongoDB
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
        self.collection = users_collection  # Coleção MongoDB

    def register_user(self, username: str, password: str) -> tuple:
        try:
            if len(username) < self.config.MIN_USERNAME_LENGTH:
                return (False, f"Nome de usuário muito curto (mínimo {self.config.MIN_USERNAME_LENGTH} caracteres)")
            if len(password) < self.config.MIN_PASSWORD_LENGTH:
                return (False, f"Senha muito curta (mínimo {self.config.MIN_PASSWORD_LENGTH} caracteres)")
            
            hashed_password = self._hash_password(password)
            
            if self.collection.find_one({"username": username}):
                return (False, "Nome de usuário já está em uso")
            
            self.collection.insert_one({"username": username, "password": hashed_password})
            return (True, "Registro bem-sucedido!")
        
        except Exception as e:
            logging.error(f"Erro crítico no registro: {str(e)}")
            return (False, f"Erro interno: {str(e)}")

    def validate_user(self, username: str, password: str) -> bool:
        try:
            hashed_password = self._hash_password(password)
            user = self.collection.find_one({"username": username})
            return user and user["password"] == hashed_password
        except Exception as e:
            logging.error(f"Erro na validação: {str(e)}")
            return False

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

class AuthManager:
    def __init__(self, db):
        self.db = db
        
    def validate_credentials(self, username: str, password: str) -> bool:
        if not self._validate_input(username, AppConfig.MIN_USERNAME_LENGTH) or \
           not self._validate_input(password, AppConfig.MIN_PASSWORD_LENGTH):
            return False
        return self.db.validate_user(username, password)
    
    @staticmethod
    def _validate_input(value: str, min_length: int) -> bool:
        value = value.strip()
        if len(value) < min_length or any(char.isspace() for char in value):
            return False
        return True

class LoginScreen:
    def __init__(self, master: tk.Tk, db, config: AppConfig = AppConfig()):
        self.master = master
        self.config = config
        self.db = db
        self.auth = AuthManager(db)
        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self) -> None:
        self.master.title(self.config.WINDOW_TITLE)
        self.master.geometry(self.config.WINDOW_SIZE)
        self.master.configure(bg=self.config.BG_COLOR)
        self.master.resizable(False, False)

    def _create_widgets(self) -> None:
        self.frame = self._create_frame()
        self._create_labels()
        self._create_entries()
        self._create_buttons()
        self._create_checkbox()

    def _create_frame(self) -> tk.Frame:
        frame = tk.Frame(self.master, bg=self.config.BG_COLOR)
        frame.pack(expand=True, padx=20, pady=10)
        return frame

    def _create_labels(self) -> None:
        tk.Label(
            self.frame,
            text="Bem-vindo",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR,
            font=(self.config.FONT, self.config.TITLE_FONT_SIZE)
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(
            self.frame,
            text="Usuário:",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR
        ).grid(row=1, column=0, pady=5, sticky='e')

        tk.Label(
            self.frame,
            text="Senha:",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR
        ).grid(row=2, column=0, pady=5, sticky='e')

    def _create_entries(self) -> None:
        self.username_entry = tk.Entry(self.frame, font=(self.config.FONT, self.config.FONT_SIZE))
        self.username_entry.grid(row=1, column=1, pady=5)

        self.password_entry = tk.Entry(self.frame, show="*", font=(self.config.FONT, self.config.FONT_SIZE))
        self.password_entry.grid(row=2, column=1, pady=5)

    def _create_buttons(self) -> None:
        btn_frame = tk.Frame(self.frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(
            btn_frame,
            text="Login",
            command=self._handle_login,
            width=15,
            bg=self.config.BUTTON_BG,
            fg=self.config.TEXT_COLOR
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="Registrar",
            command=self._open_registration,
            width=15,
            bg=self.config.BUTTON_BG,
            fg=self.config.TEXT_COLOR
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="Sair",
            command=self.master.destroy,
            width=15,
            bg=self.config.ERROR_COLOR,
            fg=self.config.TEXT_COLOR
        ).pack(side='left', padx=5)

    def _open_registration(self) -> None:
        Cadastro(self.master, self.db, self.config)

    def _create_checkbox(self) -> None:
        self.show_password = tk.BooleanVar()
        tk.Checkbutton(
            self.frame,
            text="Mostrar senha",
            variable=self.show_password,
            command=self._toggle_password_visibility,
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR,
            selectcolor=self.config.BG_COLOR
        ).grid(row=4, column=0, columnspan=2)  # Corrigido de row=5 para row=4

    def _bind_events(self) -> None:
        self.master.bind('<Return>', lambda event: self._handle_login())

    def _handle_login(self) -> None:
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            if not username or not password:
                self._show_error("Preencha todos os campos!")
                return

            success = self.auth.validate_credentials(username, password)
            
            if success:
                self._on_login_success()
            else:
                self._show_error("Usuário ou senha inválidos")

        except Exception as e:
            logging.error(f"Erro no login: {str(e)}")
            self._show_error("Erro interno no sistema")

    def _validate_fields(self, username: str, password: str) -> bool:
        if not username or not password:
            self._show_error("Preencha todos os campos!")
            return False
        return True

    def _show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)
        self.password_entry.delete(0, tk.END)

    def _on_login_success(self) -> None:
        messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
        self.master.destroy()

    def _toggle_password_visibility(self) -> None:
        show = self.show_password.get()
        self.password_entry.config(show="" if show else "*")

class Cadastro(tk.Toplevel):
    def __init__(self, master, db, config):
        super().__init__(master)
        self.db = db
        self.config = config
        
        self.title("Cadastro de Usuário")
        self.geometry("300x250")
        self.configure(bg=self.config.BG_COLOR)
        self.resizable(False, False)
        
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        frame = tk.Frame(self, bg=self.config.BG_COLOR)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        tk.Label(
            frame,
            text="Cadastro",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR,
            font=(self.config.FONT, self.config.TITLE_FONT_SIZE)
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Usuário:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=1, column=0, pady=5)
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Senha:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=2, column=0, pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Confirmar Senha:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=3, column=0, pady=5)
        self.confirm_entry = tk.Entry(frame, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=5)

        tk.Button(
            frame,
            text="Registrar",
            command=self._executar_registro,
            bg=self.config.BUTTON_BG,
            fg=self.config.TEXT_COLOR
        ).grid(row=4, column=0, columnspan=2, pady=10)

    def _bind_events(self):
        self.bind('<Return>', self._executar_registro)

    def _executar_registro(self, event=None):
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            confirm = self.confirm_entry.get().strip()

            if not self._validate_inputs(username, password, confirm):
                return

            success, message = self.db.register_user(username, password)
            
            if success:
                messagebox.showinfo("Sucesso", message)
                self.destroy()
            else:
                messagebox.showerror("Erro", message)
                
        except Exception as e:
            logging.error(f"Erro no registro: {str(e)}")
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")

    def _validate_inputs(self, username: str, password: str, confirm: str) -> bool:
        if len(username) < self.db.config.MIN_USERNAME_LENGTH:
            messagebox.showerror("Erro", f"Nome de usuário muito curto (mínimo {self.db.config.MIN_USERNAME_LENGTH} caracteres)")
            return False
            
        if len(password) < self.db.config.MIN_PASSWORD_LENGTH:
            messagebox.showerror("Erro", f"Senha muito curta (mínimo {self.db.config.MIN_PASSWORD_LENGTH} caracteres)")
            return False
            
        if password != confirm:
            messagebox.showerror("Erro", "As senhas não coincidem")
            return False
            
        return True

def main() -> None:
    root = tk.Tk()
    config = AppConfig()
    db_config = DatabaseConfig(
        MIN_USERNAME_LENGTH=config.MIN_USERNAME_LENGTH,
        MIN_PASSWORD_LENGTH=config.MIN_PASSWORD_LENGTH
    )
    db = UserDB(db_config)
    LoginScreen(root, db, config)
    root.mainloop()

if __name__ == "__main__":
    main()