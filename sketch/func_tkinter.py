import tempfile
import os
import fitz
from PIL import Image, ImageTk
import tkinter as tk

from pdf import cria_pdf_orcamento

# EXIBE PDF EM NOVA JANELA
def exibir_pdf_orçamento(page, itens_array, services_array): # total_orc, itens, cliente, id_orc
    try:
        pdf_dados = cria_pdf_orcamento(itens_array, services_array, 0)
    except Exception as e:
        print (f"Erro ao criar PDF: {e}")
    try:
            # Gerando nova janela para mostrar pdf
            pdf_view = tk.Toplevel(page)  # Cria a nova janela
            pdf_view.title("Exibidor PDF")  # Define o título da nova janela
            # Adicione widgets à nova janela, se necessário
            label = tk.Label(pdf_view, text="Conteúdo da nova janela")
            label.pack()
            # Cria um arquivo temporário
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_filename = os.path.join(temp_file.name)
                # Escreva o conteúdo do PDF no arquivo temporário
                temp_file.write(pdf_dados.getvalue())
            print("2", temp_filename)
            # Abre o arquivo temporário com PyMuPDF
            doc = fitz.open(temp_filename)

            page = doc[0]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
            # Deleta o arquivo temporário
            doc.close()
            os.remove(temp_filename)
            
    except Exception as e:
        print(f"Erro ao exibir PDF: {e}")