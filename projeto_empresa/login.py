import tkinter as tk
from tkinter import messagebox
import logging
from dataclasses import dataclass
from db import UserDB, DatabaseConfig, AuthManager
from cadastro import Cadastro

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

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
    LISTBOX_BG: str = '#444444'
    LISTBOX_FG: str = '#FFFFFF'
    LISTBOX_HIGHLIGHT: str = '#666666'

class LoginScreen:
    def __init__(self, master: tk.Tk, db, config: AppConfig = AppConfig()):
        self.master = master
        self.config = config
        self.db = db
        self.auth = AuthManager(db)
        self._setup_window()
        self._create_widgets()
        self._setup_autocomplete()  # ADICIONAR ESTA LINHA
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
                self._on_login_success()
            else:
                self._show_error("Usuário ou senha inválidos")

        except Exception as e:
            logging.error(f"Erro no login: {str(e)}")
            self._show_error("Erro interno no sistema")

    def _show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)
        self.password_entry.delete(0, tk.END)

    def _on_login_success(self) -> None:
        messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
        self.master.destroy()

    def _toggle_password_visibility(self) -> None:
        show = self.show_password.get()
        self.password_entry.config(show="" if show else "*")

    def _hide_listbox(self, event=None):
        if not self.username_entry.cget('state') == 'disabled':
            self.users_listbox.grid_remove()

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