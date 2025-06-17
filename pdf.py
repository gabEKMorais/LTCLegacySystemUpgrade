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
    
#   PDF RELATORIO OS
class PDF_REL(FPDF):
    def header(self):
        self.image('logo.png', 10, 0, 33)
        self.set_font('Arial', 'B', 15) 
        w = self.get_string_width(title) + 6 
        self.set_x((210 - w) / 2) 
        self.set_text_color(PRETO)
        self.cell(w, 9, title, 0, 1, 'C', 0)
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 10, "LTC TECNOLOGIA - LUIZ VOLKART, 35, CENTRO , TRÊS COROAS/RS", 0, 1, 'C', 1)
    def chapter_body_title(self, text):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, text, 0, 1, 'C', 1)
        self.ln(4)

    def chapter_title(self, num_os, problema):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, ("OS: "+str(num_os)), 0, 1, 'C', 1)
        self.ln(4)
        self.cell(0, HEIGH_LINHA_ITENS, "Serviço Solicitado:", 0, 1, 'C')
        self.ln(1)
        self.multi_cell(0, HEIGH_LINHA_ITENS, problema)
        self.ln(4)
    def chapter_body(self, obj, texto_itens, texto_servicos):
        self.set_font('Times', '', 12)
        fill_option = False
        if (obj.array_produtos):
            self.chapter_body_title(texto_itens)
        self.set_fill_color(FUNDO_TEXTO_ITENS)
        for item in obj.array_produtos: # nome, cod, un, valor
            if (fill_option):
                fill_option = False
            else:
                fill_option = True
            item_nome = str(item.nome)
            item_un = str(int(item.un))
            w1 = len(item_un)
            item_valor = str(f"{float(item.valor):.2f}").replace('.',',')
            w2 = len(item_valor)
            item_total = str(f"{float(item.total):.2f}").replace('.',',')
            w3 = len(item_total)
            if len(item_nome) <= 36:
                self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome, 0, 0,'',fill_option)
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                self.ln(2) 
            else:
                item_nome_parte1, item_nome_parte2 = dividir_string(item_nome, 36)
                if (len(item_nome_parte2) > 0):
                    self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                    self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                    self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                    self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                    self.ln(1) 
                    self.cell(0, HEIGH_LINHA_ITENS, item_nome_parte2, 0, 1,'',fill_option)
                    self.ln(2)
                else:
                    self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                    self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                    self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                    self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                    self.ln(2) 
        self.ln(5)
        if (obj.detalha_servicos):
            if (obj.array_servicos):
                self.chapter_body_title(texto_servicos)
            self.set_fill_color(FUNDO_TEXTO_ITENS)
            for item in obj.array_servicos: # nome, cod, un, valor
                if (fill_option):
                    fill_option = False
                else:
                    fill_option = True
                item_nome = str(item.nome)
                item_un = str(int(item.un))
                w1 = len(item_un)
                self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome, 0, 0,'',fill_option)
                item_valor = str(f"{float(item.valor):.2f}").replace('.',',')
                w2 = len(item_valor)
                self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                item_total = str(f"{float(item.total):.2f}").replace('.',',')
                w3 = len(item_total)
                self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                self.ln(2) 
        else:
            total_serv = 0
            for item in obj.array_servicos: # nome, cod, un, valor
                total_serv += item.total
            if (total_serv > 0):
                if (fill_option):
                    fill_option = False
                else:
                    fill_option = True
                total_serv = str(f"{float(total_serv):.2f}").replace('.',',')
                self.cell(0, 6, (f"Total Mão de Obra    R${total_serv}"), 0, 1, 'C', fill_option)
                self.ln(4)  
        self.ln(5)
        self.set_font('Times', '', 16)
        self.cell((160), HEIGH_LINHA_ITENS, "Total", 0, 0, 'R')
        self.cell(0, HEIGH_LINHA_ITENS, f"R${(obj.valor_total_os):.2f}", 0, 1, 'R')
        self.ln(2) 
    def print_chapter(self, obj, texto_itens, texto_servicos):
        self.add_page()
        self.chapter_title(obj.os, obj.problema)
        self.chapter_body(obj, texto_itens, texto_servicos)

    def chapter_title_unificado(self, os, problema):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.multi_cell(0, 6, os, 0, 'C', 1)
        self.ln(4)
        self.cell(0, HEIGH_LINHA_ITENS, "Serviço Solicitado:", 0, 1, 'C')
        self.ln(1)
        self.multi_cell(0, HEIGH_LINHA_ITENS, problema.upper())
        self.ln(4)
    def chapter_servico_det_title(self, os, text):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, ("OS: "+os), 0, 1, 'C', 1)
        self.cell(0, 6, text, 0, 1, 'C', 1)
        self.ln(4)
    def print_chapter_unificado(self, array_produtos, array_servicos, detalha_servicos, total_geral, texto_itens, texto_servicos):
        tem_produto = False
        for array in array_produtos:
            if (array):
                tem_produto = True
        if (tem_produto):
            self.chapter_body_title(texto_itens)
            fill_option = False
            self.set_fill_color(FUNDO_TEXTO_ITENS)
            for array in array_produtos:
                for item in array:
                    if (fill_option):
                        fill_option = False
                    else:
                        fill_option = True
                    item_nome = str(item.nome)
                    item_un = str(int(item.un))
                    w1 = len(item_un)
                    item_valor = str(f"{float(item.valor):.2f}").replace('.',',')
                    w2 = len(item_valor)
                    item_total = str(f"{float(item.total):.2f}").replace('.',',')
                    w3 = len(item_total)
                    if len(item_nome) <= 36:
                        self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome, 0, 0,'',fill_option)
                        self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                        self.ln(2) 
                    else:
                        item_nome_parte1, item_nome_parte2 = dividir_string(item_nome, 36)
                        if (len(item_nome_parte2) > 0):
                            self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                            self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                            self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                            self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                            self.ln(1) 
                            self.cell(0, HEIGH_LINHA_ITENS, item_nome_parte2, 0, 1,'',fill_option)
                            self.ln(2)
                        else:
                            self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                            self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                            self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                            self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                            self.ln(2) 
            self.ln(5)
        else:
            fill_option = False
        if (detalha_servicos):
            for array in array_servicos:
                if(len(array[1]) > 0):
                    self.chapter_servico_det_title(array[0], texto_servicos)
                    fill_option = False
                    self.set_fill_color(FUNDO_TEXTO_ITENS)
                    for item in array[1]:
                        if (fill_option):
                            fill_option = False
                        else:
                            fill_option = True
                        item_nome = str(item.nome)
                        item_un = str(int(item.un))
                        w1 = len(item_un)
                        item_valor = str(f"{float(item.valor):.2f}").replace('.',',')
                        w2 = len(item_valor)
                        item_total = str(f"{float(item.total):.2f}").replace('.',',')
                        w3 = len(item_total)
                        self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome, 0, 0,'',fill_option)
                        self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                        self.ln(5) 
        else:
            total_serv = 0
            for array in array_servicos: # nome, cod, un, valor
                for array_sec in array[1]:
                    total_serv += array_sec.total
            if (total_serv > 0):
                if (fill_option):
                    fill_option = False
                else:
                    fill_option = True
                total_serv = str(f"{float(total_serv):.2f}").replace('.',',')
                self.cell(0, 6, (f"Total Mão de Obra    R${total_serv}"), 0, 1, 'C', fill_option)
                self.ln(4)  
        self.ln(5)
        self.set_font('Times', '', 16)
        self.cell((160), HEIGH_LINHA_ITENS, "Total", 0, 0, 'R')
        self.cell(0, HEIGH_LINHA_ITENS, f"R${(total_geral):.2f}", 0, 1, 'R')
        self.ln(2) 
def cria_pdf_relatorio(rel_array, var_unifica, var_unifica_detalha, txt_detalha, page_master):
    pdf = PDF_REL()
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    global title
    title = 'LTC TECNOLOGIA RELATÓRIO DE OS  ' + current_date # define o título
    pdf.set_title(title) # define o título do objeto PDF
    pdf.set_author('LTC TECNOLOGIA') # define o autor do objeto PDF
    texto_itens = "Produto                                                                           Quantidade            Valor(un)               Total"
    texto_servicos = "Mão de Obra                                                                   Quantidade            Valor(un)               Total"
    #   PARA OS UNIFICADAS
    if (var_unifica):
        pdf.add_page()
        os_str = "OS: "
        total_geral = 0
        array_produtos = []
        array_servicos = []
        for obj in rel_array:
            os_str = os_str+"-"+str(obj.os)+" "
            total_geral += obj.valor_total_os
            array_produtos.append(obj.array_produtos)
            array_servicos.append([obj.os, obj.array_servicos])
        pdf.chapter_title_unificado(os_str, txt_detalha)
        pdf.print_chapter_unificado(array_produtos, array_servicos, var_unifica_detalha, total_geral, texto_itens, texto_servicos)
    #   PARA OS INDIVIDUAIS
    else:
        for obj in rel_array:
            pdf.print_chapter(obj, texto_itens, texto_servicos)
    exibir_pdf(pdf, page_master)

#   PDF RELATORIO PEDIDO
class PDF_REL_PED(FPDF):
    def header(self):
        self.image('logo.png', 10, 0, 33)
        self.set_font('Arial', 'B', 15) 
        w = self.get_string_width(self.title) + 6 
        self.set_x((210 - w) / 2) 
        self.set_text_color(PRETO)
        self.cell(w, 9, self.title[0:14], 0, 1, 'C', 0)
        self.cell(0, 9, self.title[14:], 0, 1, 'C', 0)
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 10, "LTC TECNOLOGIA - LUIZ VOLKART, 35, CENTRO , TRÊS COROAS/RS", 0, 1, 'C', 1)
    def chapter_title(self, num_ped):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.multi_cell(0, 6, num_ped, 0, 'C', 1)
        self.ln(4)
    def chapter_body_title(self, text):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, text, 0, 1, 'C', 1)
        self.ln(4)
    def chapter_body(self, array_pai, valor_final):
        self.set_font('Times', '', 12)
        fill_option = False
        self.set_fill_color(FUNDO_TEXTO_ITENS)
        for array in array_pai:
            for item in array: # nome, cod, un, valor
                if (fill_option):
                    fill_option = False
                else:
                    fill_option = True
                item_nome = str(item.nome)
                item_un = str(int(item.un))
                w1 = len(item_un)
                item_valor = str(f"{float(item.valor):.2f}").replace('.',',')
                w2 = len(item_valor)
                item_total = str(f"{float(item.total):.2f}").replace('.',',')
                w3 = len(item_total)
                if len(item_nome) <= 36:
                    self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome, 0, 0,'',fill_option)
                    self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                    self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                    self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                    self.ln(2) 
                else:
                    item_nome_parte1, item_nome_parte2 = dividir_string(item_nome, 36)
                    if (len(item_nome_parte2) > 0):
                        self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                        self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                        self.ln(1) 
                        self.cell(0, HEIGH_LINHA_ITENS, item_nome_parte2, 0, 1,'',fill_option)
                        self.ln(2)
                    else:
                        self.cell((114-w1), HEIGH_LINHA_ITENS, item_nome_parte1, 0, 0,'',fill_option)
                        self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item_un, 0, 0,'',fill_option)
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item_valor}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item_total}", 0, 1,'',fill_option)
                        self.ln(2) 
        self.ln(5)
        self.set_font('Times', '', 16)
        self.cell((160), HEIGH_LINHA_ITENS, "Total", 0, 0, 'R')
        self.cell(0, HEIGH_LINHA_ITENS, f"R${(valor_final):.2f}", 0, 1, 'R')
        self.ln(2) 
    def print_chapter(self, array, texto_itens, valor_final):
        self.chapter_body_title(texto_itens)
        self.chapter_body(array, valor_final)

def cria_pdf_relatorio_pedido(page_master):
    pdf = PDF_REL_PED()
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    pdf.title = 'LTC TECNOLOGIA RELATÓRIO DE PEDIDO(S)  ' + current_date # define o título
    pdf.set_title(pdf.title) # define o título do objeto PDF
    pdf.set_author('LTC TECNOLOGIA') # define o autor do objeto PDF
    pdf.add_page()
    texto_itens = "Item                                                                             Quantidade            Valor(un)               Total"
    if(page_master.checkbox_unificar.get()):
        texto_pedido = "Pedido(s): "
        valor_final = 0
        array_itens = []
        for pedido in page_master.pedidos_carregados:
            texto_pedido = texto_pedido+"-"+str(pedido.id)+" "
            valor_final += pedido.valor_total_ped
            array_itens.append(pedido.array_itens)
        pdf.chapter_title(texto_pedido)
        pdf.print_chapter(array_itens, texto_itens, valor_final)
    else:
        for pedido in page_master.pedidos_carregados:
            texto_pedido = "Pedido: " + str(pedido.id)
            pdf.chapter_title(texto_pedido)
            pdf.print_chapter([pedido.array_itens], texto_itens, pedido.valor_total_ped)
    exibir_pdf(pdf, page_master.page_master)

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
