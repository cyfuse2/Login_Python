import tkinter as tk
from config import AppConfig, DatabaseConfig
from db import UserDB
from login import LoginScreen

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