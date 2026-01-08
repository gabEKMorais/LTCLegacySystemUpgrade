import os
import win32print
import tempfile
import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import fitz
import pyodbc

from config import CONN_STR
from extras import dividir_string, centralizar_tela_app

#   CLASSES APP_VENDA
#       CLASSES DEFINIÇÃO DE CLIENTE JÁ CADASTRADO NO DB
class ClienteVenda():
    def __init__(self):
        self.id = 1
        self.nome = "Não Identificado"
    def atualiza(self, id, nome):
        self.id = int(id)
        self.nome = nome
class JanelaResultadosClientes(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        #   Frame para o Treeview e a Scrollbar
        frame_tree = tk.Frame(self)
        frame_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        #   Treeview para exibir os resultados
        self.tree = ttk.Treeview(frame_tree, columns=("ID", "Nome", "CPF"), show="headings") 
        #   Define os cabeçalhos das colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        #   Define a largura das colunas
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nome", width=170)
        self.tree.column("CPF", width=40)
        # --- ADICIONANDO A BARRA DE ROLAGEM VERTICAL ---
        #   Cria a scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        #   Configura o Treeview para usar a scrollbar
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        #   Posiciona o Treeview e a scrollbar no frame
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        # --- LIGAÇÃO DO EVENTO DE SELEÇÃO/DUPLO CLIQUE ---
        self.tree.bind("<Double-1>", self.definir_cliente) # <Double-1> é duplo clique do botão esquerdo do mouse
        #   Mensagem de instrução
        tk.Label(self, text="Selecione um cliente e clique duas vezes para definir.").pack(pady=5)

    def exibir_todos_resultados(self, resultados_busca):
        #   Limpa o Treeview (garantir que esteja vazio antes de preencher)
        for item in self.tree.get_children():
            self.tree.delete(item)
        #   Insere TODOS os resultados no Treeview
        for cliente in resultados_busca:
            self.tree.insert("", "end", values=(cliente["ID"], cliente["Nome"], cliente["CPF"]))
    def definir_cliente(self, event):
        item_selecionado_id = self.tree.focus() # Obtém o ID interno do item focado
        if item_selecionado_id:
            # Obtém os valores da linha selecionada
            valores = self.tree.item(item_selecionado_id, 'values')
            # Passa o cliente selecionado de volta para a janela principal e fecha a tela de seleção
            self.master.finaliza(valores)
class AppDefinirClienteVenda(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.title("Sistema de Busca de Clientes")
        self.geometry("400x450")
        self.resizable(width=False, height=False)
        #   CENTRALIZAR TELA
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.geometry(f"+{x}+{y}")
        #   PARAMETROS
        self.master = master
        self.criar_widgets_busca()

    def consultar_clientes_por_nome(self, nome_pesquisa):
        clientes_encontrados = []
        try:
            cnxn = pyodbc.connect(CONN_STR)
            cursor = cnxn.cursor()
            sql_nome_pesquisa = nome_pesquisa.replace("*", "%").replace("[", "[[") # Exemplo simples de escape para '['
            sql_query = "SELECT [Código do cliente], [Nome do cliente], [Cpf] FROM [Clientes] WHERE [Nome do cliente] LIKE [?]"
            cursor.execute(sql_query, sql_nome_pesquisa)
            for registro in cursor.fetchall():
                cliente = {
                    "ID": int(registro[0]),
                    "Nome": registro[1],
                    "CPF": registro[2]
                }
                clientes_encontrados.append(cliente)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            if sqlstate == '08001':
                print("Erro de conexão: Verifique o caminho do banco de dados ou o driver.")
            else:
                print("Erro no banco de dados:", ex)
        finally:
            if 'cnxn' in locals() and cnxn:
                cnxn.close()
        return clientes_encontrados
    def criar_widgets_busca(self):
        #   Label e Entry para o nome da pesquisa
        tk.Label(self, text="Pesquisar por Nome/Sobrenome (use *):").pack(pady=10)
        self.entry_pesquisa = tk.Entry(self, width=120)
        self.entry_pesquisa.pack(pady=5, padx=20)
        self.entry_pesquisa.focus_set() # Foca na entrada ao iniciar
        #   Botão de pesquisa
        tk.Button(self, text="Pesquisar", command=self.realizar_pesquisa).pack(pady=10)
        #   CONTEINER DE RESULTADOS COM TKFRAME DO TKTREEVIEW
        self.conteiner_resultados = JanelaResultadosClientes(self)
        self.conteiner_resultados.pack(expand=True, fill=tk.X)
        #   BOTAO CANCELAR
        tk.Button(self, text="Cancelar", command=self.destroy).pack(pady=10)
    def realizar_pesquisa(self):
        termo_pesquisa = (self.entry_pesquisa.get().upper() + "*")
        if not termo_pesquisa:
            messagebox.showwarning("Aviso", "Por favor, digite um termo para pesquisa.")
            return
        resultados = self.consultar_clientes_por_nome(termo_pesquisa)
        if resultados:
            self.conteiner_resultados.exibir_todos_resultados(resultados)
        else:
            messagebox.showinfo("Resultados", "Nenhum cliente encontrado com o critério '{}'.".format(termo_pesquisa))
    def finaliza(self, cliente):
        self.master.cliente_selecionado = cliente
        self.destroy()
#       CLASSES DE SELEÇÃO DE ITENS DA VENDA
class ServicoVenda:
    def __init__(self):
        self.id = 0
        self.novo = True
        self.tipo = "servico"
    def escolhe(self, id):
        self.id = id
        self.quantidade = 1
        consulta = False
        try:
            cnxn = pyodbc.connect(CONN_STR)
            cursor = cnxn.cursor()
            cursor.execute(f'SELECT "Descrição do serviço", "Valor" FROM Servicos WHERE "Código do servico" = {id}')
            consulta = cursor.fetchall()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            if sqlstate == '08001':
                print("Erro de conexão: Verifique o caminho do banco de dados ou o driver.")
            else:
                print("Erro no banco de dados:", ex)
        finally:
            if 'cnxn' in locals() and cnxn:
                cnxn.close()
        if (consulta):
            self.nome = consulta[0][0]
            self.preco = float(consulta[0][1])
            self.total = self.preco
            return
        else:
            return False
    def atualiza(self, nome, quantidade, preco):
        self.nome = nome
        self.quantidade = int(quantidade)
        self.preco = float(preco)
        self.total = self.quantidade*self.preco
class ProdutoVenda:
    def __init__(self, id):
        self.id = id
        self.novo = True
        self.tipo = "produto"
        self.quantidade = 1
        consulta = False
        try:
            cnxn = pyodbc.connect(CONN_STR)
            cursor = cnxn.cursor()
            cursor.execute(f'SELECT "Descrição do produto","Valor venda" FROM "Produtos" WHERE "Código do produto" = {id}')
            consulta = cursor.fetchall()
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            if sqlstate == '08001':
                print("Erro de conexão: Verifique o caminho do banco de dados ou o driver.")
            else:
                print("Erro no banco de dados:", ex)
        finally:
            if 'cnxn' in locals() and cnxn:
                cnxn.close()
        if (consulta):
            self.nome = consulta[0][0]
            self.preco = float(consulta[0][1])
            self.total = self.preco
            return
        else:
            return False
    def atualiza(self, nome, quantidade, preco):
        self.nome = nome
        self.quantidade = int(quantidade)
        self.preco = float(preco)
        self.total = self.quantidade*self.preco
class TreeViewVenda(tk.Frame):
    def __init__(self, master, frame_pai):
        super().__init__(frame_pai)
        self.master = master
        self.tree_item_map = {}
        #       Treeview para exibir os resultados
        self.tree_itens_venda = ttk.Treeview(self, columns=("item_id", "item_nome", "item_preço", "item_quantidade", "item_total"), show="headings") 
        #       Define os cabeçalhos das colunas
        self.tree_itens_venda.heading("item_id", text="ID")
        self.tree_itens_venda.heading("item_nome", text="Descrição")
        self.tree_itens_venda.heading("item_preço", text="Preço")
        self.tree_itens_venda.heading("item_quantidade", text="Quantidade")
        self.tree_itens_venda.heading("item_total", text="Total")
        #       Define a largura das colunas
        self.tree_itens_venda.column("item_id", width=40, anchor="center")
        self.tree_itens_venda.column("item_nome", width=170, anchor="center")
        self.tree_itens_venda.column("item_preço", width=70, anchor="center")
        self.tree_itens_venda.column("item_quantidade", width=70, anchor="center")
        self.tree_itens_venda.column("item_total", width=70, anchor="center")
        # --- ADICIONANDO A BARRA DE ROLAGEM VERTICAL ---
        #       Cria a scrollbar vertical
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree_itens_venda.yview)
        #       Configura o Treeview para usar a scrollbar
        self.tree_itens_venda.configure(yscrollcommand=scrollbar_y.set)
        #       Posiciona o Treeview e a scrollbar no frame
        self.tree_itens_venda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        #       ADICIONA O BIND DO CLIQUE DUPLO NOS ITENS
        self.tree_itens_venda.bind("<Double-1>", self.atualizar) # <Double-1> é duplo clique do botão esquerdo do mouse
    def popular_treeview(self, lista_produtos, lista_servicos):
        for item_id_treeview in self.tree_itens_venda.get_children():
            self.tree_itens_venda.delete(item_id_treeview)
        self.tree_item_map.clear() # Limpa o mapa ao recarregar
        for item_obj in lista_produtos:
            treeview_id = self.tree_itens_venda.insert("", "end", values=(
                item_obj.id,
                item_obj.nome,
                f"R$ {item_obj.preco:.2f}",
                item_obj.quantidade,
                f"R$ {item_obj.total:.2f}"
            ))
            self.tree_item_map[treeview_id] = item_obj
        for item_obj in lista_servicos:
            treeview_id = self.tree_itens_venda.insert("", "end", values=(
                item_obj.id,
                item_obj.nome,
                f"R$ {item_obj.preco:.2f}",
                item_obj.quantidade,
                f"R$ {item_obj.total:.2f}"
            ))
            self.tree_item_map[treeview_id] = item_obj
    def atualizar(self, event):
        item_selecionado_id_treeview = self.tree_itens_venda.focus()
        if item_selecionado_id_treeview:
            item_obj = self.tree_item_map.get(item_selecionado_id_treeview)
            if item_obj:
                self.master.atualiza_item_venda(item_obj)
            else:
                messagebox.showwarning("Item Não Encontrado", "Objeto Item não encontrado para a seleção.")
        else:
            messagebox.showinfo("Nenhum Item Selecionado", "Por favor, selecione um item na lista para atualizar/remover.")
class AppTelaItem(tk.Toplevel):
    def __init__(self, master, item):
        super().__init__(master)
        #   PARAMETROS
        self.ponteiro = item
        self.master = master
        #   DEFINIÇÕES DA TELA
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        if (item.novo):
            self.title("Adicionar Produto")
        else:
            self.title("Editar Produto")
        self.geometry("320x220")
        self.resizable(width=False, height=False)
        centralizar_tela_app(self)
        #   CONTEUDO    
        #       NOME   
        frame_nome = ttk.Frame(self)
        ttk.Label(frame_nome, text="Nome:").pack(padx=(10,2), side="left")
        self.entry_nome = tk.Entry(frame_nome, justify='center')
        self.entry_nome.insert(0,self.ponteiro.nome)
        self.entry_nome.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_nome.pack(padx=10, pady=10, expand=True, fill='x')
        #       QUANTIDADE
        frame_quantidade = ttk.Frame(self)
        ttk.Label(frame_quantidade, text="Quantidade:").pack(padx=(10,2), side="left")
        self.entry_quantidade = tk.Entry(frame_quantidade, justify='center')
        self.entry_quantidade.insert(0,str(self.ponteiro.quantidade))
        self.entry_quantidade.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_quantidade.pack(padx=10, pady=10, expand=True, fill='x')
        #       PREÇO
        frame_preco = ttk.Frame(self)
        ttk.Label(frame_preco, text="Preço:").pack(padx=(10,2), side="left")
        self.entry_preco = tk.Entry(frame_preco, justify='center')
        self.entry_preco.insert(0,str(self.ponteiro.preco).replace(".", ","))
        self.entry_preco.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_preco.pack(padx=10, pady=10, expand=True, fill='x')
        #       BOTOES
        ttk.Button(self, text="Salvar", command = self.salvar_item).pack(padx=10)
        if (item.novo):
            ttk.Button(self, text="Cancela", command = self.fechar_tela).pack(padx=10)
        else:
            ttk.Button(self, text="Remover", command = self.remover_item).pack(padx=10)
    def salvar_item(self):
        try:
            self.ponteiro.atualiza(self.entry_nome.get(),self.entry_quantidade.get(),self.entry_preco.get().replace(",", "."))
            self.master.confirma_app_item = True
            self.ponteiro.novo = False
            self.fechar_tela()
        except:
            messagebox.showinfo("Erro", "Verifique as informações digitadas")
    def remover_item(self):
        self.master.remove_app_item = True
        self.fechar_tela()
    def fechar_tela(self):
        self.grab_release()
        self.destroy()
class AppTelaSelecionaServ(tk.Toplevel):
    def __init__(self, master, item):
        super().__init__(master)
        self.ponteiro = item
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        #   DEFINIÇÕES DA TELA
        self.title("Adicionar Serviço")
        self.geometry("230x180")
        self.resizable(width=False, height=False)
        centralizar_tela_app(self)
        #   CONTEUDO
        ttk.Label(self, text="Escolha um serviço:", font=("Arial", 12, "bold")).pack()
        ttk.Button(self, text="Xerox", command=lambda: self.servico(108)).pack(pady=10)
        ttk.Button(self, text="Solda/Limpeza", command=lambda: self.servico(20)).pack(pady=(0,10))
        ttk.Button(self, text="Taxa Teste Banca", command=lambda: self.servico(23)).pack(pady=(0,10))
        ttk.Button(self, text="Cancelar", command = self.fechar_tela).pack()
    def servico(self, id):
        self.ponteiro.escolhe(id)
        return self.fechar_tela()    
    def fechar_tela(self):
        self.grab_release()
        self.destroy()
class AppVendas(tk.Frame):
    def __init__(self, master, reinicia_app):
        super().__init__(master)

        #   PARAMETROS INICIAIS
        self.func_reiniciar = reinicia_app
        self.itens_venda_produto = []
        self.itens_venda_servico = []
        self.cliente = ClienteVenda()
        self.total_venda = 0
        self.venda_desconto = tk.StringVar()

        #   ESTILO - PARA OS BOTOES DO FINAL
        style = ttk.Style()
        style.configure('Finalizar.TButton',
                    background='lightgreen',
                    foreground='black', # Cor do texto
                    font=('Arial', 10, 'bold'))
        style.map('Finalizar.TButton',
              background=[('active', 'palegreen')]) # Um verde um pouco mais claro ao passar o mouse
        style.configure('Cancelar.TButton',
                    background='lightcoral', # Um vermelho mais suave
                    foreground='black',
                    font=('Arial', 10, 'bold'))
        style.map('Cancelar.TButton',
              background=[('active', 'salmon')]) # Um vermelho um pouco mais claro ao passar o mouse

        #   FRAMES PRINCIPAIS
        frame_itens_venda = ttk.Frame(self)
        frame_itens_venda.pack(side="left", expand=True)
        ttk.Frame(self, borderwidth=2, relief="solid").pack(side="left", fill='y', expand=True, padx=8) # LINHA DIVISORIA
        frame_info_venda = ttk.Frame(self)
        frame_info_venda.pack(side="left", expand=True)

        #   DADOS DA VENDA - FRAMES E ITENS DE ITENS_VENDA
        #       TEXTO HEADER
        ttk.Label(frame_itens_venda, text="PRODUTOS E SERVIÇOS DA VENDA", font=("Arial", 12, "bold")).pack(expand=True, pady=10)
        #       FRAME PRODUTOS
        frame_adicionar_produto = ttk.Frame(frame_itens_venda)
        frame_adicionar_produto.pack(expand=True)
        ttk.Label(frame_adicionar_produto, text="Produto (id):", font=("Arial", 12), justify="center").pack(side="left", expand=True, pady=10)
        self.entry_produto = tk.Entry(frame_adicionar_produto, width=18, justify="center")
        self.entry_produto.pack(side="left", expand=True, pady=10, padx=(5,10))
        ttk.Button(frame_adicionar_produto, text="Adicionar", command=lambda: self.novo_produto(self.entry_produto.get())).pack(side="left", expand=True, pady=10)
        #       BOTAO SERVIÇOS
        ttk.Button(frame_itens_venda, text="Adicionar Serviço", command = self.novo_servico).pack(expand=True, pady=(2,15))
        #       TREE FRAME DOS ITENS
        self.treeview_itens = TreeViewVenda(self, frame_itens_venda)
        self.treeview_itens.pack(expand=True)
        #       TOTAL VENDA
        self.label_total_venda = ttk.Label(frame_itens_venda, text=f"Total Venda R${self.total_venda}", font=("Arial", 14, "bold"))
        self.label_total_venda.pack(expand=True, pady=10)
        #       DESCONTO
        frame_desconto_entry = ttk.Frame(frame_itens_venda)
        frame_desconto_entry.pack(expand=True)
        ttk.Label(frame_desconto_entry, text="Desconto:", font=("Arial", 12)).pack(side="left", expand=True, padx=10)
        tk.Entry(frame_desconto_entry, justify='center', textvariable=self.venda_desconto, width=18).pack(side="left", expand=True)
        frame_desconto_label = ttk.Frame(frame_itens_venda)
        frame_desconto_label.pack(expand=True, pady=10)
        ttk.Label(frame_desconto_label, text="Total Com Desconto R$", font=("Arial", 14)).pack(side="left", expand=True, padx=10)
        self.label_total_com_desconto = ttk.Label(frame_desconto_label, text=self.total_venda, font=("Arial", 14))
        self.label_total_com_desconto.pack(side="left", expand=True, padx=10)
        self.venda_desconto.trace_add("write", self.atualizar_label_desconto)
        #   ------------    FIM DOS DADOS DA VENDA
        #   DADOS DO RECIBO
        ttk.Label(frame_info_venda, text="DADOS DO RECIBO", font=("Arial", 12, "bold")).pack(expand=True, pady=10)
        #       MENU METODO PAGAMENTO
        frame_metodo_pagamento = ttk.Frame(frame_info_venda)
        frame_metodo_pagamento.pack(expand=True, padx=10)
        self.metodo_pagamento = tk.StringVar(self)
        opcoes_metodo_pagamento = ["Dinheiro", "Cartão", "Pix"]
        self.metodo_pagamento.set(opcoes_metodo_pagamento[0])
        ttk.Label(frame_metodo_pagamento, text="Método de Pagamento: ", font=("Arial", 12)).pack(side="left", expand=True, padx=10)
        tk.OptionMenu(frame_metodo_pagamento, self.metodo_pagamento, *opcoes_metodo_pagamento).pack(side="left", expand=True, padx=10)
        #       COMPRADOR VENDA
        frame_comprador_venda = ttk.Frame(frame_info_venda)
        frame_comprador_venda.pack(expand=True, padx=10)
        ttk.Label(frame_comprador_venda, text="Comprador:", font=("Arial", 12)).pack(side="left", expand=True, pady=10, padx=12)
        self.entry_comprador_venda = tk.Entry(frame_comprador_venda, justify='center')
        self.entry_comprador_venda.pack(side="left", expand=True, pady=10)
        #       OBSERCAÇÃO VENDA
        frame_observacao_venda = ttk.Frame(frame_info_venda)
        frame_observacao_venda.pack(expand=True, padx=10)
        ttk.Label(frame_observacao_venda, text="Observação:", font=("Arial", 12)).pack(side="left", expand=True, pady=10, padx=12)
        self.entry_obs_venda = tk.Entry(frame_observacao_venda, justify='center')
        self.entry_obs_venda.pack(side="left", expand=True, pady=10)
        #       CLIENTE SIS
        frame_cliente_sistema = ttk.Frame(frame_info_venda)
        frame_cliente_sistema.pack(expand=True, padx=10)
        ttk.Label(frame_cliente_sistema, text="Cliente:", font=("Arial", 12)).pack(side="left", pady=10)
        self.label_cliente_nome = ttk.Label(frame_cliente_sistema, text=self.cliente.nome, font=("Arial", 12))
        self.label_cliente_nome.pack(side="left", pady=10, padx=12)
        ttk.Button(frame_info_venda, text="Identificar Cliente", command = self.selecionar_cliente).pack(expand=True, pady=10)
        #       CHECKBOXES
        frame_checkbox = ttk.Frame(frame_info_venda)
        frame_checkbox.pack(expand=True, padx=10)
        self.checkbox_gera_pedido_var = tk.BooleanVar(value=True) # CHECKBOX GERAR PEDIDO
        tk.Checkbutton(frame_checkbox, text = "Gerar Pedido", variable = self.checkbox_gera_pedido_var).pack(side="left", expand=True, padx=15)
        self.checkbox_controle_interno_var = tk.BooleanVar(value=True) # CHECKBOX IMPRIMIR CONTROLE INTERNO
        tk.Checkbutton(frame_checkbox, text = "Controle Interno", variable = self.checkbox_controle_interno_var).pack(side="left", expand=True, pady=15)
        #       BOTAO FINALIZA E CANCELAR VENDA
        frame_botoes_final = ttk.Frame(frame_info_venda)
        frame_botoes_final.pack(expand=True, padx=10)
        ttk.Button(frame_botoes_final, text="Recibo", style='Finalizar.TButton', command = self.abrir_recibo).pack(side="left", expand=True, padx=40)
        ttk.Button(frame_botoes_final, text="Cancela/Limpa", style='Cancelar.TButton', command = self.func_reiniciar).pack(side="left", expand=True, padx=40)
    def selecionar_cliente(self):
        self.cliente_selecionado = None
        self.wait_window(AppDefinirClienteVenda(self))
        if (self.cliente_selecionado):
            self.cliente.atualiza(self.cliente_selecionado[0],self.cliente_selecionado[1])
            self.label_cliente_nome.config(text=self.cliente.nome)
        return
    def novo_produto(self, id):
        try:
            id = int(id)
            try:
                item = ProdutoVenda(id)
                if (item):
                    self.entry_produto.delete(0, tk.END)
                    self.confirma_app_item = False
                    self.wait_window(AppTelaItem(self, item))
                    if (self.confirma_app_item):
                        self.itens_venda_produto.append(item)
                        return self.atualiza_tabela_itens()
                    return
                else:
                    messagebox.showinfo("Erro", "O código de produto informado é inválido (tela)")
            except:
                messagebox.showinfo("Erro", "O código de produto informado é inválido (db/tela)")
        except:
            messagebox.showinfo("Erro", "O código de produto informado é inválido (int)")
    def novo_servico(self):
        item = ServicoVenda()
        self.wait_window(AppTelaSelecionaServ(self, item))
        if (item.id != 0):
            self.confirma_app_item = False
            self.wait_window(AppTelaItem(self, item))
            if (self.confirma_app_item):
                self.itens_venda_servico.append(item)
                return self.atualiza_tabela_itens()
            return
        else:
            return 
    def atualiza_item_venda(self, item):
        self.confirma_app_item = False
        self.remove_app_item = False
        self.wait_window(AppTelaItem(self, item))
        if (self.confirma_app_item):
            #print("Atualizou " + item.nome)
            return self.atualiza_tabela_itens()
        if (self.remove_app_item):
            #print("Removeu " + item.nome)
            return self.remove_item_venda(item)
        return
    def atualiza_tabela_itens(self):
        self.treeview_itens.popular_treeview(self.itens_venda_produto,self.itens_venda_servico)
        return self.atualiza_total_venda()
    def atualiza_total_venda (self):
        total_atual = 0
        for item in self.itens_venda_produto:
            total_atual += item.total
        for item in self.itens_venda_servico:
            total_atual += item.total
        self.total_venda = total_atual
        self.label_total_venda.config(text=f"Total R${self.total_venda:.2f}")
        return self.atualizar_label_desconto()
    def atualizar_label_desconto(self, *args):
        valor_atual = self.venda_desconto.get().replace(",",".")
        try:
            valor_venda = self.total_venda - float(valor_atual)
        except:
            valor_venda = self.total_venda
        valor_venda = f"{valor_venda:.2f}".replace(".",",")
        self.label_total_com_desconto.config(text=valor_venda)
    def remove_item_venda(self, item):
        if (item.tipo == "produto"):
            self.itens_venda_produto.remove(item)
        else:
            self.itens_venda_servico.remove(item)
        del item
        return self.atualiza_tabela_itens()
    def abrir_recibo(self):
        if (self.itens_venda_produto or self.itens_venda_servico):
            self.wait_window(AppTelaRecibo(self))
            try:
                os.remove(self.pdf_path)
            except FileNotFoundError:
                print(f"Arquivo {self.pdf_path} não encontrado.")
            finally:
                messagebox.showinfo("Aviso", "Venda concluida!")
                self.func_reiniciar()
        else:
             messagebox.showinfo("Erro", "Você ainda não adicionou nenhum produto!")
#   CLASSE GERAÇÃO PDF E TELA RECIBO
class AppTelaRecibo(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        #   PARAMETROS E DEFINIÇÕES
        self.master = master
        self.title("RECIBO") 
        self.geometry("250x600")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        centralizar_tela_app(self)
        #   DADOS DO RECIBO
        #       DATA
        self.data = datetime.datetime.now().strftime("%d/%m/%Y")
        #       DEFININDO COMPRADOR
        entry_comprador = str(master.entry_comprador_venda.get())
        if (len(entry_comprador) < 2):
            self.comprador = "Não identificado"
        else:
            self.comprador = entry_comprador[:20]
        #       DEFININDO OBS VENDA
        self.observacao_venda = ("Não impresso " + str(master.entry_obs_venda.get()))
        #       DESCONTO
        try:
            #print(master.venda_desconto.get())
            self.desconto = float(master.venda_desconto.get().replace(",","."))
        except:
            self.desconto = 0
        #       CALCULO DO TOTAL E VALOR PAGO APOS DESCONTO
        self.total = 0
        for item in master.itens_venda_produto:
            self.total += item.total
        for item in master.itens_venda_servico:
            self.total += item.total
        try:   
            self.valor_pago = float(self.total) - float(self.desconto)
        except:
            self.valor_pago = self.total
        #   GERAÇÃO DO PEDIDO
        if (master.checkbox_gera_pedido_var.get()):
            try:
                self.registro = RegistrarVenda(self, master)
            except Exception as ex:
                print(f"Erro: {ex}")
        #   GERAÇÃO DO PDF E VIZUALIZAÇÃO
        self.pdf_path = self.gerar_pdf(master)
        doc = fitz.open(self.pdf_path)
        pix = doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pagina = ImageTk.PhotoImage(img) 
        #   BOTOES
        botao_imprimir = ttk.Button(self, text="Imprimir", command=lambda: self.imprimir_recibo(self.pdf_path))
        botao_imprimir.pack()
        botao_sair = ttk.Button(self, text="Sair", command = self.fechar_tela)
        botao_sair.pack()
        try:
            label_imagem = ttk.Label(self)
            label_imagem.config(image = pagina)
            label_imagem.image = pagina
            label_imagem.pack() 
        except Exception as ex:
            print(ex)

    def gerar_pdf(self, master):
        largura_mm = 80
        altura_mm = 327#297
        largura_pt = largura_mm * 2.83465
        altura_pt = altura_mm * 2.83465
        pdf = FPDF(orientation='P', unit='pt', format=(largura_pt, altura_pt))
        pdf.add_page()
        #   Titulo              .set_font("Helvetica", "B", 14)
        #   Numeros             .set_font("Helvetica", "B", 12)
        #   Texto               .set_font("Courier", "B", 12)
        #   LOGO E HEADER
        pdf.image('logo.png', 20, 10, 40)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 14, 'LTC TECNOLOGIA', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, 'RECIBO DE PAGAMENTO', 0, 1, 'C')
        pdf.cell(0, 28, '', 0, 1, 'C')
        #   CORPO - VALORES
        #       VALOR PAGO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 14, 'Recebemos a quantia de', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, f'R${self.valor_pago:.2f}', 0, 1, 'C')
        #       DATA PAGAMENTO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(50, 14, 'No dia', 0, 0, 'C')
        pdf.cell(0, 14, self.data, 0, 1, 'C')
        pdf.cell(0, 20, '', 0, 1, 'C')
        #       DADOS PEDIDO
        if (master.checkbox_gera_pedido_var.get()):
            if (self.registro.registrado):
                pdf.set_font("Courier", "B", 12) 
                pdf.cell(0, 20, 'Referente ao pedido', 0, 1, 'C')  
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 14, f'Nº {self.registro.numero_pedido}', 0, 1, 'C')
            else:
                pdf.set_font("Courier", "B", 12)       
                pdf.cell(0, 10, 'Referente ao pedido', 0, 1, 'C')
        else:
                pdf.set_font("Courier", "B", 12)       
                pdf.cell(0, 10, 'Referente ao pedido', 0, 1, 'C')
        #       VALOR PEDIDO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 20, 'De valor', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 14, f'R${self.total:.2f}', 0, 1, 'C')
        #       DESCONTO
        if (isinstance(self.desconto, float)):
            if (self.desconto > 0):
                pdf.set_font("Courier", "B", 12)
                pdf.cell(0, 20, 'Decrescido em', 0, 1, 'C')
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 14, f'R${self.desconto:.2f}', 0, 1, 'C')
                pdf.set_font("Courier", "B", 12)
                pdf.cell(0, 20, 'De desconto', 0, 1, 'C')
        #       DESCRIÇÃO DOS PRODUTOS
        if (master.itens_venda_produto):
            pdf.cell(0, 20, '', 0, 1, 'C')
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 20, 'Descrição Produto', 0, 1, 'C')
            pdf.cell(0, 20, ' Código | Preço | Un | Total', 0, 1, 'C')
            for produto in master.itens_venda_produto:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        #       DESCRIÇÃO DOS SERVIÇOS
        if (master.itens_venda_servico):
            pdf.cell(0, 20, '', 0, 1, 'C')
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 20, 'Descrição Serviço', 0, 1, 'C')
            pdf.cell(0, 20, ' Código | Preço | Un | Total', 0, 1, 'C')
            for produto in master.itens_venda_servico:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        #   PARA CONTROLE INTERNO
        if (master.checkbox_controle_interno_var.get()):
            pdf.add_page()
            pdf.cell(0, 20, 'CONTROLE INTERNO', 0, 1, 'C')
            #       DATA
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 14, (datetime.datetime.now().strftime("%d/%m/%y %H:%M")), 0, 1, 'C')
            #       NUMERO PEDIDO
            if (master.checkbox_gera_pedido_var.get()):
                if (self.registro.registrado):
                    pdf.set_font("Courier", "B", 12) 
                    pdf.cell(0, 20, 'Referente ao pedido', 0, 1, 'C')  
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 14, f'Pedido Nº {self.registro.numero_pedido}', 0, 1, 'C')
            #       VALOR PAGO
            pdf.cell(0, 14, 'Valor pago', 0, 1, 'C')
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 20, f'R${self.valor_pago:.2f}', 0, 1, 'C')
            #       METODO DE PAGAMENTO
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 14, f'Método: {master.metodo_pagamento.get()}', 0, 1, 'C')
            #       DESCRIÇÃO DOS PRODUTOS
            pdf.set_font("Courier", "B", 12)
            for produto in master.itens_venda_produto:
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
            #       DESCRIÇÃO DOS SERVIÇOS
            for produto in master.itens_venda_servico:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        return self.criar_pdf_temporario_fpdf(pdf)
    def criar_pdf_temporario_fpdf(self, pdf):
        conteudo_pdf = pdf.output(dest='S') # Obter a saída em bytes
        arquivo_temporario = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        arquivo_temporario.write(conteudo_pdf)
        arquivo_temporario.close()
        return arquivo_temporario.name
    def imprimir_recibo(self, pdf_temporario):
        #   FAZ A IMPRESSÃO
        impressora_padrao_atual = win32print.GetDefaultPrinter()
        try:
            win32print.SetDefaultPrinter("RECIBOS")
            caminho_pdf_abs = os.path.abspath(pdf_temporario)
            os.startfile(caminho_pdf_abs, "print")
        finally:
            # Restaura a impressora padrão original
            win32print.SetDefaultPrinter(impressora_padrao_atual)
    def fechar_tela(self):
        self.master.pdf_path = self.pdf_path
        self.grab_release()
        self.destroy()
#   CLASSE REGISTRA VENDA NO DB
class RegistrarVenda():
    def __init__(self, recibo, app_venda):
        self.registrado = False
        self.venda = recibo
        self.app_master = app_venda
        self.con = pyodbc.connect(CONN_STR)
        self.cur = self.con.cursor()  
        self.numero_pedido = (self.definir_numero_pedido() + 1)
        if isinstance(self.numero_pedido, int):
            self.numero_pedido_nominal = f"PED{str(self.numero_pedido)}-01"
        else:
            return
        if not (self.tabela_pedidos()):
            return
        if not (self.atualiza_sequencial()):
            return
        self.con.commit()
        cont_indice_item = 1
        for item in app_venda.itens_venda_produto:
            if not (self.tabela_pedidos_itens(item, cont_indice_item)):
                print("Parou: Produto")
                return
            self.baixa_estoque(item)
            cont_indice_item += 1
        for item in app_venda.itens_venda_servico:
            if not (self.tabela_pedidos_itens(item, cont_indice_item)):
                print("Parou: Serviço")
                return
            cont_indice_item += 1
        self.con.commit()
        if not (self.tabela_cre()):
            print("Parou: Cre")
            return
        if not (self.tabela_pagamentos_cre()):
            print("Parou: Pagamentos Cre")
            return
        self.registrado = True
        return self.fechar_conexao()

    def atualiza_sequencial(self):
        #print(f"Iniciado: Sequencial")
        try:
            nome_tabela = "SYS~Sequencial"
            set_colunas = {"Valor": str(self.numero_pedido), "Valor Anterior": str(self.numero_pedido-1)}
            where_coluna = "Tabela"
            where_valor = "Pedidos"
            set_parts = [f"[{col}] = ?" for col in set_colunas.keys()]
            set_clause = ", ".join(set_parts)
            valores = list(set_colunas.values())
            valores.append(where_valor)
            sql_update = f"UPDATE [{nome_tabela}] SET {set_clause} WHERE [{where_coluna}] = ?;"
            self.cur.execute(sql_update, valores)
            #print(f"DEBUG: Atualização em '{nome_tabela}' bem-sucedida para '{where_coluna}' = '{where_valor}'")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao inserir registro sqc: {sqlstate}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False  
        return True         
    def inserir(self, nome_tabela, colunas_para_inserir, valores_para_inserir):
        #print(f"Iniciado: {nome_tabela}")
        try:
            nomes_colunas_str = "(" + ", ".join([f"[{c}]" for c in colunas_para_inserir]) + ")"
            placeholders_str = "(" + ", ".join(["?"] * len(valores_para_inserir)) + ")"
            sql_insert = f"INSERT INTO {nome_tabela} {nomes_colunas_str} VALUES {placeholders_str}"
            self.cur.execute(sql_insert, valores_para_inserir)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao inserir registro inserttables: {sqlstate}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False
        #print(f"Finalizado: {nome_tabela}")
        return True
    def tabela_pedidos(self):    
        nome_tabela = "[Pedidos]"
        valores_para_inserir = [
            self.numero_pedido,
            self.venda.data,
            self.app_master.cliente.id,
            self.venda.comprador,
            1,
            "01",
            self.venda.total,
            self.venda.observacao_venda,
            1,
            self.venda.data
        ]
        colunas_para_inserir = [
            "Número do pedido", # numero
            "Data", # data/hora
            "Código do cliente", # numero
            "Comprador", # texto curto
            "Código da condição", # numero
            "Código da forma de pgto", # texto curto
            "Total", # numero
            "Observações", # texto longo
            "Código do vendedor", # numero
            "Data conclusão" # data/hora
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def tabela_pedidos_itens(self, item, indice_item):
        nome_tabela = "[Pedidos_itens]"
        if (item.tipo == "produto"):
            valores_para_inserir = [
                self.numero_pedido,
                item.id,
                item.quantidade,
                item.preco,
                item.preco,
                0,
                "UN",
                indice_item
            ]
        else:
            valores_para_inserir = [
                self.numero_pedido,
                0,
                item.quantidade,
                item.preco,
                item.preco,
                item.id,
                "UN",
                indice_item
            ]
        colunas_para_inserir = [
            "Número do pedido",
            "Código do produto",
            "Quantidade",
            "Valor unitário",
            "Valor",
            "Código do servico",
            "Um",
            "Sequencial"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def baixa_estoque(self, item):
        nome_tabela = "Produtos" # Colchetes para o nome com espaço
        coluna_valor = "Estoque"
        coluna_where = "Código do produto"
        valor_where = item.id
        try:
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            #print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            #print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
            self.cur.execute(sql_select, (valor_where,))
            resultado = self.cur.fetchone()
            if resultado:
                set_coluna = "Estoque"
                valor = resultado[0] - item.quantidade
                where_coluna = "Código do produto"
                where_valor = item.id
                set_clause = f"[{set_coluna}] = ?"
                sql_update = f"UPDATE [{nome_tabela}] SET {set_clause} WHERE [{where_coluna}] = ?;"
                valores = (valor, where_valor)
                self.cur.execute(sql_update, valores)
                return resultado[0], valor
            else:
                return 0
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo bestq: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return 0
    def tabela_cre(self):
        nome_tabela = "[Cre]"
        valores_para_inserir = [
            self.numero_pedido_nominal,
            1,
            self.venda.data,
            self.venda.data,
            self.app_master.cliente.id,
            1,
            "GERADO AUTOMATICAMENTE PELO SISTEMA DE VENDAS",
            self.venda.total,
            self.venda.desconto,
            self.venda.valor_pago,
            0,
            self.venda.data,
            self.venda.data,
            self.numero_pedido,
            1,
            "01",
            0,
            1,
            0,
            True,
            0
        ]
        colunas_para_inserir = [
            "Número do documento",
            "Parcela",
            "Data do lançamento",
            "Vencimento",
            "Código do cliente",
            "Código do vendedor",
            "Observações",
            "Valor",
            "Abatimentos",
            "Valor pago",
            "Saldo",
            "Datajuros",
            "Datadescontos",
            "Número do pedido",
            "Código da condição",
            "Código da forma de pgto",
            "Número da os",
            "Código do banco",
            "Número impresso",
            "Baixa automaticamente",
            "Juros cre"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def tabela_pagamentos_cre(self):
        nome_tabela = "[Pagamentos cre]"
        valores_para_inserir = [
            self.numero_pedido_nominal,
            self.venda.data,
            self.venda.valor_pago,
            self.app_master.metodo_pagamento.get()
        ]
        colunas_para_inserir = [
            "Número do documento",
            "Data",
            "Valor",
            "Obs"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def definir_numero_pedido(self):
        try:
            nome_tabela = "SYS~Sequencial"
            coluna_valor = "Valor"
            coluna_where = "Tabela"
            valor_where = "Pedidos"
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            #print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            #print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
            self.cur.execute(sql_select, (valor_where,))
            resultado = self.cur.fetchone()
            if resultado:
                return int(resultado[0] )
            else:
                return False
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo nped: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return False
    def fechar_conexao(self):
        try:
            self.con.commit()
            #print("Dados salvos com sucesso!")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()

