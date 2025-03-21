import tkinter as tk
from tkinter import messagebox
import logging
from config import AppConfig  # Adicione esta linha

class Cadastro(tk.Toplevel):
    def __init__(self, master, db, config: AppConfig):
        super().__init__(master)
        self.db = db  # ← Adicione esta linha crucial
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