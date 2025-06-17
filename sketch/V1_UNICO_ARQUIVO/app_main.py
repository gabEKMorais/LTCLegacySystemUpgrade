#   IMPORTA LIBS NECESSÁRIAS
import datetime # PARA CONFIG DE DATAS, HORAS, ETC.
import io
import time # PARA CONFIGS DE SLEEP, ETC
import tempfile # PARA ARQUIVOS TEMPORARIOS
import os # PARA FUNÇÕES RELACIONADAS AO SISTEMA
import fitz
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import pyodbc # PARA DB ACESS
from fpdf import FPDF # PARA CRIAÇÃO DO PDF

#   CONFIG GLOBAL
#       - CORES UTILIZADAS
VERMELHO_PADRAO = [246, 19, 23]
AZUL_PADRAO = [89, 197, 207]
BRANCO = 255
PRETO = 0
CINZA = 128
FUNDO_TEXTO_ITENS = 220
#       - ACESSO AO DB
MDB = r'C:\Users\LTC\Desktop\gabe\PY\DBPARATESTE.MDB'
DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
CONN_STR = ';'.join(['DRIVER=' + DRV, 'DBQ=' + MDB])
#       - PARA CLASSES PDF
HEIGH_LINHA_ITENS = 4

#   FUNÇÕES EXTRAS QUE PODEM SER REUTILIZADAS
#       - MANIPULAÇÃO DE DADOS - DIVISÃO STRING GRANDE
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

#   CLASSE PARA BANCO DE DADOS
class ConectarDB:
    def __init__(self):
        # Criando conexão.
        self.con = pyodbc.connect(CONN_STR)
        # Criando cursor.
        self.cur = self.con.cursor()
    def consultar_cliente_orc(self, id_cliente):
        try:
            self.cur.execute(f'SELECT "Nome do cliente" FROM Clientes WHERE "Código do cliente" = {id_cliente}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []       
    def consultar_produto_orc(self, id_produto):
        try:
            self.cur.execute(f'SELECT "Descrição do produto" FROM Produtos WHERE "Código do produto" = {id_produto}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []    
    def consultar_orçamento_orc(self, id_orcamento):
        try:
            self.cur.execute(f'SELECT "Código do cliente" FROM Vendas WHERE "Número da venda" = {id_orcamento}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consultar_itens_orçamento_orc(self, id_orcamento):
        try:
            self.cur.execute(f'SELECT "Código do produto","Quantidade","Valor unitário" FROM Vendas_itens WHERE "Número da venda" = {id_orcamento}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_services(self, array_services):
        try:
            if (array_services):
                interrogacoes = ", ".join("?" * len(array_services))  # Cria "?, ?, ?, ?"
                sql = f'SELECT "Descrição do serviço", "Valor" FROM Servicos WHERE "Código do servico" IN ({interrogacoes})'
                self.cur.execute(sql, tuple(array_services))
                return self.cur.fetchall()
            else:
                print("Erro ao executar a consulta: lista vazia")
                return [] 
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def fechar_conexao(self):
        if self.con:
            self.con.close()
#       - CONSULTA TODOS ITENS DO ORCAMENTO X
def consulta_orcamento_itens(id_orc):
    banco = ConectarDB()
    orc = banco.consultar_orçamento_orc(id_orc)
    nomeCliente = banco.consultar_cliente_orc(orc[0][0])
    totalorc = 0
    orcItens = banco.consultar_itens_orçamento_orc(id_orc)
    orcItensArray = []
    for item in orcItens:
        orcItemArray = []
        if (item[0] != 0): # nome un valor total
            produtoOrc = banco.consultar_produto_orc(int(item[0]))
            orcItemArray.append(produtoOrc[0][0])
            orcItemArray.append(int(item[1]))
            orcItemArray.append(item[2])
            orcItemArray.append(item[1] * item[2])
            orcItemArray.append(False)
            orcItensArray.append(orcItemArray)
    banco.fechar_conexao()
    return totalorc, orcItensArray, nomeCliente[0][0]
#       - CONSULTA OS SERVIÇOS DE ID X PRESENTES NA ARRAY
def consulta_orcamento_servicos(array_services):
    banco = ConectarDB()
    array_servicos = []
    array_servicos_temp = banco.consulta_services(array_services)
    for item in array_servicos_temp:
        array_servicos_temp2 = []
        array_servicos_temp2.append(item[0])
        array_servicos_temp2.append(1)
        array_servicos_temp2.append(item[1])
        array_servicos_temp2.append(0)
        array_servicos.append(array_servicos_temp2)
    banco.fechar_conexao()
    return array_servicos

#   CLASSE PDF ORC PARA CRIAÇÃO DO PDF ORÇAMENTO
class PDFORC(FPDF):
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
        self.set_font('Arial', 'I', 8) 
        self.set_text_color(CINZA) 
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C') 

    def chapter_title_orc(self, txt):
        self.set_font('Arial', '', 12) 
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        self.cell(0, 6, txt, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body_orc(self, array, total_orc=0):
        self.set_font('Times', '', 12)
        self.set_fill_color(FUNDO_TEXTO_ITENS)
        fill_option = False
        for item in array:
            if (item[0] != "Null"):
                if (fill_option):
                    fill_option = False
                else:
                    fill_option = True
                item0 = str(item[0])
                item1 = str(int(item[1]))
                w1 = len(item1)
                if len(item0) <= 36:
                    self.cell((114-w1), HEIGH_LINHA_ITENS, item0, 0, 0,'',fill_option)
                    item2 = str(f"{float(item[2]):.2f}").replace('.',',')
                    w2 = len(item2)
                    self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)
                    item3 = str(f"{float(item[3]):.2f}").replace('.',',')
                    w3 = len(item3)
                    if (total_orc != 0):
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item2}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item3}", 0, 1,'',fill_option)
                    else:
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item2}", 0, 1,'',fill_option)
                    self.ln(2) 
                else:
                    item0Parte1, item0Parte2 = dividir_string(item0, 36)
                    self.cell((114-w1), HEIGH_LINHA_ITENS, item0Parte1, 0, 0,'',fill_option)
                    item2 = str(f"{float(item[2]):.2f}").replace('.',',')
                    w2 = len(item2)
                    self.cell((32+w1-w2), HEIGH_LINHA_ITENS, item1, 0, 0,'',fill_option)
                    item3 = str(f"{float(item[3]):.2f}").replace('.',',')
                    w3 = len(item3)
                    if (total_orc != 0):
                        self.cell((31+w2-w3), HEIGH_LINHA_ITENS, f"R${item2}", 0, 0,'',fill_option)
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item3}", 0, 1,'',fill_option)
                    else:
                        self.cell(0, HEIGH_LINHA_ITENS, f"R${item2}", 0, 1,'',fill_option)
                    self.ln(1) 
                    self.cell(0, HEIGH_LINHA_ITENS, item0Parte2, 0, 1,'',fill_option)
                    self.ln(2)
        self.ln(5)
        if (total_orc != 0):
            self.set_font('Times', '', 16)
            self.cell((160), HEIGH_LINHA_ITENS, "Total", 0, 0, 'R')
            self.cell(0, HEIGH_LINHA_ITENS, f"R${total_orc}", 0, 1, 'R')
            self.ln(2)

    def print_first_chapter_orc(self, txt, array, total_orc):
        self.add_page()
        self.chapter_title_orc(txt)
        self.chapter_body_orc(array, total_orc)

    def print_chapter_orc(self, txt, array):
        self.chapter_title_orc(txt)
        self.chapter_body_orc(array)  
#       - RESPONSAVEL PELA CRIAÇÃO DO PDF DE ORÇAMENTO
def cria_pdf_orcamento(itens_array, services_array, retorno): # itens = total_orc, itens, cliente, id_orc | services = 0, itens 
                                                              # [nome, quant, valor, total, bolean] | [nome, quant, valor]
    pdf = PDFORC()
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    global title
    title = 'LTC TECNOLOGIA ORÇAMENTO   ' + current_date # define o título
    pdf.set_title(title) # define o título do objeto PDF
    pdf.set_author('LTC TECNOLOGIA') # define o autor do objeto PDF
    texto_itens1 = "Produto                                                                           Quantidade            Valor(un)               Total"
    texto_itens2 = "Produto De Acordo Com a Instalação                            Quantidade            Valor(un)"
    texto_servicos = "Mão de Obra                                                                   Quantidade            Valor(un)"
    valor_final = str(f"{float(itens_array[0]):.2f}").replace('.',',')
    cha1_array = []
    cha2_array = []
    for item in itens_array[1]:
        if (item[4]):
            cha1_array.append(item)
        else:
            cha2_array.append(item)
    if (cha1_array):
        pdf.print_first_chapter_orc(texto_itens1, cha1_array, valor_final)
    if (cha2_array):
        pdf.print_chapter_orc(texto_itens2, cha2_array)
    if (services_array):
        pdf.print_chapter_orc(texto_servicos,services_array)
    if (retorno == 0):
        # Salva o PDF em um objeto BytesIO (em memória)
        pdf_bytes = io.BytesIO()
        pdf.output(pdf_bytes, "F")  # "F" para salvar em um arquivo
        pdf_bytes.seek(0)    
        return pdf_bytes
    else:
        # Salva o PDF em disco
        pdf.output(f'{itens_array[2]} {itens_array[3]}.pdf', 'F')

#   CLASSE PDF_VIEW - PARA ABRIR A IMAGEM RECEBIDA EM NOVA JANELA
class app_pdf_view(tk.Toplevel):
    def __init__(self, master, pdf_image):
        super().__init__(master)
        self.title("Exibidor PDF") 
        try:
            self.label = tk.Label(self) 
            self.label.image = pdf_image
            self.label.config(image=pdf_image)
            self.label.pack()
        except Exception as e:
            print (f"Erro ao mostrar o PDF: {e}")

#   CLASSE PDF_ORCAMENTO
class app_pdf_orcamento(tk.Frame): # ou Toplevel para nova janela..
    def __init__(self, master):
        super().__init__(master)
        # Parametros-variaveis utilizados | INICIALIZAÇÃO
        self.retorno_orc_db = []
        self.labels = []
        self.buttons = []
        self.labels_edit = []
        self.buttons_edit = []
        self.labels_edit_state = False
        self.variaveis_checkboxes = {}
        self.checkboxes_itens = []
        self.services_opt = [44, 5, 82, 14]
        # 44 m obra - 5 hr tecnico - 82 hr aj tecnico - 14 km a mais
        self.id_orc = None
        self.cont_labels = None
        self.contindice = None
        self.controw = None
        self.index_item_edit = None
        ''' no caso de nova janela
        self.TAMANHO_PADRAO_TELA = "800x500"
        self.tamanho_tela = self.TAMANHO_PADRAO_TELA
        # GERAÇÃO DA TELA
        self.title("ORÇAMENTO LTC")
        self.geometry(self.tamanho_tela)
        self.resizable(False, False)  #  horizontal e vertical
        '''
        # COLUNAS CONFIG
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=8)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.columnconfigure(9, weight=1)
        self.columnconfigure(10, weight=1)
        # WIDGETS ESQUERDA
        self.label_esquerda = tk.Label(self, text="Código orçamento:")
        self.label_esquerda.grid(row=0, column=0, padx=5, sticky="w") 
        self.entry_orcamento = tk.Entry(self)
        self.entry_orcamento.grid(row=0, column=1, padx=5, pady=3, sticky="ew") 
        self.botao_exibir_pdf = ttk.Button(self, text="CARREGAR DADOS", command=lambda: self.exibir_pdf_samepage(self.entry_orcamento.get()))
        self.botao_exibir_pdf.grid(row=0, column=2, padx=5, pady=3, sticky="ew") 
        # nome item
        self.label_esquerda_nome = tk.Label(self, text="Descrição:")
        self.entry_esquerda_nome = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_nome)
        self.labels_edit.append(self.entry_esquerda_nome)
        # unidade item
        self.label_esquerda_un = tk.Label(self, text="Quantidade:")
        self.entry_esquerda_un = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_un)
        self.labels_edit.append(self.entry_esquerda_un)
        # valor item
        self.label_esquerda_valor = tk.Label(self, text="Valor unitário:")
        self.entry_esquerda_valor = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_valor)
        self.labels_edit.append(self.entry_esquerda_valor)
        # botoes
        self.botao_novo_item = ttk.Button(self, text="NOVO PRODUTO", command=lambda: self.novo_item_widget())
        self.buttons_edit.append(self.botao_novo_item)
        self.botao_salva_item = ttk.Button(self, text="SALVAR", command=lambda: self.botao_edit(0))
        self.buttons_edit.append(self.botao_salva_item)
        self.botao_cancela_edit = ttk.Button(self, text="CANCELA", command=lambda: self.botao_edit(1))
        self.buttons_edit.append(self.botao_cancela_edit)
        # aviso erro
        self.label_esquerda_erro = tk.Label(self, text="Valor ou Unidade incorretos!")
        self.labels_edit.append(self.label_esquerda_erro)
        # LINHA VERTICAL
        self.separador = tk.Frame(self, width=2, bg="black")
        self.separador.grid(row=2, column=3, rowspan=96, sticky="ns")
        # WIDGETS DIREITA
        self.label_direita = tk.Label(self, text="DESCRIÇÃO:")
        self.label_direita.grid(row=0, column=4, pady=3, sticky="ew") 
        self.label_unitario = tk.Label(self, text="UN/M")
        self.label_unitario.grid(row=0, column=5, pady=3, sticky="ew") 
        self.label_valor = tk.Label(self, text="R$")
        self.label_valor.grid(row=0, column=6, pady=3, sticky="ew") 
        self.label_checkbox = tk.Label(self, text="FIXO")
        self.label_checkbox.grid(row=0, column=9, pady=3, padx=(5,10), sticky="ew") 
        # WIDGETS OUTROS
        self.linha_fim = tk.Frame(self, width=2, bg="black")
        self.linha_fim.grid(row=98, column=0, padx=6, pady=5, columnspan=99, sticky="ew")
        self.botao_abrir_pdf = ttk.Button(self, text="ABRIR PDF", command=lambda: self.exibir_pdf())
        self.botao_abrir_pdf.grid(row=99, column=3, pady=5)
        # DIVISORIA CAMPOS 
        self.linha_esquerda = tk.Frame(self, width=2, bg="black")
        self.linha_esquerda.grid(row=1, column=0, padx=6, pady=5, columnspan=99, sticky="ew")

    def exibir_pdf_samepage(self, id_orc_entry):
        self.id_orc = id_orc_entry
        if (len(self.retorno_orc_db) == 0):
            #print("Busca inicial")
            total_orc, itens_array, nome_cliente = consulta_orcamento_itens(self.id_orc)
            self.retorno_orc_db = [total_orc, itens_array, nome_cliente, self.id_orc]
            self.cont_labels = 0
            self.alterna_widgets_direita()
        elif (self.id_orc != self.retorno_orc_db[3]):
            #print("Nova busca")
            total_orc, itens_array, nome_cliente = consulta_orcamento_itens(self.id_orc)
            self.retorno_orc_db = [total_orc, itens_array, nome_cliente, self.id_orc]
            self.cont_labels = 0
            self.alterna_widgets_direita()
        None #print("Sem busca!")
    def alterna_widgets_direita(self):
        if (self.labels and self.cont_labels == 0):
            try:
                for array in self.labels:
                    array[0].destroy()
                    array[1].destroy()
                    array[2].destroy()
            except Exception as e:
                print (f"Erro ao apagar labels: {e}")
        if (self.buttons and self.cont_labels == 0):
            try:
                for array in self.buttons:
                    for item in array:
                        item.destroy()
            except Exception as e:
                print (f"Erro ao apagar botoes: {e}")
        if (self.variaveis_checkboxes and self.cont_labels == 0):
            try:
                for item in self.checkboxes_itens:
                    item.destroy()
            except Exception as e:
                print (f"Erro ao apagar checkboxes: {e}")
        self.update()
        time.sleep(0.6) 
        if (self.cont_labels == 0):
            self.labels = []
            self.buttons = []
            self.checkboxes_itens = []
            self.variaveis_checkboxes = {}
            self.controw = 2
            self.contindice = 0
            for item in self.retorno_orc_db[1]:
                # labels itens
                labbels_temp = []
                label = tk.Label(self, text=f"{item[0][0:15]}")
                label.grid(row=self.controw, column=4, sticky="ew")
                labbels_temp.append(label)
                label = tk.Label(self, text=f"{item[1]}")
                label.grid(row=self.controw, column=5, sticky="ew")
                labbels_temp.append(label)
                label = tk.Label(self, text=f"{item[2]}")
                label.grid(row=self.controw, column=6, sticky="ew")
                labbels_temp.append(label)
                label = tk.Frame(self, width=1, bg="black")
                labbels_temp.append(label)
                labbels_temp.append("Temp")
                self.labels.append(labbels_temp)
                # botoes itens
                botao_edit = ttk.Button(self, text="Editar", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 0, label_row))
                botao_edit.grid(row=self.controw, column=7, sticky="ew")
                botao_delete = ttk.Button(self, text="Remover", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 1, label_row))
                botao_delete.grid(row=self.controw, column=8, sticky="ew")
                buttons_temp = []
                buttons_temp.append(botao_edit)
                buttons_temp.append(botao_delete)
                self.buttons.append(buttons_temp)
                # checkbox
                var_check = tk.BooleanVar(value=True)
                self.variaveis_checkboxes[self.contindice] = var_check
                check = tk.Checkbutton(self, variable=var_check)
                check.grid(row=self.controw, column=9, pady=3, padx=5, sticky="ew")
                self.checkboxes_itens.append(check)
                # contadores update
                self.controw += 1
                self.contindice += 1
                self.cont_labels += 1
                self.update()
                time.sleep(0.6)
            self.buttons_edit[0].grid(row=2, column=1, padx=5, sticky="w") 
        else:
            item = self.retorno_orc_db[1][self.cont_labels]
            # labels item
            labbels_temp = []
            label = tk.Label(self, text=f"{item[0][0:15]}")
            label.grid(row=self.controw, column=4, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(self, text=f"{item[1]}")
            label.grid(row=self.controw, column=5, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(self, text=f"{item[2]}")
            label.grid(row=self.controw, column=6, sticky="ew")
            labbels_temp.append(label)
            label = tk.Frame(self, width=1, bg="black")
            labbels_temp.append(label)
            labbels_temp.append("Temp")
            self.labels.append(labbels_temp)
            # botoes item
            botao_edit = ttk.Button(self, text="Editar", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 0, label_row))
            botao_edit.grid(row=self.controw, column=7, sticky="ew")
            botao_delete = ttk.Button(self, text="Remover", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 1, label_row))
            botao_delete.grid(row=self.controw, column=8, sticky="ew")
            buttons_temp = []
            buttons_temp.append(botao_edit)
            buttons_temp.append(botao_delete)
            self.buttons.append(buttons_temp)
            # checkbox
            var_check = tk.BooleanVar(value=True)
            self.variaveis_checkboxes[self.contindice] = var_check
            check = tk.Checkbutton(self, variable=var_check)
            check.grid(row=self.controw, column=9, pady=3, padx=5, sticky="ew")
            self.checkboxes_itens.append(check)
            # contadores update
            self.controw += 1
            self.contindice += 1
            self.cont_labels += 1
            self.update()
            time.sleep(0.6)
        return self.update()
    def botao_item (self, indice, operacao, label_row): 
        if (operacao == 0): #EDITA
            #print (f"Edita {indice} na linha {label_row}")
            self.index_item_edit = indice
            if (not self.labels_edit_state):
                self.alterna_widgets_esquerda()
            self.labels_edit[1].delete(0, tk.END)
            self.labels_edit[1].insert(0,self.retorno_orc_db[1][indice][0])
            self.labels_edit[3].delete(0, tk.END)
            self.labels_edit[3].insert(0,int(self.retorno_orc_db[1][indice][1]))
            self.labels_edit[5].delete(0, tk.END)
            self.labels_edit[5].insert(0,(str(self.retorno_orc_db[1][indice][2]).replace(".", ",")))
            return self.update()
        else: # DELETA OU RECUPERA
            if (self.retorno_orc_db[1][indice][0] == "Null"):
                try:
                    # edita nome para retornar ao pdf
                    self.retorno_orc_db[1][indice][0] = self.labels[indice][4]
                    # atualiza botões e label
                    self.buttons[indice][0].grid(row=label_row, column=7, sticky="ew")
                    self.buttons[indice][1].config(text="Remover")
                    self.labels[indice][3].grid_forget()
                    #print ("Registro recuperado!")
                    return self.update()
                except:
                    print("Não foi possivel recuperar!")
                    return None
            else:
                try:
                    if (self.labels_edit_state):
                        self.alterna_widgets_esquerda()
                    self.labels[indice][4] = self.retorno_orc_db[1][indice][0]
                    # edita nome para sair do pdf
                    self.retorno_orc_db[1][indice][0] = "Null"
                    # atualiza valor final
                    self.retorno_orc_db[0] = float(self.retorno_orc_db[0]) - (int(self.retorno_orc_db[1][indice][1])*self.retorno_orc_db[1][indice][2])
                    # atualiza botões e label
                    self.buttons[indice][0].grid_forget()
                    self.buttons[indice][1].config(text="Recupera")
                    self.labels[indice][3].grid(row=label_row, column=4, columnspan=3, sticky="ew")
                    #print ("Registro removido!")
                    return self.update()
                except:
                    print("Não foi possivel apagar!")
                    return None
    def alterna_widgets_esquerda(self):
        if (self.labels_edit_state):
            self.labels_edit[3].delete(0, tk.END)
            self.labels_edit[5].delete(0, tk.END)
            self.labels_edit[1].delete(0, tk.END)
            self.labels_edit[0].grid_forget()
            self.labels_edit[1].grid_forget()
            self.labels_edit[2].grid_forget()
            self.labels_edit[3].grid_forget()
            self.labels_edit[4].grid_forget()
            self.labels_edit[5].grid_forget()
            self.labels_edit[6].grid_forget()
            self.buttons_edit[1].grid_forget()
            self.buttons_edit[2].grid_forget()
            self.buttons_edit[0].grid(row=2, column=1, padx=5, sticky="w")
            self.labels_edit_state = False
        else:
            self.labels_edit[0].grid(row=2, column=0, padx=5, sticky="w") 
            self.labels_edit[1].grid(row=2, column=1, padx=5, pady=3, sticky="ew") 
            self.labels_edit[2].grid(row=3, column=0, padx=5, sticky="w") 
            self.labels_edit[3].grid(row=3, column=1, padx=5, pady=3, sticky="ew") 
            self.labels_edit[4].grid(row=4, column=0, padx=5, sticky="w") 
            self.labels_edit[5].grid(row=4, column=1, padx=5, pady=3, sticky="ew") 
            self.buttons_edit[0].grid_forget()
            self.buttons_edit[1].grid(row=5, column=1, padx=5, pady=3, sticky="ew")
            self.buttons_edit[2].grid(row=5, column=2, padx=5, pady=3, sticky="ew") 
            self.labels_edit_state = True
        return self.update()
    def novo_item_widget(self):
        self.index_item_edit = -1
        return self.alterna_widgets_esquerda()
    def botao_edit (self, operacao):
        if (operacao == 0): # EDITA/SALVA
            if (self.index_item_edit >= 0):
                try:
                    nome_item = self.labels_edit[1].get().upper()
                    quant_item = int(self.labels_edit[3].get())
                    valor_item = float((self.labels_edit[5].get()).replace(",", "."))
                    self.retorno_orc_db[1][self.index_item_edit][0] = nome_item
                    self.retorno_orc_db[1][self.index_item_edit][1] = quant_item
                    valor_item_temp = self.retorno_orc_db[1][self.index_item_edit][2]
                    self.retorno_orc_db[1][self.index_item_edit][2] = valor_item
                    valor_item_temp = (valor_item*quant_item) - valor_item_temp
                    self.retorno_orc_db[1][self.index_item_edit][3] = quant_item*valor_item
                    self.labels[self.index_item_edit][0].config(text=nome_item[:15])
                    self.labels[self.index_item_edit][1].config(text=str(quant_item))
                    self.labels[self.index_item_edit][2].config(text=str(valor_item))
                    return self.alterna_widgets_esquerda()
                except:
                    self.labels_edit[6].grid(row=6, column=0, columnspan=3, padx=5, pady=3, sticky="ew") 
            else: # NOVO ITEM
                nome_item = self.labels_edit[1].get().upper()
                quant_item = int(self.labels_edit[3].get())
                valor_item = float((self.labels_edit[5].get()).replace(",", "."))
                total_item = quant_item*valor_item
                item_temp_array = [nome_item, quant_item, valor_item, total_item, False]
                # ADICIONA O ITEM NOVO EM TELA E ADICIONA ELE NO ARRAY
                self.retorno_orc_db[1].append(item_temp_array)
                return self.alterna_widgets_esquerda(), self.alterna_widgets_direita()
        else: # CANCELA
            return self.alterna_widgets_esquerda()
    def exibir_pdf (self):
        # AQUI SEPARO OS ITENS FIXOS E ITENS VARIAVEIS DO ORÇAMENTO
        selecoes = [(opcao, var.get()) for opcao, var in self.variaveis_checkboxes.items()]
        selecoes2 = [(opcao, valor) for opcao, valor in selecoes if valor]
        for item in self.retorno_orc_db[1]:
            item[4] = False
        # AQUI CALCULO O VALOR FINAL DO DOCUMENTO
        valor_final = 0
        for item in selecoes2:
            self.retorno_orc_db[1][item[0]][4] = item[1]
            if (self.retorno_orc_db[1][item[0]][0] != "Null"):
                valor_final += self.retorno_orc_db[1][item[0]][3]
        self.retorno_orc_db[0] = valor_final
        # AQUI RECEBO OS SERVIÇOS E ARMAZENDO EM ARRAY
        services_array = consulta_orcamento_servicos(self.services_opt)
        # AQUI RETORNA A FUNÇÃO QUE APRESENTA O DOCUMENTO
        return self.exibir_pdf_orçamento(services_array)
    def exibir_pdf_orçamento(self, services_array): # total_orc, itens, cliente, id_orc
        try:
            pdf_dados = cria_pdf_orcamento(self.retorno_orc_db, services_array, 0)
        except Exception as e:
            print (f"Erro ao criar PDF: {e}")
        try:
                # Cria um arquivo temporário
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as self.temp_file:
                    temp_filename = os.path.join(self.temp_file.name)
                    # Escreva o conteúdo do PDF no arquivo temporário
                    self.temp_file.write(pdf_dados.getvalue())
                    # Abre o arquivo temporário com PyMuPDF
                doc = fitz.open(temp_filename)
                page = doc[0]
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                photo = ImageTk.PhotoImage(img)
                # ENVIA A IMAGEM GERADA PARA UMA INSTANCIA DE CLASSE RESPONSAVEL POR MOSTRAR EM TELA
                app_pdf_view_instance = app_pdf_view(self, photo)
                app_pdf_view_instance.mainloop()
                # Deleta o arquivo temporário
                doc.close()
                os.remove(temp_filename)
                
        except Exception as e:
            print(f"Erro ao exibir PDF: {e}")

#    PROGRAMA PRINCIPAL
class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação Principal")
        self.geometry("800x500")

        # Menu para alternar entre as telas
        self.header = tk.Frame(self, bg="lightblue", pady = 10)
        self.header.pack(fill=tk.X, side=tk.TOP)
        # Conteúdo do header (exemplo)
        self.label_app_pdf_orcamento = tk.Label(self.header, text="GERAR ORÇAMENTO", font=("Arial", 16), bg="lightblue")
        self.label_app_pdf_orcamento.pack(side=tk.LEFT, expand=True)
        self.label_app_pdf_orcamento.bind("<Button-1>", self.abrir_app_pdf_orcamento)
        self.label_app_pdf_orcamento2 = tk.Label(self.header, text="ESTOQUE", font=("Arial", 16), bg="lightblue")
        self.label_app_pdf_orcamento2.pack(side=tk.LEFT, expand=True)
        self.label_app_pdf_orcamento2.bind("<Button-1>", self.teste)
        self.label_app_pdf_orcamento2 = tk.Label(self.header, text="GERAR RELATÓRIO", font=("Arial", 16), bg="lightblue")
        self.label_app_pdf_orcamento2.pack(side=tk.LEFT, expand=True)
        self.label_app_pdf_orcamento2.bind("<Button-1>", self.teste)
            
        self.app_pdf_orcamento_conteiner = app_pdf_orcamento(self)
       
    def abrir_app_pdf_orcamento(self, event):
        try:
            self.app_pdf_orcamento_conteiner.pack()
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")
    def teste(self, event):
        try:
            print("Teste")
            self.app_pdf_orcamento_conteiner.pack_forget()
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")
#       - CHAMADA DO PROGRAMA PRINCIPAL PARA INICIAR LOOP
if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()