import requests
import json
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from config import *
from extras import centralizar_tela_app, dividir_string, exibir_pdf

#   ACESSO AO BANCO DE DADOS
class ConectarDB:
    def __init__(self):
        # Criando conexão.
        self.con = pyodbc.connect(CONN_STR)
        # Criando cursor.
        self.cur = self.con.cursor()
    def fechar_conexao(self):
        if self.con:
            self.con.close()
    def consulta_itens_pedido(self,id):
        try:
            self.cur.execute(f'SELECT "Código do servico","Código do produto","Quantidade","Valor unitário" FROM "Pedidos_itens" WHERE "Número do pedido" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_itens_os(self,id):
        try:
            self.cur.execute(f'SELECT "Código do servico","Código do produto","Quantidade","Valor unitário" FROM "OS itens" WHERE "Número da os" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_dados_os(self,id):
        try:
            self.cur.execute(f'SELECT "problema","Data","Código do cliente","Comprador" FROM "OS" WHERE "Número da os" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_dados_pedido(self,id):
        try:
            self.cur.execute(f'SELECT "Observações","Data","Código do cliente","Comprador" FROM "Pedidos" WHERE "Número do pedido" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_cliente(self,id):
        try:
            self.cur.execute(f'SELECT "Nome do cliente" FROM Clientes WHERE "Código do cliente" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []  
    def consultar_nome_produto(self, id):
        try:
            self.cur.execute(f'SELECT "Descrição do produto" FROM Produtos WHERE "Código do produto" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []  
    def consultar_ncm_produto(self, id):
        try:
            self.cur.execute(f'SELECT "Classificação fiscal" FROM Produtos WHERE "Código do produto" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []  
    def consulta_nome_servico(self,id):
        try:
            self.cur.execute(f'SELECT "Descrição do serviço" FROM Servicos WHERE "Código do servico" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
#   FUNÇÃO E CLASSES NECESSÁRIAS
def GeminiGetNCM(descricao):
    prompt = (
        f"Dado o produto '{descricao}', retorne apenas o número do NCM correspondente. "
        "Exemplo: 'Smartphone Apple iPhone 15 Pro Max', NCM: 8517.12.31."
        "Se não encontrar o NCM, retorne 'NCM não encontrado'."
    )
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Isso levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        data = response.json()
        # O caminho para a resposta pode variar, então ajustamos
        ncm = data['candidates'][0]['content']['parts'][0]['text'].strip()
        # Verifica se a resposta parece um NCM (formato dddd.dd.dd)
        if "." in ncm and len(ncm.replace('.', '')) >= 8:
            return ncm.replace('.', '')
        else:
            return 0
    except requests.exceptions.RequestException as e:
        #print(f"Ocorreu um erro na requisição: {e}")
        return 0
    except (KeyError, IndexError) as e:
        #print(f"Formato de resposta inesperado: {e}")
        return 0
class Os():
    def __init__(self, id):
        try:
            banco = ConectarDB()
            self.id = int(id)
            consulta = banco.consulta_dados_os(self.id)
            self.texto = consulta[0][0]
            self.data = consulta[0][1].strftime("%d/%m/%Y")
            self.cliente = banco.consulta_cliente(int(consulta[0][2]))[0][0]
            self.comprador = consulta[0][3]
            self.produtos = []
            self.servicos = []
            self.total = 0
            self.total_m_obra = 0
            self.detalha_servicos = True
            consulta = banco.consulta_itens_os(self.id)
            for item in consulta: # serv ID (0), prod ID (1), un (2), vl (3)
                if (item[0] != 0):      #Serviço
                    obj_temp = Servico(item[0], banco.consulta_nome_servico(item[0])[0][0], item[2], item[3])
                    self.servicos.append(obj_temp)
                    self.total_m_obra += (item[2] * item[3])
                else:                   #Produto
                    obj_temp = Produto(item[1], banco.consultar_nome_produto(item[1])[0][0], item[2], item[3], banco.consultar_ncm_produto(item[1])[0][0])
                    self.produtos.append(obj_temp)
                self.total += (item[2] * item[3])
            banco.fechar_conexao()
            self.total = round(self.total, 2)
            self.total_m_obra = round(self.total_m_obra, 2)
        except Exception as ex:
            self.id = 0
class Pedido():
    def __init__(self, id):
        try:
            banco = ConectarDB()
            self.id = id
            consulta = banco.consulta_dados_pedido(self.id)
            self.texto = consulta[0][0]
            self.data = consulta[0][1].strftime("%d/%m/%Y")
            self.cliente = banco.consulta_cliente(int(consulta[0][2]))[0][0]
            self.comprador = consulta[0][3]
            self.produtos = []
            self.servicos = []
            self.total = 0
            self.total_m_obra = 0
            consulta = banco.consulta_itens_pedido(self.id)
            for item in consulta: # serv ID (0), prod ID (1), un (2), vl (3)
                if (item[0] != 0):      #Serviço
                    obj_temp = Servico(item[0], banco.consulta_nome_servico(item[0])[0][0], item[2], item[3])
                    self.servicos.append(obj_temp)
                    self.total_m_obra += (item[2] * item[3])
                else:                   #Produto
                    obj_temp = Produto(item[1], banco.consultar_nome_produto(item[1])[0][0], item[2], item[3], banco.consultar_ncm_produto(item[1])[0][0])
                    self.produtos.append(obj_temp)
                self.total += (item[2] * item[3])
            banco.fechar_conexao()
            self.total = round(self.total, 2)
            self.total_m_obra = round(self.total_m_obra, 2)
        except Exception as ex:
            messagebox.showinfo("Erro", f"Pedido inválido")
class Servico():
    def __init__(self, id, descricao, quantidade, valor):
        self.id = int(id)
        self.descricao = descricao
        self.quantidade = int(quantidade)
        self.valor = float(valor)
        self.total = round((self.quantidade * self.valor), 2)
class Produto():
    def __init__(self, id, descricao, quantidade, valor, ncm):
        self.id = int(id)
        self.ncm = 0
        self.descricao = descricao
        self.quantidade = int(quantidade)
        self.valor = float(valor)
        self.total = round((self.quantidade * self.valor), 2)
        try:
            ncm = int(ncm)
            if (ncm >= 8):
                self.ncm = ncm
        except:
            self.ncm = GeminiGetNCM(self.descricao)
class PDF_REL(FPDF):
    def header(self):
        title = f"LTC TECNOLOGIA RELATÓRIO - Página {self.page_no()}/{{nb}}"
        self.image('logo.png', 10, 0, 33)
        self.set_font('Courier', 'B', 15) 
        w = self.get_string_width(title) + 6 
        self.set_x((210 - w) / 2) 
        self.cell(w, 12, title, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Courier', '', 12) 
        self.cell(0, 10, "LTC TECNOLOGIA - LUIZ VOLKART, 35, CENTRO , TRÊS COROAS/RS", align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    def cabecalho_secao (self, objeto):
        self.set_font('Courier', 'B', 12) 
        informacoes = ""
        if (isinstance(objeto, Os)):
            informacoes += f"OS {objeto.id} "
        else:
            informacoes += f"Pedido {objeto.id} "
        informacoes += f"- Data {objeto.data} "
        if (objeto.comprador):
            informacoes += f"- Comprador {objeto.comprador}"
        self.cell(0, 8, informacoes, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if (objeto.texto):
            self.descricao_texto(objeto.texto)
        self.ln(1)
        return
    def cabecalho_unificado_os (self, ids):
        self.set_font('Courier', 'B', 12) 
        informacoes = "OS"
        for id in ids:
            informacoes += f" - {id}"
        self.multi_cell(0, 8, informacoes, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        #   TODO OBS
        self.ln(1)
        return
    def cabecalho_unificado_pedido (self, ids):
        self.set_font('Courier', 'B', 12) 
        informacoes = "Pedidos"
        for id in ids:
            informacoes += f" - {id}"
        self.multi_cell(0, 8, informacoes, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        #   TODO OBS
        self.ln(1)
        return
    def tabela_produtos (self, produtos):
        self.set_fill_color(255, 255, 255)
        self.set_font("Courier", size=10)
        with self.table(
            col_widths=(26, 100, 32, 32, 34, 36),
            text_align="CENTER"
        ) as table:
            headings_row = table.row()
            for heading in self.cabecalho_produtos:
                headings_row.cell(heading)
            for produto in produtos:
                row = table.row()
                row.cell(str(produto[0]))
                row.cell(str(produto[1]))
                row.cell(str(produto[2]))
                row.cell("R$" + str(produto[3]))
                row.cell(str(produto[4]))
                row.cell("R$" + str(produto[5]))
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        return
    def tabela_servicos(self, servicos):
        self.set_fill_color(255, 255, 255)
        self.set_font("Courier", size=10)
        with self.table(
            col_widths=(100, 40, 34, 50),
            text_align="CENTER"
        ) as table:
            headings_row = table.row()
            for heading in self.cabecalho_servicos:
                headings_row.cell(heading)
            for servico in servicos:
                row = table.row()
                row.cell(str(servico[0]))
                row.cell("R$" + str(servico[1]))
                row.cell(str(servico[2]))
                row.cell("R$" + str(servico[3]))
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        return
    def mao_obra_simples (self, total):
        if (total == 0):
            return
        self.set_fill_color(255, 255, 255)
        self.set_font("Courier", "B", size=12)
        total_tratado = f"{total:.2f}".replace(".",",")
        self.cell(0, 8, f"Mão de Obra R$ {total_tratado}", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        return
    def descricao_texto (self, texto):
        self.multi_cell(0, 8, f"Descrição: {texto}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        return
    def valor_total (self, total):
        self.set_fill_color(255, 255, 255)
        self.set_font("Courier", "B", size=14)
        total_tratado = f"{total:.2f}".replace(".",",")
        self.cell(0, 8, f"Total R$ {total_tratado}", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        return
#   APP PRINCIPAL
class AppRelatorio(tk.Frame):
    def __init__(self, master, reinicia_app):
        #   INICIAL E CONFIGS
        super().__init__(master)
        #   PARAMETROS INICIAIS
        self.func_reiniciar = reinicia_app
        self.os_carregadas = []
        self.pedidos_carregados = []
        self.total_os = 0
        self.total_pedidos = 0
        self.total_relatorio = 0
        #   CORPO APP
        frame_geral = ttk.Frame(self)
        frame_geral.pack(expand=True)
        frame_div_geral = ttk.Frame(frame_geral, borderwidth=5, relief=tk.GROOVE)
        frame_div_geral.pack(side="left", expand=True)
        frame_div_itens = ttk.Frame(frame_div_geral)
        frame_div_itens.pack(expand=True)
        frame_opcoes_geral = ttk.Frame(frame_geral, borderwidth=5, relief=tk.GROOVE)
        frame_opcoes_geral.pack(side="left", expand=True)
        #       SEÇÃO OS
        frame_os = ttk.Frame(frame_div_itens, borderwidth=5, relief=tk.RAISED)
        frame_os.pack(side="left", expand=True)
        ttk.Label(frame_os, text="Adicionar OS", font=("Arial", 12, "bold")).pack(expand=True, padx=10)
        frame_os_header = ttk.Frame(frame_os)
        frame_os_header.pack(expand=True, pady=10)
        self.entry_os = tk.Entry(frame_os_header, width=18, justify="center")
        self.entry_os.pack(side="left", expand=True, padx=10)
        ttk.Button(frame_os_header, text="Adicionar", command=lambda: self.adicionar_os(self.entry_os.get())).pack(side="left", expand=True)
        self.tree_os = TreeViewItens(self,frame_os)
        self.tree_os.pack(expand=True)
        self.label_total_os = ttk.Label(frame_os, text=f"R$ {self.total_os}", font=("Arial", 12, "bold"))
        self.label_total_os.pack(expand=True, padx=10)
        #       SEÇÃO PEDIDOS
        frame_pedidos = ttk.Frame(frame_div_itens, borderwidth=5, relief=tk.RAISED)
        frame_pedidos.pack(side="left", expand=True)
        ttk.Label(frame_pedidos, text="Adicionar Pedido", font=("Arial", 12, "bold")).pack(expand=True, padx=10)
        frame_pedidos_header = ttk.Frame(frame_pedidos)
        frame_pedidos_header.pack(expand=True, pady=10)
        self.entry_pedido = tk.Entry(frame_pedidos_header, width=18, justify="center")
        self.entry_pedido.pack(side="left", expand=True, padx=10)
        ttk.Button(frame_pedidos_header, text="Adicionar", command=lambda: self.adicionar_pedido(self.entry_pedido.get())).pack(side="left", expand=True)
        self.tree_pedidos = TreeViewItens(self,frame_pedidos)
        self.tree_pedidos.pack(expand=True)
        self.label_total_pedidos = ttk.Label(frame_pedidos, text=f"R$ {self.total_pedidos}", font=("Arial", 12, "bold"))
        self.label_total_pedidos.pack(expand=True, padx=10)
        #       SEÇÃO TOTAL GERAL
        self.label_total_relatorio = ttk.Label(frame_div_geral, text=f"R$ {self.total_relatorio}", font=("Arial", 14, "bold"))
        self.label_total_relatorio.pack(expand=True, pady=10)
        #       SEÇÃO DIREITA - OPÇÕES E BOTÃO PARA GERAR O PDF
        #           OS
        frame_unificar_os = ttk.Frame(frame_opcoes_geral, borderwidth=5, relief=tk.RAISED)
        frame_unificar_os.pack(expand=True)
        self.checkbox_unificar_os_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_os, text = "Unificar OS", variable = self.checkbox_unificar_os_var).pack(expand=True, padx=15)
        self.checkbox_detalhar_os_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_os, text = "Detalhar Serviços", variable = self.checkbox_detalhar_os_var).pack(expand=True, padx=15)
        #           PEDIDOS
        frame_unificar_pedidos = ttk.Frame(frame_opcoes_geral, borderwidth=5, relief=tk.RAISED)
        frame_unificar_pedidos.pack(expand=True)
        self.checkbox_unificar_pedidos_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_pedidos, text = "Unificar Pedidos", variable = self.checkbox_unificar_pedidos_var).pack(expand=True, padx=15)
        self.checkbox_detalhar_pedidos_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_pedidos, text = "Detalhar Serviços", variable = self.checkbox_detalhar_pedidos_var).pack(expand=True, padx=15)
        #           GERAL
        frame_unificar_tudo = ttk.Frame(frame_opcoes_geral, borderwidth=5, relief=tk.RAISED)
        frame_unificar_tudo.pack(expand=True)
        self.checkbox_unificar_tudo_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_tudo, text = "Unificar Tudo", variable = self.checkbox_unificar_tudo_var).pack(expand=True, padx=15)
        self.checkbox_detalhar_tudo_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_unificar_tudo, text = "Detalhar Serviços", variable = self.checkbox_detalhar_tudo_var).pack(expand=True, padx=15)
        ttk.Button(frame_opcoes_geral, text="Gerar PDF", command= self.gerar_pdf).pack(expand=True, pady=15)
        ttk.Button(frame_opcoes_geral, text="Cancela/Limpa", command = self.func_reiniciar).pack(expand=True, pady=30)
    def adicionar_os(self,id):
        try:
            temp = Os(id)
            if(temp.id != 0 and temp.total > 0):
                for obj in self.os_carregadas:
                    if (temp.id == obj.id):
                        return messagebox.showinfo("Erro", "OS já adicionada anteriormente!")
                self.entry_os.delete(0, tk.END)
                self.os_carregadas.append(temp)
                self.atualiza_labels_valores(temp)
                return self.tree_os.popular_treeview(self.os_carregadas)
            else:
                return messagebox.showinfo("Erro", f"OS inválida!")
        except:
            None
    def adicionar_pedido(self,id):
        try:
            temp = Pedido(id)
            if(temp.id != 0 and temp.total > 0):
                for obj in self.pedidos_carregados:
                    if (temp.id == obj.id):
                        return messagebox.showinfo("Erro", "Pedido já adicionada anteriormente!")
                self.entry_pedido.delete(0, tk.END)
                self.pedidos_carregados.append(temp)
                self.atualiza_labels_valores(temp)
                return self.tree_pedidos.popular_treeview(self.pedidos_carregados)
            else:
                return messagebox.showinfo("Erro", f"Pedido inválido!")
        except:
            None
    def atualiza_labels_valores(self, obj):
        if (isinstance(obj, Os)):
            self.total_os += obj.total
            self.label_total_os.config(text=f"R$ {self.total_os:.2f}")
            self.total_relatorio += obj.total
            self.label_total_relatorio.config(text=f"R$ {self.total_relatorio:.2f}")
        else:
            self.total_pedidos += obj.total
            self.label_total_pedidos.config(text=f"R$ {self.total_pedidos:.2f}")
            self.total_relatorio += obj.total
            self.label_total_relatorio.config(text=f"R$ {self.total_relatorio:.2f}")
    def abrir_item(self,obj):
        self.remove_app_item = False
        self.wait_window(AppTelaItem(self, obj))
        if (self.remove_app_item):
            #print(f"Removeu {obj.id}")
            if (isinstance(obj, Os)):
                self.os_carregadas.remove(obj)
                self.tree_os.popular_treeview(self.os_carregadas)
            else:
                self.pedidos_carregados.remove(obj)
                self.tree_pedidos.popular_treeview(self.pedidos_carregados)
            obj.total = -obj.total
            self.atualiza_labels_valores(obj)
            del obj
        return
    def gerar_pdf(self):
        pdf = PDF_REL()
        pdf.set_text_color(PRETO)
        pdf.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2])
        #   TABELANDO OS DADOS
        pdf.cabecalho_produtos = ["Código","Descrição","NCM", "Valor","Quantidade","Total"]
        pdf.cabecalho_servicos = ["Descrição", "Valor", "Quantidade", "Total"]
        if (self.checkbox_unificar_tudo_var.get()):
            if (self.os_carregadas or self.pedidos_carregados):
                self.descricao_data = "GERAL"
                self.wait_window(AppTelaDescricao(self))
                if (self.checkbox_detalhar_tudo_var.get()): #  UNIFICA TUDO E DETALHA SERVIÇOS
                    pdf.add_page()
                    produtos_data = []
                    servicos_data = []
                    total_data = 0
                    ids_data = []
                    for os in self.os_carregadas:
                        ids_data.append(os.id)
                        total_data += os.total
                        for item in os.produtos:
                            produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                        for item in os.servicos:
                            servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                    pdf.cabecalho_unificado_os(ids_data)
                    ids_data = []
                    for pedido in self.pedidos_carregados:
                        ids_data.append(pedido.id)
                        total_data += pedido.total
                        for item in pedido.produtos:
                            produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                        for item in pedido.servicos:
                            servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                    pdf.cabecalho_unificado_pedido(ids_data)
                    pdf.descricao_texto(self.descricao_data)
                    pdf.tabela_produtos(produtos_data)
                    pdf.tabela_servicos(servicos_data)
                    pdf.valor_total(total_data)    
                else:   #  UNIFICA TUDO E SIMPLIFICA SERVIÇOS
                    pdf.add_page()
                    produtos_data = []
                    total_data = 0
                    total_m_obra_data = 0
                    ids_data = []
                    for os in self.os_carregadas:
                        ids_data.append(os.id)
                        total_data += os.total
                        total_m_obra_data += os.total_m_obra
                        for item in os.produtos:
                            produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                    pdf.cabecalho_unificado_os(ids_data)
                    ids_data = []
                    for pedido in self.pedidos_carregados:
                        ids_data.append(pedido.id)
                        total_data += pedido.total
                        total_m_obra_data += pedido.total_m_obra
                        for item in pedido.produtos:
                            produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                    pdf.cabecalho_unificado_pedido(ids_data)
                    pdf.descricao_texto(self.descricao_data)
                    pdf.tabela_produtos(produtos_data)
                    pdf.mao_obra_simples(total_m_obra_data)
                    pdf.valor_total(total_data) 
                return exibir_pdf(pdf, self)
        else:
            if (self.os_carregadas):
                if (self.checkbox_unificar_os_var.get()):
                    self.descricao_data = "OS"
                    self.wait_window(AppTelaDescricao(self))
                    if (self.checkbox_detalhar_os_var.get()):   #  UNIFICA OS E DETALHA SERVIÇOS 
                        pdf.add_page()
                        ids_data = []
                        produtos_data = []
                        servicos_data = []
                        total_data = 0
                        for os in self.os_carregadas:
                            ids_data.append(os.id)
                            total_data += os.total
                            for item in os.produtos:
                                produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                            for item in os.servicos:
                                servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                        pdf.cabecalho_unificado_os(ids_data)
                        pdf.descricao_texto(self.descricao_data)
                        pdf.tabela_produtos(produtos_data)
                        pdf.tabela_servicos(servicos_data)
                        pdf.valor_total(total_data)    
                    else:   #  UNIFICA OS E SIMPLIFICA SERVIÇOS
                        pdf.add_page()
                        ids_data = []
                        produtos_data = []
                        total_data = 0
                        total_m_obra_data = 0
                        for os in self.os_carregadas:
                            ids_data.append(os.id)
                            total_data += os.total
                            total_m_obra_data += os.total_m_obra
                            for item in os.produtos:
                                produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                        pdf.cabecalho_unificado_os(ids_data)
                        pdf.descricao_texto(self.descricao_data)
                        pdf.tabela_produtos(produtos_data)
                        pdf.mao_obra_simples(total_m_obra_data)
                        pdf.valor_total(total_data)    
                else:
                    if (self.checkbox_detalhar_os_var.get()):   #  NÃO UNIFICA OS E DETALHA SERVIÇOS 
                        for os in self.os_carregadas:
                            pdf.add_page()
                            pdf.cabecalho_secao(os)
                            if (os.produtos):
                                produtos_data = []
                                for item in os.produtos:
                                    produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                                pdf.tabela_produtos(produtos_data)
                            if (os.servicos):
                                servicos_data = []
                                for item in os.servicos:
                                    servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                                pdf.tabela_servicos(servicos_data)
                            pdf.valor_total(os.total)    
                    else:   #  NÃO UNIFICA OS E SIMPLIFICA SERVIÇOS
                        for os in self.os_carregadas:
                            pdf.add_page()
                            pdf.cabecalho_secao(os)
                            if (os.produtos):
                                produtos_data = []
                                for item in os.produtos:
                                    produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                                pdf.tabela_produtos(produtos_data)
                            if (os.total_m_obra > 0):
                                pdf.mao_obra_simples(os.total_m_obra)
                            pdf.valor_total(os.total)
            if (self.pedidos_carregados):
                if (self.checkbox_unificar_pedidos_var.get()):
                    self.descricao_data = "Pedidos"
                    self.wait_window(AppTelaDescricao(self))
                    if (self.checkbox_detalhar_pedidos_var.get()):  #  UNIFICA PEDIDOS E DETALHA SERVIÇOS 
                        pdf.add_page()
                        ids_data = []
                        produtos_data = []
                        servicos_data = []
                        total_data = 0
                        for pedido in self.pedidos_carregados:
                            ids_data.append(pedido.id)
                            total_data += pedido.total
                            for item in pedido.produtos:
                                produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                            for item in pedido.servicos:
                                servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                        pdf.cabecalho_unificado_pedido(ids_data)
                        pdf.descricao_texto(self.descricao_data)
                        pdf.tabela_produtos(produtos_data)
                        pdf.tabela_servicos(servicos_data)
                        pdf.valor_total(total_data) 
                    else:   #  UNIFICA PEDIDOS E SIMPLIFICA SERVIÇOS
                        pdf.add_page()
                        ids_data = []
                        produtos_data = []
                        total_data = 0
                        total_m_obra_data = 0
                        for pedido in self.pedidos_carregados:
                            ids_data.append(pedido.id)
                            total_data += pedido.total
                            total_m_obra_data += pedido.total_m_obra
                            for item in pedido.produtos:
                                produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                        pdf.cabecalho_unificado_pedido(ids_data)
                        pdf.descricao_texto(self.descricao_data)
                        pdf.tabela_produtos(produtos_data)
                        pdf.mao_obra_simples(total_m_obra_data)
                        pdf.valor_total(total_data)  
                else:
                    if (self.checkbox_detalhar_pedidos_var.get()):  #  NÃO UNIFICA PEDIDOS E DETALHA SERVIÇOS 
                        for pedido in self.pedidos_carregados:
                            pdf.add_page()
                            pdf.cabecalho_secao(pedido)
                            if (pedido.produtos):
                                produtos_data = []
                                for item in pedido.produtos:
                                    produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                                pdf.tabela_produtos(produtos_data)
                            if (pedido.servicos):
                                servicos_data = []
                                for item in pedido.servicos:
                                    servicos_data.append([item.descricao,item.valor,item.quantidade,item.total])
                                pdf.tabela_servicos(servicos_data)
                            pdf.valor_total(pedido.total)  
                    else:   #  NÃO UNIFICA PEDIDOS E SIMPLIFICA SERVIÇOS
                        for pedido in self.pedidos_carregados:
                            pdf.add_page()
                            pdf.cabecalho_secao(pedido)
                            if (pedido.produtos):
                                produtos_data = []
                                for item in pedido.produtos:
                                    produtos_data.append([item.id,item.descricao,item.ncm,item.valor,item.quantidade,item.total])
                                pdf.tabela_produtos(produtos_data)
                            if (pedido.total_m_obra > 0):
                                pdf.mao_obra_simples(pedido.total_m_obra)
                            pdf.valor_total(pedido.total)
        return exibir_pdf(pdf, self)
#   APP PARA ABRIR INFORMAÇÕES DAS OS E PEDIDOS
class AppTelaItem(tk.Toplevel):
    def __init__(self, master, obj):
        super().__init__(master, padx=10, pady=10)
        #   PARAMETROS
        self.master = master
        #   DEFINIÇÕES DA TELA
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        self.title("Informações")
        self.geometry("450x520")
        self.resizable(width=False, height=False)
        centralizar_tela_app(self)
        #   CONTEUDO    
        frame_pai = ttk.Frame(self)
        frame_pai.pack()
        if (isinstance(obj, Os)):
            ttk.Label(frame_pai, text=f"OS: {obj.id}     Data {obj.data}", font=("Arial", 14, "bold")).pack()
        else:
            ttk.Label(frame_pai, text=f"PED: {obj.id}     Data {obj.data}", font=("Arial", 14, "bold")).pack()
        if (len(obj.cliente) < 24):
            ttk.Label(frame_pai, text=f"Cliente: {obj.cliente}", font=("Arial", 12, "bold")).pack()
        else:
            parte1, parte2 = dividir_string(obj.cliente,24)
            ttk.Label(frame_pai, text=f"Cliente: {parte1}", font=("Arial", 12, "bold")).pack()
            ttk.Label(frame_pai, text=f"{parte2}", font=("Arial", 12, "bold")).pack()
        if (obj.comprador):
            ttk.Label(frame_pai, text=f"Comprador: {obj.comprador}", font=("Arial", 12, "bold")).pack()
        if (obj.texto):
            frame_texto = ttk.Frame(frame_pai, borderwidth=2, relief=tk.RIDGE)
            frame_texto.pack()
            if (len(obj.texto) < 30):
                ttk.Label(frame_texto, text=obj.texto, font=("Arial", 12, "bold")).pack()
            else:
                if(len(obj.texto) > 120):
                    parte1, parte2 = dividir_string(obj.texto, 30)
                    ttk.Label(frame_texto, text=parte1, font=("Arial", 12, "bold")).pack()
                    parte1, parte2 = dividir_string(parte2, 30)
                    ttk.Label(frame_texto, text=parte1, font=("Arial", 12, "bold")).pack()
                    parte1, parte2 = dividir_string(parte2, 30)
                    ttk.Label(frame_texto, text=parte1, font=("Arial", 12, "bold")).pack()
                    ttk.Label(frame_texto, text=f"{parte2[:27]}...", font=("Arial", 12, "bold")).pack()
                else:
                    parte1, parte2 = dividir_string(obj.texto, 30)
                    ttk.Label(frame_texto, text=parte1, font=("Arial", 12, "bold")).pack()
                    while (parte2):
                        parte1, parte2 = dividir_string(parte2, 30)
                        ttk.Label(frame_texto, text=parte1, font=("Arial", 12, "bold")).pack()
        ttk.Label(frame_pai, text=f"Total R$ {obj.total}", font=("Arial", 12, "bold")).pack()
        tree_itens = TreeViewSubItens(self,frame_pai)
        tree_itens.pack()
        if (obj.servicos):
            tree_itens.popular_treeview(obj.servicos)
        if (obj.produtos):
            tree_itens.popular_treeview(obj.produtos)
        #       BOTOES
        ttk.Button(frame_pai, text="Sair", command = self.fechar_tela).pack(pady=12)
        ttk.Button(frame_pai, text="Remover", command = self.remover_item).pack()
    def remover_item(self):
        self.master.remove_app_item = True
        self.fechar_tela()
    def fechar_tela(self):
        self.grab_release()
        self.destroy()
class AppTelaDescricao(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master, padx=10, pady=10)
        #   PARAMETROS
        self.master = master
        #   DEFINIÇÕES DA TELA
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        self.title("Adicionar Informações")
        self.geometry("250x200")
        self.resizable(width=False, height=False)
        centralizar_tela_app(self)
        #   CONTEUDO    
        ttk.Label(self, text=f"Descreva: {master.descricao_data}", font=("Arial", 12, "bold")).pack(expand=True)
        self.entry_texto = tk.Entry(self, width=18, justify="center")
        self.entry_texto.pack(expand=True, pady=10)
        ttk.Button(self, text="Salvar", command = self.fechar_tela).pack(expand=True)
    def fechar_tela(self):
        self.master.descricao_data = self.entry_texto.get()
        self.grab_release()
        self.destroy()
#   TreeViews
class TreeViewItens(tk.Frame):
    def __init__(self, master, frame_pai):
        super().__init__(frame_pai)
        self.master = master
        self.tree_item_map = {}
        #       Treeview para exibir os resultados
        self.tree_itens = ttk.Treeview(self, columns=("item_id", "item_total"), show="headings") 
        #       Define os cabeçalhos das colunas
        self.tree_itens.heading("item_id", text="ID")
        self.tree_itens.heading("item_total", text="Total")
        #       Define a largura das colunas
        self.tree_itens.column("item_id", width=40, anchor="center")
        self.tree_itens.column("item_total", width=70, anchor="center")
        #       Posiciona o Treeview no frame
        self.tree_itens.pack(fill=tk.BOTH, expand=True)
        #       ADICIONA O BIND DO CLIQUE DUPLO NOS ITENS
        self.tree_itens.bind("<Double-1>", self.checarDados) # <Double-1> é duplo clique do botão esquerdo do mouse
    def popular_treeview(self, lista_itens):
        for item_id_treeview in self.tree_itens.get_children():
            self.tree_itens.delete(item_id_treeview)
        self.tree_item_map.clear() # Limpa o mapa ao recarregar
        for item_obj in lista_itens:
            treeview_id = self.tree_itens.insert("", "end", values=(
                item_obj.id,
                f"R$ {item_obj.total:.2f}"
            ))
            self.tree_item_map[treeview_id] = item_obj
    def checarDados(self, event):
        item_selecionado_id_treeview = self.tree_itens.focus()
        if item_selecionado_id_treeview:
            item_obj = self.tree_item_map.get(item_selecionado_id_treeview)
            if item_obj:
                self.master.abrir_item(item_obj)
            else:
                messagebox.showwarning("Item Não Encontrado", "Item não encontrado para a seleção.")
        else:
            messagebox.showinfo("Nenhum Item Selecionado", "Por favor, selecione um item na lista para atualizar/remover.")
class TreeViewSubItens(tk.Frame):
    def __init__(self, master, frame_pai):
        super().__init__(frame_pai)
        self.master = master
        self.tree_item_map = {}
        #       Treeview para exibir os resultados
        self.tree_itens = ttk.Treeview(self, columns=("item_id", "item_descricao", "item_valor", "item_quantidade", "item_total"), show="headings") 
        #       Define os cabeçalhos das colunas
        self.tree_itens.heading("item_id", text="ID")
        self.tree_itens.heading("item_descricao", text="Descrição")
        self.tree_itens.heading("item_valor", text="Valor")
        self.tree_itens.heading("item_quantidade", text="Quantidade")
        self.tree_itens.heading("item_total", text="Total")
        #       Define a largura das colunas
        self.tree_itens.column("item_id", width=40, anchor="center")
        self.tree_itens.column("item_descricao", width=180, anchor="center")
        self.tree_itens.column("item_valor", width=50, anchor="center")
        self.tree_itens.column("item_quantidade", width=70, anchor="center")
        self.tree_itens.column("item_total", width=50, anchor="center")
        # --- ADICIONANDO A BARRA DE ROLAGEM VERTICAL ---
        #       Cria a scrollbar vertical
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree_itens.yview)
        #       Configura o Treeview para usar a scrollbar
        self.tree_itens.configure(yscrollcommand=scrollbar_y.set)
        #       Posiciona o Treeview e a scrollbar no frame
        self.tree_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    def popular_treeview(self, lista_itens):
        for item_obj in lista_itens:
            self.tree_itens.insert("", "end", values=(
                item_obj.id,
                item_obj.descricao,
                f"R$ {item_obj.valor}",
                item_obj.quantidade,
                f"R$ {item_obj.total:.2f}"
            ))
