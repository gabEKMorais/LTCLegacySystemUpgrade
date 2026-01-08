import datetime
import os
import tempfile
from fpdf import FPDF
from config import *
from extras import dividir_string
from app_pdf_view import app_pdf_view

HEIGH_LINHA_ITENS = 4

#   PDF ORÇAMENTO
class PDF_ORC(FPDF):
    def header(self):
        self.image('logo.png', 10, 0, 33)
        self.set_font('Arial', 'B', 15) 
        w = self.get_string_width(title) + 6 
        self.set_x((210 - w) / 2) 
        self.set_text_color(PRETO)
        self.cell(w, 9, title, 0, 1, 'C', 0)
        self.ln(0) 
        self.set_font('Arial', 'B', 15) 
        self.set_text_color(CINZA) 
        adendoFrase = "Válido para a presente data!"
        w = self.get_string_width(adendoFrase) + 6
        self.set_x((210 - w) / 2)
        self.cell(w, 9, adendoFrase, 0, 1, 'C', 0) 
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 10, "LTC TECNOLOGIA - LUIZ VOLKART, 35, CENTRO , TRÊS COROAS/RS", 0, 1, 'C', 1)

    def chapter_title_orc(self, txt):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, txt, 0, 1, 'L', 1)
        self.ln(4)
    def chapter_orc_fixo(self, array, total_orc):
        self.set_font('Times', '', 12)
        self.set_fill_color(FUNDO_TEXTO_ITENS)
        fill_option = False
        for item in array:
            if (fill_option):
                fill_option = False
            else:
                fill_option = True
            item0 = str(item.nome)
            item1 = str(item.un)
            item2 = str(f"{float(item.valor):.2f}").replace('.',',')
            item3 = str(f"{float(item.total):.2f}").replace('.',',')
            w1 = len(item1)
            w2 = len(item2)
            w3 = len(item3)
            if len(item0) <= 36:
                self.cell((114-w1), HEIGH_LINHA_ITENS, item0, 0, 0,'',fill_option)
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)
                self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item2}", 0, 0,'',fill_option)
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item3}", 0, 1,'',fill_option)
                self.ln(2) 
            else:
                item0Parte1, item0Parte2 = dividir_string(item0, 36)
                self.cell((114-w1), HEIGH_LINHA_ITENS, item0Parte1, 0, 0,'',fill_option)           
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)                
                self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item2}", 0, 0,'',fill_option)
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item3}", 0, 1,'',fill_option)
                self.ln(1) 
                if (item0Parte2):
                    self.cell(0, HEIGH_LINHA_ITENS, item0Parte2, 0, 1,'',fill_option)
                    self.ln(2)
        self.ln(5)
        self.set_font('Times', '', 16)
        self.cell((160), HEIGH_LINHA_ITENS, "Total", 0, 0, 'R')
        self.cell(0, HEIGH_LINHA_ITENS, f"R${total_orc}", 0, 1, 'R')
        self.ln(2)
    def chapter_orc(self, array):
        self.set_font('Times', '', 12)
        self.set_fill_color(FUNDO_TEXTO_ITENS)
        fill_option = False
        for item in array:
            if (fill_option):
                fill_option = False
            else:
                fill_option = True
            item0 = str(item.nome)
            item1 = "1"
            item2 = str(f"{float(item.valor):.2f}").replace('.',',')
            w1 = len(item1)
            w2 = len(item2)
            if len(item0) <= 36:
                self.cell((114-w1), HEIGH_LINHA_ITENS, item0, 0, 0,'',fill_option)
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)                
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item2}", 0, 1,'',fill_option)
                self.ln(2) 
            else:
                item0Parte1, item0Parte2 = dividir_string(item0, 36)
                self.cell((114-w1), HEIGH_LINHA_ITENS, item0Parte1, 0, 0,'',fill_option)
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)                
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item2}", 0, 1,'',fill_option)
                self.ln(1) 
                if (item0Parte2):
                    self.cell(0, HEIGH_LINHA_ITENS, item0Parte2, 0, 1,'',fill_option)
                    self.ln(2)
        self.ln(5)  
    def print_chapter_orc_fixo(self, txt, array, total_orc):
        self.chapter_title_orc(txt)
        self.chapter_orc_fixo(array, total_orc)
    def print_chapter_orc(self, txt, array):
        self.chapter_title_orc(txt)
        self.chapter_orc(array)    
def cria_pdf_orcamento(page_master, orcamento):
    pdf = PDF_ORC()
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    global title
    title = 'LTC TECNOLOGIA ORÇAMENTO   ' + current_date # define o título
    pdf.set_title(title) # define o título do objeto PDF
    pdf.set_author('LTC TECNOLOGIA') # define o autor do objeto PDF
    pdf.add_page()
    texto_itens1 = "Produto                                                                           Quantidade            Valor(un)               Total"
    texto_itens2 = "Produto De Acordo Com a Instalação                            Quantidade            Valor(un)"
    texto_servicos = "Mão de Obra                                                                   Quantidade            Valor(un)"
    cha1_array = []
    cha2_array = []
    cha3_array = []
    valor_final = 0
    for produto in orcamento.array_produtos:
        if not (produto.remove):
            if (produto.fixo):
                cha1_array.append(produto)
                valor_final += produto.total
            else:
                cha2_array.append(produto)
    for servico in orcamento.array_services:
        if not (servico.remove):
            cha3_array.append(servico)
    valor_final = str(f"{float(valor_final):.2f}").replace('.',',')
    if (cha1_array):
        pdf.print_chapter_orc_fixo(texto_itens1, cha1_array, valor_final)
    if (cha2_array):
        pdf.print_chapter_orc(texto_itens2, cha2_array)
    if (orcamento.array_services):
        pdf.print_chapter_orc(texto_servicos,cha3_array)
    exibir_pdf(pdf, page_master)
 
#   FUNÇÕES PARA ARQUIVO TEMPORARIO E INSTANCIAMENTO COM TKINTER
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
    excluir_pdf_temporario(nome_arquivo_temporario)
    pdf_view_instance.destroy()
