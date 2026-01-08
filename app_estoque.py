import pyodbc
from config import CONN_STR
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from collections import defaultdict
import re
from fpdf import FPDF
import datetime
from extras import exibir_pdf, centralizar_tela_app

class Produto():
    def __init__(self,id,nome,preco,estoque):
        self.id = int(id)
        self.nome = nome
        self.estoque = int(estoque)
        self.preco = f"R$ {preco:.2f}"
class TreeViewVenda(tk.Frame):
    def __init__(self, frame_pai):
        super().__init__(frame_pai)
        self.tree_item_map = {}
        #       Treeview para exibir os resultados
        self.tree_itens_venda = ttk.Treeview(self, columns=("item_id","item_nome","item_preco","item_estoque"), show="headings") 
        #       Define os cabeçalhos das colunas
        self.tree_itens_venda.heading("item_id", text="ID")
        self.tree_itens_venda.heading("item_nome", text="Descrição")
        self.tree_itens_venda.heading("item_preco", text="Preço")
        self.tree_itens_venda.heading("item_estoque", text="Estoque")
        #       Define a largura das colunas
        self.tree_itens_venda.column("item_id", width=40, anchor="center")
        self.tree_itens_venda.column("item_nome", width=280, anchor="center")
        self.tree_itens_venda.column("item_preco", width=80, anchor="center")
        self.tree_itens_venda.column("item_estoque", width=80, anchor="center")
        # --- ADICIONANDO A BARRA DE ROLAGEM VERTICAL ---
        #       Cria a scrollbar vertical
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree_itens_venda.yview)
        #       Configura o Treeview para usar a scrollbar
        self.tree_itens_venda.configure(yscrollcommand=scrollbar_y.set)
        #       Posiciona o Treeview e a scrollbar no frame
        self.tree_itens_venda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    def popular_treeview(self, lista_produtos):
        for item_id_treeview in self.tree_itens_venda.get_children():
            self.tree_itens_venda.delete(item_id_treeview)
        self.tree_item_map.clear() # Limpa o mapa ao recarregar
        for item_obj in lista_produtos:
            treeview_id = self.tree_itens_venda.insert("", "end", values=(
                item_obj.id,
                item_obj.nome,
                item_obj.preco,
                item_obj.estoque
            ))
            self.tree_item_map[treeview_id] = item_obj
class RelatorioVendas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        #   PARAMETROS E DEFINIÇÕES
        self.master = master
        self.title("Relatório de Vendas") 
        self.geometry("450x50")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        centralizar_tela_app(self)
        #   CONTEUDO
        ttk.Label(self, text="Data Inicial:").pack(side="left", padx=5)
        self.data_inicial = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
        self.data_inicial.pack(side="left", padx=5)
        ttk.Label(self, text="Data Final:").pack(side="left", padx=(10,5))
        self.data_final = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
        self.data_final.pack(side="left", padx=5)
        ttk.Button(self, text="Gerar", command = self.relatorio).pack(expand=True, pady=10)

    def relatorio(self):
        #   DEFINE DATA DE INICIO E FIM
        inicio = datetime.datetime.strptime(self.data_inicial.get(), "%d/%m/%Y")
        inicio = inicio.strftime("%Y-%m-%d")
        fim = datetime.datetime.strptime(self.data_final.get(), "%d/%m/%Y")
        fim = fim.strftime("%Y-%m-%d")
        if(inicio > fim):
            return messagebox.showinfo("Erro", "Data inválida!")
        #print(f"Gerar relatorio formatado entre {inicio} e {fim}")
        #   GERA RELATORIO DE VENDA
        dados_agregados = defaultdict(int)
        try:
            conn = pyodbc.connect(CONN_STR)
            cursor = conn.cursor()
            query_pedidos = f"SELECT [Número do pedido] FROM [Pedidos] WHERE [Data] >= #{inicio}# AND [Data] <= #{fim}#"
            cursor.execute(query_pedidos)
            pedidos = []
            for row in cursor.fetchall():
                pedidos.append(int(row[0]))
            for pedido in pedidos:
                query = f"SELECT [Código do produto], [Quantidade] FROM [Pedidos_itens] WHERE [Número do pedido] = {pedido}"
                cursor.execute(query)
                for row in cursor.fetchall():
                    item_id = row[0]
                    quantidade = row[1]
                    if (item_id != 0):
                        dados_agregados[item_id] += quantidade
            itens_ordenados = sorted(dados_agregados.items(), key=lambda item: item[1], reverse=True)
            resultado_final = [[int(item_id), int(quantidade_total)] for item_id, quantidade_total in itens_ordenados]
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao conectar ou consultar o banco de dados: {sqlstate} - {ex}")
            return messagebox.showinfo("Erro", "Erro de Acesso!")
        finally:
            if conn:
                conn.close()
            if(resultado_final):
                return self.gerar_pdf(resultado_final)
            else:
                return messagebox.showinfo("Erro", "Não foram encontrador itens!")
    def gerar_pdf(self, relatorio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 14, f'LTC TECNOLOGIA - Relatório de Vendas de {self.data_inicial.get()} à {self.data_final.get()}', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 8)
        quebralinha = False
        linha = 1
        for item in relatorio:
            if (linha == 48):
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 13)
                pdf.cell(0, 14, f'LTC TECNOLOGIA - Relatório de Vendas de {self.data_inicial.get()} à {self.data_final.get()}', 0, 1, 'C')
                pdf.set_font("Helvetica", "B", 8)
                linha = 1
            nome = self.item_nome(item[0])
            if quebralinha:
                pdf.cell(10, 5, f'{item[0]}', 0, 0, 'C')
                pdf.cell(70, 5, f' {nome[:35]} ', 0, 0, 'C')
                pdf.cell(10, 5, f'{item[1]}', 0, 1, 'C')
                quebralinha = False
                linha += 1
            else:
                pdf.cell(10, 5, f'{item[0]}', 0, 0, 'C')
                pdf.cell(70, 5, f' {nome[:35]} ', 0, 0, 'C')
                pdf.cell(30, 5, f'{item[1]}', 0, 0, 'C')
                pdf.cell(1, 7, '|', 0, 0, 'C')
                quebralinha = True
        self.master.pdf_relatorio = pdf
        return self.fechar_tela()
    def item_nome(self, id):
        try:
            conn = pyodbc.connect(CONN_STR)
            cursor = conn.cursor()
            cursor.execute(f"SELECT [Descrição do produto] FROM [Produtos] WHERE [Código do produto] = {id}")
            registro = cursor.fetchone()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return "Indefinido"
        finally:
            if conn:
                conn.close()  
        return registro[0]
    def fechar_tela(self):
        self.grab_release()
        self.destroy()

class AppEstoque(tk.Frame):
    def __init__(self, master, reinicia_app):
        super().__init__(master)
        #   PARAMETROS
        self.master = master
        #   CONTEUDO
        frame_app = tk.Frame(self)
        frame_app.pack(expand=True, fill='x')
        #       LABEL TITULO
        ttk.Label(frame_app, text="Consulta de Estoque", font=("Arial", 14, "bold"), justify="center").pack(expand=True, pady=10)
        #       CAMPOS ID E DESCRIÇÃO COM ENTRY PARA FILTRAGEM DOS DADOS
        frame_filtro = tk.Frame(frame_app)
        ttk.Label(frame_filtro, text="Filtros:", font=("Arial", 12), justify="center").pack(side="left", expand=True, pady=10, padx=10)
        ttk.Label(frame_filtro, text="ID", font=("Arial", 12), justify="center").pack(side="left", expand=True, pady=10)
        self.entry_id = tk.Entry(frame_filtro, width=12, justify="center")
        self.entry_id.pack(side="left", expand=True, pady=10, padx=(5,10))
        self.entry_id.bind("<KeyRelease>", self.aplicar_filtro)
        ttk.Label(frame_filtro, text="Descrição", font=("Arial", 12), justify="center").pack(side="left", expand=True, pady=10, padx=(10,0))
        self.entry_descricao = tk.Entry(frame_filtro, width=26, justify="center")
        self.entry_descricao.pack(side="left", expand=True, pady=10, padx=(5,10))
        self.entry_descricao.bind("<KeyRelease>", self.aplicar_filtro)
        #       TREE FRAME DOS ITENS
        self.treeview_itens = TreeViewVenda(frame_app)
        #   INICIA O TREEVIEW COM O ESTOQUE ATUAL
        self.inicia_estoque()
        if (self.estoque):
            frame_filtro.pack(expand=True)
            self.treeview_itens.pack(expand=True)
            ttk.Button(frame_app, text="Imprimir Estoque Atual", command = self.imprime_estoque).pack(expand=True, pady=10)
            ttk.Button(frame_app, text="Relatório de vendas", command = self.relatorio_vendas).pack(expand=True, pady=10)
            ttk.Button(frame_app, text="Atualizar Estoque", command = self.inicia_estoque).pack(expand=True, pady=10)
        else:
            ttk.Label(frame_app, text="Estoque Indisponivel no Momento!", font=("Arial", 24, "bold"), justify="center").pack(expand=True, pady=10)
            ttk.Button(frame_app, text="Reiniciar App Estoque", command = reinicia_app).pack(expand=True, pady=10)

    def inicia_estoque(self):
        self.entry_id.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.estoque = []
        try:
            cnxn = pyodbc.connect(CONN_STR)
            cursor = cnxn.cursor()
            sql_query = "SELECT [Código do produto],[Descrição do produto],[Valor venda],[Estoque] FROM Produtos WHERE [Estoque] <> 0;"
            cursor.execute(sql_query)
            for registro in cursor.fetchall():
                #print(f"| {str(row[0]):<20} | {str(row[1]):<30} | {str(row[2]):<10} |")
                self.estoque.append(Produto(registro[0],registro[1],registro[2],registro[3]))
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao conectar ou executar a query: {sqlstate}")
            print(ex)
        finally:
            # Fechar a conexão e o cursor, se estiverem abertos
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'cnxn' in locals() and cnxn:
                cnxn.close()
            self.estoque = sorted(self.estoque, key=lambda produto: produto.nome)
            self.treeview_itens.popular_treeview(self.estoque)
        return
    def aplicar_filtro(self, event=None):
        filtro_id = self.entry_id.get().strip().upper()
        filtro_desc = self.entry_descricao.get().strip().upper()
        if not (filtro_id or filtro_desc):
            estoque_filtrado = self.estoque
        else:
            #   EXPRESSÃO REGULAR PARA A DESCRIÇÃO
            try:
                regex_pattern = re.escape(filtro_desc).replace(r'\*', '.*')
                compiled_regex = re.compile(regex_pattern, re.IGNORECASE)
                estoque_filtrado = []
                for produto in self.estoque:
                    id_str = str(produto.id)
                    nome_str = produto.nome
                    if ((filtro_id in id_str) and (compiled_regex.search(nome_str))):
                        #print(f"Tem: {filtro_id} em {id_str} ou {filtro_desc} em {nome_str}")
                        estoque_filtrado.append(produto)
            except re.error:
                estoque_filtrado = []
                for produto in self.estoque:
                    id_str = str(produto.id)
                    nome_str = produto.nome
                    if ((filtro_id in id_str) and (filtro_desc in nome_str)):
                        #print(f"Tem: {filtro_id} em {id_str} ou {filtro_desc} em {nome_str}")
                        estoque_filtrado.append(produto)
        self.treeview_itens.popular_treeview(estoque_filtrado)
    def relatorio_vendas(self):
        self.pdf_relatorio = None
        self.wait_window(RelatorioVendas(self)) 
        if (self.pdf_relatorio):
            return exibir_pdf(self.pdf_relatorio, self.master)
    def imprime_estoque(self):
        self.inicia_estoque()
        data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 14, f'LTC TECNOLOGIA - CONTROLE DE ESTOQUE - {data}', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 8)
        quebralinha = False
        linha = 1
        for produto in self.estoque:
            if (linha == 48):
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 13)
                pdf.cell(0, 14, f'LTC TECNOLOGIA - CONTROLE DE ESTOQUE - {data}', 0, 1, 'C')
                pdf.set_font("Helvetica", "B", 8)
                linha = 1
            if quebralinha:
                pdf.cell(10, 5, f'{produto.id}', 0, 0, 'C')
                pdf.cell(70, 5, f' {produto.nome[:35]} ', 0, 0, 'C')
                pdf.cell(10, 5, f'{produto.estoque}', 0, 1, 'C')
                quebralinha = False
                linha += 1
            else:
                pdf.cell(10, 5, f'{produto.id}', 0, 0, 'C')
                pdf.cell(70, 5, f' {produto.nome[:35]} ', 0, 0, 'C')
                pdf.cell(30, 5, f'{produto.estoque}', 0, 0, 'C')
                pdf.cell(1, 7, '|', 0, 0, 'C')
                quebralinha = True
        return exibir_pdf(pdf, self.master)
