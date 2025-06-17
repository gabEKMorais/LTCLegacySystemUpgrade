import tkinter as tk
from tkinter import ttk
import fitz

from extras import EntryComTextoInicial

class app_pdf_view(tk.Toplevel):
    def __init__(self, master, pdf_image):
        super().__init__(master)
        self.pdf_image = pdf_image
        self.title("Exibidor PDF") 
        try:
            # Exibe as imagens em uma janela Tkinter
            self.indice = 0
            self.label_imagem = ttk.Label(self)
            self.label_imagem.config(image = self.pdf_image[self.indice])
            self.label_imagem.image = self.pdf_image[self.indice]
            #   BOTOES E WIDGETS WHATS
            self.frame_botoes = ttk.Frame(self)
            self.frame_botoes.pack() # ocupa as duas colunas
            self.botao_anterior = ttk.Button(self.frame_botoes, text="Página Anterior", command=self.atualiza_imagem_1)
            self.botao_proximo = ttk.Button(self.frame_botoes, text="Próxima Página", command=self.atualiza_imagem_0)
            self.botao_whats = ttk.Button(self.frame_botoes, text="Enviar para Whats")
            self.entry = EntryComTextoInicial(self.frame_botoes, texto_inicial="Digite o número")
            if (len(self.pdf_image) > 1):
                self.botao_anterior.pack(side="left", padx=10)
                #self.entry.pack(side="left", padx=10)
                #self.botao_whats.pack(side="left", padx=10)
                self.botao_proximo.pack(side="left", padx=10)
            #else:
                #self.entry.pack(side="left", padx=10)
                #self.botao_whats.pack(side="left", padx=10)
            self.label_imagem.pack() 
        except Exception as e:
            print (f"Erro ao mostrar a pagina: {e}")
    def atualiza_imagem_0(self): # proxima
        self.indice += 1
        if (self.indice < len(self.pdf_image)):
            self.label_imagem.config(image = self.pdf_image[self.indice])
            self.label_imagem.image = self.pdf_image[self.indice]
        else:
            self.indice = 0
            self.label_imagem.config(image = self.pdf_image[self.indice])
            self.label_imagem.image = self.pdf_image[self.indice]
        return self.update()
    def atualiza_imagem_1(self): # anterior
        self.indice -= 1
        if (self.indice >= 0):
            self.label_imagem.config(image = self.pdf_image[self.indice])
            self.label_imagem.image = self.pdf_image[self.indice]
        else:
            self.indice = len(self.pdf_image)-1
            self.label_imagem.config(image = self.pdf_image[self.indice])
            self.label_imagem.image = self.pdf_image[self.indice]
        return self.update()
