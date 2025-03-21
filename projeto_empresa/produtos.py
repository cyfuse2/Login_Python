import tkinter as tk
from tkinter import messagebox
import logging
from config import AppConfig

class CadastroProduto(tk.Toplevel):
    def __init__(self, master, db):  # Corrigido
        super().__init__(master)
        self.db = db
        self.config = AppConfig()
        
        self.title("Cadastro de Produtos")
        self.geometry("400x300")
        self.configure(bg=self.config.BG_COLOR)
        self.resizable(False, False)
        
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        frame = tk.Frame(self, bg=self.config.BG_COLOR)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        tk.Label(
            frame,
            text="Cadastro de Produtos",
            bg=self.config.BG_COLOR,
            fg=self.config.TEXT_COLOR,
            font=(self.config.FONT, self.config.TITLE_FONT_SIZE)
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Campos do formulário
        tk.Label(frame, text="Nome:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=1, column=0, pady=5, sticky='e')
        self.nome_entry = tk.Entry(frame)
        self.nome_entry.grid(row=1, column=1, pady=5, sticky='ew')

        tk.Label(frame, text="Quantidade:", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=2, column=0, pady=5, sticky='e')
        self.quantidade_entry = tk.Entry(frame)
        self.quantidade_entry.grid(row=2, column=1, pady=5, sticky='ew')

        tk.Label(frame, text="Preço (R$):", bg=self.config.BG_COLOR, fg=self.config.TEXT_COLOR).grid(row=3, column=0, pady=5, sticky='e')
        self.preco_entry = tk.Entry(frame)
        self.preco_entry.grid(row=3, column=1, pady=5, sticky='ew')

        # Botão de cadastro
        tk.Button(
            frame,
            text="Salvar Produto",
            command=self._salvar_produto,
            bg=self.config.BUTTON_BG,
            fg=self.config.TEXT_COLOR
        ).grid(row=4, column=0, columnspan=2, pady=15)

    def _bind_events(self):
        self.bind('<Return>', lambda event: self._salvar_produto())

    def _salvar_produto(self, event=None):
        try:
            nome = self.nome_entry.get().strip()
            quantidade = self.quantidade_entry.get().strip()
            preco = self.preco_entry.get().strip()

            if not self._validar_campos(nome, quantidade, preco):
                return

            # Converter para tipos numéricos
            quantidade = int(quantidade)
            preco = float(preco)

            if self.db.register_product(nome, quantidade, preco):
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
                self.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar produto")

        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos")
        except Exception as e:
            logging.error(f"Erro no cadastro: {str(e)}")
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")

    def _validar_campos(self, nome: str, quantidade: str, preco: str) -> bool:
        if not nome:
            messagebox.showerror("Erro", "Nome do produto é obrigatório")
            return False
            
        if not quantidade.isdigit() or int(quantidade) < 0:
            messagebox.showerror("Erro", "Quantidade inválida")
            return False
            
        try:
            if float(preco) <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido")
            return False
            
        return True