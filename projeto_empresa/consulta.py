import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
from config import AppConfig
import sqlite3
from datetime import datetime

class ConsultaProdutos(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.config = AppConfig()
        
        self.title("Consulta de Produtos")
        self.geometry("800x400")
        self.configure(bg=self.config.BG_COLOR)
        self.resizable(True, True)
        
        self._create_widgets()
        self._carregar_produtos()

    def _create_widgets(self):
        frame = tk.Frame(self, bg=self.config.BG_COLOR)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Treeview para exibir os produtos
        self.tree = ttk.Treeview(
            frame,
            columns=('ID', 'Nome', 'Quantidade', 'Preço', 'Data Cadastro'),
            show='headings',
            selectmode='browse'
        )

        # Configurar colunas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Quantidade', text='Quantidade')
        self.tree.heading('Preço', text='Preço Unitário (R$)')
        self.tree.heading('Data Cadastro', text='Data Cadastro')

        # Ajustar largura das colunas
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Nome', width=200, anchor='w')
        self.tree.column('Quantidade', width=100, anchor='center')
        self.tree.column('Preço', width=150, anchor='e')
        self.tree.column('Data Cadastro', width=150, anchor='center')

        # Scrollbar
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        # Layout
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    def _carregar_produtos(self):
        try:
            produtos = self.db.get_all_products()
            print(f"\n Número de produtos encontrados: {len(produtos)}")
            
            self.tree.delete(*self.tree.get_children())
            
            for produto in produtos:
                print(f"Processando produto: {produto}")
                
                try:
                    # Acesse os campos por índice numérico
                    id_produto = produto[0]
                    nome = produto[1]
                    quantidade = produto[2]
                    preco = produto[3]
                    data_cadastro = produto[4]
                    
                    # Formate os dados
                    data = datetime.strptime(data_cadastro, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                    preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                    
                    # Insira na treeview
                    self.tree.insert('', 'end', values=(
                        id_produto,
                        nome,
                        quantidade,
                        preco_formatado,
                        data
                    ))
                    
                except Exception as e:
                    print(f"Erro ao processar produto {produto}: {str(e)}")
                    logging.error(f"Erro no processamento: {str(e)}")

        except Exception as e:
            print(f" Erro geral: {str(e)}")
            logging.error(f"Erro na consulta: {str(e)}")
            tk.messagebox.showerror("Erro", "Falha ao carregar dados")