import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from config import CONN_STR

def consultar_clientes_por_nome(nome_pesquisa):
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
        resultados = consultar_clientes_por_nome(termo_pesquisa)
        if resultados:
            self.conteiner_resultados.exibir_todos_resultados(resultados)
        else:
            messagebox.showinfo("Resultados", "Nenhum cliente encontrado com o critério '{}'.".format(termo_pesquisa))
    def finaliza(self, cliente):
        self.master.cliente_selecionado = cliente
        self.destroy()
