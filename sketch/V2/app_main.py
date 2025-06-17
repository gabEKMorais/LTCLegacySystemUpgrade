import tkinter as tk
from tkinter import ttk

from config import *
from app_pdf_orcamento_class import app_pdf_orcamento
from app_pdf_relatorio_class import app_pdf_relatorio


# PROGRAMA PRINCIPAL
class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação Principal")
        self.geometry("800x500")
        self.centralizar_janela()

        # Menu para alternar entre as telas
        self.header = tk.Frame(self, bg=FUNDO_APP_PRINCIPAL_HEADER, pady = 10)
        self.header.pack(fill=tk.X, side=tk.TOP)
        # Conteúdo do header (exemplo)
        self.label_app_pdf_orcamento = tk.Label(self.header, text="GERAR ORÇAMENTO", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_pdf_orcamento.pack(side=tk.LEFT, expand=True)
        self.label_app_pdf_orcamento.bind("<Button-1>", self.abrir_app_pdf_orcamento)
        self.label_app_estoque = tk.Label(self.header, text="ESTOQUE", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_estoque.pack(side=tk.LEFT, expand=True)
        self.label_app_estoque.bind("<Button-1>", self.abrir_app_estoque)
        self.label_app_relatorio = tk.Label(self.header, text="GERAR RELATÓRIO", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_relatorio.pack(side=tk.LEFT, expand=True)
        self.label_app_relatorio.bind("<Button-1>", self.abrir_app_pdf_relatorio)
        # APPS    
        self.app_pdf_orcamento_conteiner = app_pdf_orcamento(self)
        self.app_pdf_relatorio_conteiner = app_pdf_relatorio(self)
       
    def abrir_app_pdf_orcamento(self, event):
        try:
            self.reset_apps()
            self.app_pdf_orcamento_conteiner.pack()
            self.label_app_pdf_orcamento["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")
    def abrir_app_estoque(self, event):
        try:
            self.reset_apps()
            self.label_app_estoque["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
            print("Estoque")
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")
    def abrir_app_pdf_relatorio(self, event):
        try:
            self.reset_apps()
            self.app_pdf_relatorio_conteiner.pack()
            self.label_app_relatorio["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")
    def reset_apps(self):
        # tira apps tela
        self.app_pdf_orcamento_conteiner.pack_forget()
        self.app_pdf_relatorio_conteiner.pack_forget()

        self.label_app_pdf_orcamento["bg"] = FUNDO_APP_PRINCIPAL_HEADER
        self.label_app_estoque["bg"] = FUNDO_APP_PRINCIPAL_HEADER
        self.label_app_relatorio["bg"] = FUNDO_APP_PRINCIPAL_HEADER

    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.geometry(f"+{x}+{y}")

# CHAMADA DO PROGRAMA PRINCIPAL PARA INICIAR LOOP
if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()