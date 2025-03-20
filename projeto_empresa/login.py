import tkinter as tk
from tkinter import messagebox
import logging
from config import AppConfig
from db import AuthManager
from cadastro import Cadastro
from menu import MainMenu

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

class LoginScreen:
    def __init__(self, master: tk.Tk, db, config: AppConfig = AppConfig()):
        self.master = master
        self.config = config
        self.db = db
        self.auth = AuthManager(db)
        self._setup_window()
        self._create_widgets()
        self._setup_autocomplete()
        self._bind_events()

    def _setup_window(self) -> None:
        self.master.title(self.config.WINDOW_TITLE)
        self.master.geometry(self.config.WINDOW_SIZE)
        self.master.configure(bg=self.config.BG_COLOR)
        self.master.resizable(False, False)

    def _setup_autocomplete(self):
        self.username_entry.bind('<KeyRelease>', self._update_users_list)
        self.username_entry.bind('<FocusOut>', self._hide_listbox)
        self.users_listbox.bind('<<ListboxSelect>>', self._select_user_from_list)

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
            text="Empresa:",
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
        self.username_entry.grid(row=1, column=1, pady=5, sticky='ew')

        self.password_entry = tk.Entry(self.frame, show="*", font=(self.config.FONT, self.config.FONT_SIZE))
        self.password_entry.grid(row=2, column=1, pady=5, sticky='ew')

        self.users_listbox = tk.Listbox(
            self.frame,
            height=4,
            bg=self.config.LISTBOX_BG,
            fg=self.config.LISTBOX_FG,
            selectbackground=self.config.LISTBOX_HIGHLIGHT,
            font=(self.config.FONT, self.config.FONT_SIZE-2)
        )
        self.users_listbox.grid(row=3, column=1, sticky='nsew', padx=5, pady=2)
        self.users_listbox.grid_remove()

    def _update_users_list(self, event=None):
        search_term = self.username_entry.get().strip()
        print(f"Termo buscado: '{search_term}'")
        
        users = self.db.search_users(search_term)
        print(f"Usuários encontrados: {users}")
        
        self.users_listbox.delete(0, tk.END)
        
        if search_term and users:
            for user in users:
                self.users_listbox.insert(tk.END, user)
            self.users_listbox.grid()
        else:
            self.users_listbox.grid_remove()

    def _select_user_from_list(self, event):
        if self.users_listbox.curselection():
            index = self.users_listbox.curselection()[0]
            value = self.users_listbox.get(index)
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, value)
            self.users_listbox.grid_remove()

    def _create_buttons(self) -> None:
        btn_frame = tk.Frame(self.frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)  # Alterado para row=4
        
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
        ).grid(row=5, column=0, columnspan=2, pady=5)

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
                # CORREÇÃO AQUI: passar o username como parâmetro
                self._on_login_success(username)  # ← Adicionado o parâmetro
            else:
                self._show_error("Usuário ou senha inválidos")

        except Exception as e:
            logging.error(f"Erro no login: {str(e)}")
            self._show_error("Erro interno no sistema")

    def _show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)
        self.password_entry.delete(0, tk.END)

    def _on_login_success(self, username: str) -> None:
        messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
        self.master.withdraw()  # Esconde a janela de login
        MainMenu(self.master, username)  # Abre o menu principal

    def _toggle_password_visibility(self) -> None:
        show = self.show_password.get()
        self.password_entry.config(show="" if show else "*")

    def _hide_listbox(self, event=None):
        if not self.username_entry.cget('state') == 'disabled':
            self.users_listbox.grid_remove()

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
                font=(self.config.FONT, self.config.FONT_SIZE)  # Adicionei o parêntese faltante
            )
            btn.pack(pady=10, padx=10, side='top')  # Removi o parêntese extra

    def _open_cadastro(self):
        messagebox.showinfo("Cadastro", "Funcionalidade de cadastro em desenvolvimento!")

    def _open_consulta(self):
        messagebox.showinfo("Consulta", "Funcionalidade de consulta em desenvolvimento!")

    def _open_relatorio(self):
        messagebox.showinfo("Relatório", "Funcionalidade de relatório em desenvolvimento!")

    def _on_close(self):
        self.master.destroy()  # Fecha completamente a aplicação