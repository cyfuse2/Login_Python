from dataclasses import dataclass

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

@dataclass
class DatabaseConfig:
    DB_NAME: str = "users.db"
    TABLE_NAME: str = "users"
    MIN_USERNAME_LENGTH: int = 3
    MIN_PASSWORD_LENGTH: int = 5