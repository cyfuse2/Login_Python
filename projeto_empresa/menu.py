import tkinter as tk
from tkinter import messagebox
from config import AppConfig

class MainMenu(tk.Toplevel):
    def __init__(self, master, username: str):
        super().__init__(master)
        self.username = username
        self.config = AppConfig()
        self._setup_window()
        self._create_widgets()
        
    def _setup_window(self):
        self.title("Sistema de Gestão")
        self.geometry("600x400")
        self.configure(bg=self.config.BG_COLOR)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        # Cabeçalho
        header_frame = tk.Frame(self, bg=self.config.BG_COLOR)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text=f"Bem-vindo, {self.username}",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR,
            font=(self.config.FONT, self.config.TITLE_FONT_SIZE)
        ).pack(side='left')

        # Botões principais
        buttons_frame = tk.Frame(self, bg=self.config.BG_COLOR)
        buttons_frame.pack(expand=True)

        buttons = [
            ("Cadastrar", self._open_cadastro),
            ("Consulta", self._open_consulta),
            ("Relatório", self._open_relatorio),
            ("Sair", self._on_close)
        ]

        for text, command in buttons:
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                width=15,
                height=2,
                bg=self.config.BUTTON_BG,
                fg=self.config.TEXT_COLOR,
                font=(self.config.FONT, self.config.FONT_SIZE)
            )
            btn.pack(pady=10, padx=10, side='top')

    def _open_cadastro(self):
        messagebox.showinfo("Cadastro", "Funcionalidade de cadastro em desenvolvimento!")

    def _open_consulta(self):
        messagebox.showinfo("Consulta", "Funcionalidade de consulta em desenvolvimento!")

    def _open_relatorio(self):
        messagebox.showinfo("Relatório", "Funcionalidade de relatório em desenvolvimento!")

    def _on_close(self):
        self.master.destroy()