import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import fitz

class app_pdf_view(tk.Toplevel):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.pdf_path = pdf_path
        doc = fitz.open(self.pdf_path)
        paginas = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            paginas.append(ImageTk.PhotoImage(img))  # Adiciona a imagem à lista
        self.pdf_image = paginas
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
            self.botao_imprime = ttk.Button(self.frame_botoes, text="IMPRIMIR", command=self.imprimir_pdf)
            self.botao_salvar = ttk.Button(self.frame_botoes, text="SALVAR PDF", command=self.salvar_pdf)
            if (len(self.pdf_image) > 1):
                self.botao_anterior.pack(side="left", padx=10)
                self.botao_imprime.pack(side="left", padx=10)
                self.botao_salvar.pack(side="left", padx=10)
                self.botao_proximo.pack(side="left", padx=10)
            else:
                self.botao_imprime.pack(side="left", padx=10)
                self.botao_salvar.pack(side="left", padx=10)
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
    def imprimir_pdf(self):
        try:
            caminho_pdf_abs = os.path.abspath(self.pdf_path)
            os.startfile(caminho_pdf_abs, "print")  # Inicia a impressão no Windows
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_pdf_abs}")
        except Exception as e:
            print(f"Ocorreu um erro ao imprimir o PDF: {e}")
    def salvar_pdf(self):
        caminho_destino = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho_destino:
            try:
                shutil.copy2(self.pdf_path, caminho_destino)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o arquivo: {e}")