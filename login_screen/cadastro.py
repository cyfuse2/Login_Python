import tkinter as tk
from tkinter import ttk
from typing import Optional

class Cadastro(tk.Toplevel):
    def __init__(self, master, db, config):
        super().__init__(master)
        self.db = db
        self.config = config
        
        self.title("Registro de Usuário")
        self.geometry("300x250")
        self.configure(bg='#333333')
        self.resizable(False, False)
        
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        self.frame = ttk.Frame(self)
        self.frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Labels
        ttk.Label(self.frame, text="Criar Nova Conta", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Entradas
        ttk.Label(self.frame, text="Usuário:").grid(row=1, column=0, sticky='w')
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.frame, text="Senha:").grid(row=2, column=0, sticky='w')
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.frame, text="Confirmar Senha:").grid(row=3, column=0, sticky='w')
        self.confirm_entry = ttk.Entry(self.frame, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=5)

        # Botões
        self.register_btn = ttk.Button(self.frame, text="Registrar", command=self._register)
        self.register_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def _bind_events(self) -> None:
        self.bind('<Return>', lambda event: self._register())

    def _register(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not self._validate_inputs(username, password, confirm):
            return

        if self.db.register_user(username, password):
            tk.messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
            self.destroy()
        else:
            tk.messagebox.showerror("Erro", "Nome de usuário já existe!")

    def _validate_inputs(self, username: str, password: str, confirm: str) -> bool:
        if len(username) < self.config.MIN_USERNAME_LENGTH:
            tk.messagebox.showerror("Erro", f"Nome de usuário muito curto (mínimo {self.config.MIN_USERNAME_LENGTH} caracteres)")
            return False
            
        if len(password) < self.config.MIN_PASSWORD_LENGTH:
            tk.messagebox.showerror("Erro", f"Senha muito curta (mínimo {self.config.MIN_PASSWORD_LENGTH} caracteres)")
            return False
            
        if password != confirm:
            tk.messagebox.showerror("Erro", "As senhas não coincidem")
            return False
            
        return True