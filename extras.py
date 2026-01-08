from tkinter import ttk
import os
import tempfile
from app_pdf_view import app_pdf_view

#   MANIPULAÇÃO DE DADOS - DIVISÃO STRING GRANDE
def dividir_string(texto, tamanho_maximo):
    palavras = texto.split()
    parte1 = []
    tamanho_atual = 0
    for palavra in palavras:
        if tamanho_atual + len(palavra) + 1 <= tamanho_maximo:
            parte1.append(palavra)
            tamanho_atual += len(palavra) + 1  # +1 para incluir o espaço
        else:
            break
    parte1 = ' '.join(parte1)
    parte2 = ' '.join(palavras[len(parte1.split()):])
    return parte1, parte2

#   WIDGET TKINTER
class EntryComTextoInicial(ttk.Entry):
    def __init__(self, master=None, texto_inicial="Digite aqui...", **kwargs):
        super().__init__(master, **kwargs)
        self.texto_inicial = texto_inicial
        self.inserir_texto_inicial()
        self.bind("<FocusIn>", self.limpar_texto)

    def inserir_texto_inicial(self):
        self.insert(0, self.texto_inicial)

    def limpar_texto(self, *args):
        self.delete(0, "end")
        self.unbind("<FocusIn>") # remove o bind para que nao execute novamente.

#   CENTRALIZA TELA TKINTER
def centralizar_tela_app(app):
    app.update_idletasks()
    largura = app.winfo_width()
    altura = app.winfo_height()
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    return app.geometry(f"+{x}+{y}")

#   FUNÇÕES PARA ARQUIVO TEMPORARIO E PDF_VIEW
def exibir_pdf(pdf, page_master):
    try:
        nome_arquivo_temporario = criar_pdf_temporario_fpdf(pdf)
        pdf_view_instance = app_pdf_view(page_master,nome_arquivo_temporario)
        pdf_view_instance.protocol("WM_DELETE_WINDOW", lambda: ao_fechar_janela(pdf_view_instance, nome_arquivo_temporario))
        pdf_view_instance.mainloop()
    except Exception as e:
            print (f"Erro ao criar instancia: {e}")
def criar_pdf_temporario_fpdf(pdf):
    conteudo_pdf = pdf.output(dest='S') # Obter a saída em bytes
    arquivo_temporario = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    arquivo_temporario.write(conteudo_pdf)
    arquivo_temporario.close()
    return arquivo_temporario.name
def excluir_pdf_temporario(nome_arquivo):
    try:
        os.remove(nome_arquivo)
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado.")
def ao_fechar_janela(pdf_view_instance, nome_arquivo_temporario):
    pdf_view_instance.destroy()
    excluir_pdf_temporario(nome_arquivo_temporario)
