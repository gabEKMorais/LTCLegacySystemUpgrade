import tkinter as tk
from config import *
from app_pdf_orcamento_class import app_pdf_orcamento
from app_relatorios import AppRelatorio
from app_vendas import AppVendas
from app_estoque import AppEstoque
from extras import centralizar_tela_app

# PROGRAMA PRINCIPAL
class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação Principal")
        self.geometry("1000x700")
        centralizar_tela_app(self)
        #   Menu para alternar entre as telas
        self.header = tk.Frame(self, bg=FUNDO_APP_PRINCIPAL_HEADER, pady = 10)
        self.header.pack(fill=tk.X, side=tk.TOP)
        #   Conteúdo do header (exemplo)
        self.label_app_vendas = tk.Label(self.header, text="VENDAS", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_vendas.pack(side=tk.LEFT, expand=True)
        self.label_app_vendas.bind("<Button-1>", self.abrir_app_vendas)
        self.label_app_estoque = tk.Label(self.header, text="ESTOQUE", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_estoque.pack(side=tk.LEFT, expand=True)
        self.label_app_estoque.bind("<Button-1>", self.abrir_app_estoque)
        self.label_app_pdf_orcamento = tk.Label(self.header, text="ORÇAMENTO", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_pdf_orcamento.pack(side=tk.LEFT, expand=True)
        self.label_app_pdf_orcamento.bind("<Button-1>", self.abrir_app_pdf_orcamento)
        self.label_app_relatorios = tk.Label(self.header, text="RELATÓRIOS", font=("Arial", 16), bg=FUNDO_APP_PRINCIPAL_HEADER)
        self.label_app_relatorios.pack(side=tk.LEFT, expand=True)
        self.label_app_relatorios.bind("<Button-1>", self.abrir_app_pdf_relatorio)
        #   APPS    
        self.app_pdf_orcamento_conteiner = app_pdf_orcamento(self, self.reinicia_app_orcamento)
        self.app_relatorios_conteiner = AppRelatorio(self, self.reinicia_app_relatorios)
        self.app_vendas_conteiner = AppVendas(self, self.reinicia_app_vendas)
        self.app_estoque_conteiner = AppEstoque(self, self.reinicia_app_estoque)
        #   INICIO COM VENDAS
        self.abrir_app_vendas("Click")

    def abrir_app_pdf_orcamento(self, event):
        try:
            self.reset_apps()
            self.app_pdf_orcamento_conteiner.pack(expand=True)
            self.label_app_pdf_orcamento["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao abrir modulo: {e}")
    def reinicia_app_orcamento(self):
        self.app_pdf_orcamento_conteiner.pack_forget()
        self.app_pdf_orcamento_conteiner = app_pdf_orcamento(self, self.reinicia_app_orcamento)
        return self.app_pdf_orcamento_conteiner.pack(expand=True)
    def abrir_app_pdf_relatorio(self, event):
        try:
            self.reset_apps()
            self.app_relatorios_conteiner.pack(expand=True)
            self.label_app_relatorios["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao abrir modulo: {e}")
    def reinicia_app_relatorios(self):
        self.app_relatorios_conteiner.pack_forget()
        self.app_relatorios_conteiner = AppRelatorio(self, self.reinicia_app_relatorios)
        return self.app_relatorios_conteiner.pack(expand=True)
    def abrir_app_vendas(self, event):
        try:
            self.reset_apps()
            self.app_vendas_conteiner.pack(expand=True)
            self.label_app_vendas["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao abrir modulo: {e}")    
    def reinicia_app_vendas(self):
        self.app_vendas_conteiner.pack_forget()
        self.app_vendas_conteiner = AppVendas(self, self.reinicia_app_vendas)
        return self.app_vendas_conteiner.pack(expand=True)
    def abrir_app_estoque(self, event):
        try:
            self.reset_apps()
            self.app_estoque_conteiner.pack(expand=True)
            self.label_app_estoque["bg"] = FUNDO_APP_PRINCIPAL_HEADER_SELECAO
        except Exception as e:
            print(f"Erro ao abrir modulo: {e}") 
    def reinicia_app_estoque(self):
        self.app_estoque_conteiner.pack_forget()
        self.app_estoque_conteiner = AppEstoque(self, self.reinicia_app_estoque)
        return self.app_estoque_conteiner.pack(expand=True)  
    def reset_apps(self):
        # tira apps tela
        self.app_pdf_orcamento_conteiner.pack_forget()
        self.app_relatorios_conteiner.pack_forget()
        self.app_vendas_conteiner.pack_forget()
        self.app_estoque_conteiner.pack_forget()

        self.label_app_pdf_orcamento["bg"] = FUNDO_APP_PRINCIPAL_HEADER
        self.label_app_relatorios["bg"] = FUNDO_APP_PRINCIPAL_HEADER
        self.label_app_vendas["bg"] = FUNDO_APP_PRINCIPAL_HEADER
        self.label_app_estoque["bg"] = FUNDO_APP_PRINCIPAL_HEADER

# CHAMADA DO PROGRAMA PRINCIPAL PARA INICIAR LOOP
if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()