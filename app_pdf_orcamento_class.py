import tkinter as tk
from tkinter import ttk, messagebox

from extras import EntryComTextoInicial
from database import consulta_orcamento
from pdf import cria_pdf_orcamento

class app_pdf_orcamento (tk.Frame):
    def __init__(self, master, reinicia_app):
        super().__init__(master)
        #       FRAME INICIAL 
        self.frame_inicial = ttk.Frame(self) 
        label_inicial = ttk.Label(self.frame_inicial, text="Escolha a opção para iniciar:", font=("Arial", 14, "bold"))
        label_inicial.pack(padx=20, pady=10)
        botao_inicial_novo_orcamento = ttk.Button(self.frame_inicial, text="Novo orçamento", command=self.novo_orcamento)
        botao_inicial_novo_orcamento.pack(padx=20, pady=10)
        entry_inicial = EntryComTextoInicial(self.frame_inicial, "Nº do orçamento")
        entry_inicial.pack(padx=20, pady=(10, 2))
        botao_inicial_carrega_orcamento = ttk.Button(self.frame_inicial, text="Carregar orçamento", command=lambda: self.carrega_orcamento(entry_inicial.get()))
        botao_inicial_carrega_orcamento.pack(padx=20, pady=(2, 10))
        self.frame_inicial.pack(padx=10, pady=10)
        #   WIDGETS DA PAGINA ORÇAMENTO
        #       FRAME ORÇAMENTO
        self.frame_orcamento = tk.Frame(self)
        #       FRAME NOVO ITEM
        frame_novo_item_pai = ttk.Frame(self.frame_orcamento)
        frame_novo_item_pai.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        self.botao_novo_item = ttk.Button(frame_novo_item_pai, text="Novo", command=lambda: self.novo_ou_edita_item("produto"))
        self.botao_novo_item.pack(padx=10, pady=10, expand=True)
        #           Frames para adicionar itens
        #               Produtos
        self.frame_item_produto = ttk.Frame(frame_novo_item_pai)
        label = ttk.Label(self.frame_item_produto, text="Descrição do Produto", font=("Arial", 8, "bold"))
        label.pack(padx=20)
        self.entry_produto_descricao = tk.Entry(self.frame_item_produto)
        self.entry_produto_descricao.pack(padx=20, pady=(4,10))
        label = ttk.Label(self.frame_item_produto, text="Valor do Produto", font=("Arial", 8, "bold"))
        label.pack(padx=20)
        self.entry_produto_valor = tk.Entry(self.frame_item_produto)
        self.entry_produto_valor.pack(padx=20, pady=(4,10))
        label = ttk.Label(self.frame_item_produto, text="Quantidade do Produto", font=("Arial", 8, "bold"))
        label.pack(padx=20)
        self.entry_produto_un = tk.Entry(self.frame_item_produto)
        self.entry_produto_un.pack(padx=20, pady=(4,10))
        self.botao_produto_salvar = ttk.Button(self.frame_item_produto, text="Salvar")
        self.botao_produto_salvar.pack(padx=10, pady=10)
        botao_produto_cancela = ttk.Button(self.frame_item_produto, text="Cancelar", command=self.cancela)
        botao_produto_cancela.pack(padx=10, pady=10)
        #               Serviços
        self.frame_item_servico = ttk.Frame(frame_novo_item_pai)
        label = ttk.Label(self.frame_item_servico, text="Descrição do Serviço", font=("Arial", 8, "bold"))
        label.pack(padx=20)
        self.entry_servico_descricao = tk.Entry(self.frame_item_servico)
        self.entry_servico_descricao.pack(padx=20, pady=(4,10))
        label = ttk.Label(self.frame_item_servico, text="Valor do Serviço", font=("Arial", 8, "bold"))
        label.pack(padx=20)
        self.entry_servico_valor = tk.Entry(self.frame_item_servico)
        self.entry_servico_valor.pack(padx=20, pady=(4,10))
        self.botao_servico_salvar = ttk.Button(self.frame_item_servico, text="Salvar")
        self.botao_servico_salvar.pack(padx=10, pady=10)
        botao_servico_cancela = ttk.Button(self.frame_item_servico, text="Cancelar", command=self.cancela)
        botao_servico_cancela.pack(padx=10, pady=10)
        #       FRAME PAI DAS LISTAS E FRAME DOS BOTOES
        frame_listas = ttk.Frame(self.frame_orcamento, borderwidth=2, relief="solid")
        frame_listas.pack(side=tk.LEFT, padx=10, pady=10)
        #           BOTOES
        frame_botoes = ttk.Frame(frame_listas)
        botao_lista_produtos = ttk.Button(frame_botoes, text="Produtos", command=lambda: self.muda_lista("produto"))
        botao_lista_produtos.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        botao_lista_servicos = ttk.Button(frame_botoes, text="Serviços", command=lambda: self.muda_lista("servico"))
        botao_lista_servicos.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        botao_pdf = ttk.Button(frame_botoes, text="Exibir PDF", command=self.exibir_pdf)
        botao_pdf.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        botao_pdf = ttk.Button(frame_botoes, text="Sair", command=reinicia_app)
        botao_pdf.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        frame_botoes.pack(fill=tk.X,expand=True)
        #       FRAME LISTA PRODUTOS
        self.frame_lista_produtos = ttk.Frame(frame_listas) 
        self.frame_lista_produtos.columnconfigure(0, weight=2)  # DESCRIÇÃO
        self.frame_lista_produtos.columnconfigure(1, weight=1)  # UNIDADE
        self.frame_lista_produtos.columnconfigure(2, weight=1)  # VALOR
        self.frame_lista_produtos.columnconfigure(3, weight=1)  # TOTAL
        self.frame_lista_produtos.columnconfigure(4, weight=1)  # BOTAO EDITA
        self.frame_lista_produtos.columnconfigure(5, weight=1)  # BOTAO REMOVE
        self.frame_lista_produtos.columnconfigure(6, weight=1)  # CHECKBOX
        label = ttk.Label(self.frame_lista_produtos, text="Descrição")
        label.grid(row=0, column=0, sticky="ew", padx=10)
        label = ttk.Label(self.frame_lista_produtos, text="Un")
        label.grid(row=0, column=1, sticky="ew", padx=10)
        label = ttk.Label(self.frame_lista_produtos, text="Valor")
        label.grid(row=0, column=2, sticky="ew", padx=10)
        label = ttk.Label(self.frame_lista_produtos, text="Total")
        label.grid(row=0, column=3, sticky="ew", padx=10)
        label = ttk.Label(self.frame_lista_produtos, text="Fixo")
        label.grid(row=0, column=6, sticky="ew", padx=10)
        separador = tk.Frame(self.frame_lista_produtos, width=2, bg="black")
        separador.grid(row=1,column=0,columnspan=10, sticky="ew")
        self.frame_lista_produtos.pack()
        #       FRAME LISTA SERVIÇOS
        self.frame_lista_servicos = ttk.Frame(frame_listas) 
        self.frame_lista_servicos.columnconfigure(0, weight=2)  # DESCRIÇÃO
        self.frame_lista_servicos.columnconfigure(1, weight=1)  # VALOR
        self.frame_lista_servicos.columnconfigure(2, weight=1)  # BOTAO REMOVE
        label = ttk.Label(self.frame_lista_servicos, text="Descrição")
        label.grid(row=0, column=0, sticky="ew", padx=10)
        label = ttk.Label(self.frame_lista_servicos, text="Valor")
        label.grid(row=0, column=1, sticky="ew", padx=10)
        separador = tk.Frame(self.frame_lista_servicos, width=2, bg="black")
        separador.grid(row=1,column=0,columnspan=10, sticky="ew")

#   INICIAR ORÇAMENTO DO ZERO
    def novo_orcamento(self):
        self.orcamento = consulta_orcamento(None)
        self.inicia_orcamento()
#   INICIAR ORÇAMENTO A PARTIR DE UM EXISTENTE NO DB
    def carrega_orcamento(self, numero_orcamento):
        try:
            self.orcamento = consulta_orcamento(numero_orcamento)
            if(self.orcamento.tem_orc):
                self.inicia_orcamento()
            else:
                messagebox.showinfo("Erro", "O número de orçamento informado é inválido")
        except:
            messagebox.showinfo("Erro", "O número de orçamento informado é inválido")
#   ATUALIZA APP PARA INICIAR ORÇAMENTO
    def inicia_orcamento(self):
        self.frame_inicial.pack_forget()
        self.frame_orcamento.pack(fill=tk.BOTH, expand=True)
        self.cont_row_prod = 2
        self.cont_row_serv = 2
        return self.inicia_listas()
#   MOSTRA EM TELA PRODUTOS E SERVIÇOS
    def inicia_listas(self):
        for produto in self.orcamento.array_produtos:
            self.adiciona_item(produto)
        for servico in self.orcamento.array_services:
            self.adiciona_item(servico)
        return self.update()
    def adiciona_item(self, obj):
        if (obj.tipo == "produto"):
            obj.label_nome = ttk.Label(self.frame_lista_produtos, text=obj.nome[0:15])
            obj.label_nome.grid(row=self.cont_row_prod, column=0, sticky="ew", padx=10)
            obj.label_un = ttk.Label(self.frame_lista_produtos, text=obj.un)
            obj.label_un.grid(row=self.cont_row_prod, column=1, sticky="ew", padx=10)
            obj.label_valor = ttk.Label(self.frame_lista_produtos, text=obj.valor)
            obj.label_valor.grid(row=self.cont_row_prod, column=2, sticky="ew", padx=10)
            obj.label_total = ttk.Label(self.frame_lista_produtos, text=obj.total)
            obj.label_total.grid(row=self.cont_row_prod, padx=10, pady=7, column=3, sticky="ew")
            obj.botao_edita = ttk.Button(self.frame_lista_produtos, text="Edita", command=lambda obj_pointer = obj:self.novo_ou_edita_item("produto", obj_pointer))
            obj.botao_edita.grid(row=self.cont_row_prod, column=4, padx=10, pady=7, sticky="ew")
            obj.botao_remove = ttk.Button(self.frame_lista_produtos, text="Remove", command=lambda obj_pointer = obj:self.remove_item(obj_pointer))
            obj.botao_remove.grid(row=self.cont_row_prod, column=5, sticky="ew")
            obj.removedor = tk.Frame(self.frame_lista_produtos, width=1, bg="black")
            obj.fixo_var = tk.BooleanVar(value=obj.fixo)
            obj.checkbox = ttk.Checkbutton(self.frame_lista_produtos, variable=obj.fixo_var, command=lambda obj_pointer=obj: self.atualiza_fixo(obj_pointer))
            obj.checkbox.grid(row=self.cont_row_prod, column=6, sticky="ew", padx=(15,10))
            obj.row = self.cont_row_prod
            self.cont_row_prod += 1
        else:
            obj.label_nome = ttk.Label(self.frame_lista_servicos, text=obj.nome)
            obj.label_nome.grid(row=self.cont_row_serv, column=0, sticky="ew", padx=10)
            obj.label_valor = ttk.Label(self.frame_lista_servicos, text=obj.valor)
            obj.label_valor.grid(row=self.cont_row_serv, column=1, sticky="ew", padx=10)
            obj.botao_edita = ttk.Button(self.frame_lista_servicos, text="Edita", command=lambda obj_pointer = obj:self.novo_ou_edita_item("Servico", obj_pointer))
            obj.botao_edita.grid(row=self.cont_row_serv, column=2, padx=10, pady=7, sticky="ew")
            obj.botao_remove = ttk.Button(self.frame_lista_servicos, text="Remove", command=lambda obj_pointer = obj:self.remove_item(obj_pointer))
            obj.botao_remove.grid(row=self.cont_row_serv, column=3, padx=10, pady=7, sticky="ew")
            obj.removedor = tk.Frame(self.frame_lista_servicos, width=1, bg="black")
            obj.row = self.cont_row_serv
            self.cont_row_serv += 1
        self.update()
    def atualiza_fixo(self, obj):
        obj.fixo = obj.fixo_var.get()
#   MUDA A LISTA EM DISPLAY
    def muda_lista(self, tipo):
        if (tipo == "produto"):
            self.frame_lista_servicos.pack_forget()
            self.frame_item_produto.pack_forget()
            self.frame_item_servico.pack_forget()
            self.botao_novo_item.config(command=lambda: self.novo_ou_edita_item("produto"))
            self.botao_novo_item.pack(padx=10, pady=10, expand=True)
            self.frame_lista_produtos.pack()
        else:
            self.frame_lista_produtos.pack_forget()
            self.frame_item_produto.pack_forget()
            self.frame_item_servico.pack_forget()
            self.botao_novo_item.config(command=lambda: self.novo_ou_edita_item("servico"))
            self.botao_novo_item.pack(padx=10, pady=10, expand=True)
            self.frame_lista_servicos.pack()
        return self.update()
#   ABRE FRAME PARA EDIÇÃO/CRIAÇÃO
    def novo_ou_edita_item(self, tipo, obj_pointer=None):
        if (tipo == "produto"):
            self.botao_novo_item.pack_forget()
            self.entry_produto_descricao.delete(0, tk.END) 
            self.entry_produto_valor.delete(0, tk.END) 
            self.entry_produto_un.delete(0, tk.END) 
            self.frame_item_produto.pack(padx=10, pady=10, expand=True)
            if (obj_pointer != None):
                self.botao_produto_salvar.config(command=lambda: self.salva_item("produto", obj_pointer))
                self.entry_produto_descricao.insert(0,obj_pointer.nome)
                self.entry_produto_valor.insert(0,str(obj_pointer.valor).replace(".", ","))
                self.entry_produto_un.insert(0,obj_pointer.un)
            else:
                self.botao_produto_salvar.config(command=lambda: self.salva_item("produto"))
        else:
            self.botao_novo_item.pack_forget()
            self.entry_servico_descricao.delete(0, tk.END) 
            self.entry_servico_valor.delete(0, tk.END) 
            self.frame_item_servico.pack(padx=10, pady=10, expand=True)
            if (obj_pointer != None):
                self.botao_servico_salvar.config(command=lambda: self.salva_item("servico", obj_pointer))
                self.entry_servico_descricao.insert(0,obj_pointer.nome)
                self.entry_servico_valor.insert(0,str(obj_pointer.valor).replace(".", ","))
            else:
                self.botao_servico_salvar.config(command=lambda: self.salva_item("servico"))
        return self.update()
#   CANCELA EDIÇÃO/CRIAÇÃO    
    def cancela(self):
        self.frame_item_produto.pack_forget()
        self.frame_item_servico.pack_forget()
        self.botao_novo_item.pack(padx=10, pady=10, expand=True)
        return self.update()
#   SALVA UM NOVO ITEM OU A EDIÇÃO DE UM EXISTENTE    
    def salva_item(self, tipo, obj_pointer=None):
        try:
            if (tipo == "produto"):
                if(obj_pointer == None):
                    self.adiciona_item(self.orcamento.novo_produto(self.entry_produto_descricao.get(),self.entry_produto_valor.get().replace(",", "."),self.entry_produto_un.get()))
                    return self.cancela()
                else:
                    obj_pointer.atualiza(self.entry_produto_descricao.get(),self.entry_produto_valor.get().replace(",", "."),self.entry_produto_un.get())
                    obj_pointer.label_nome.config(text=obj_pointer.nome[0:15])
                    obj_pointer.label_valor.config(text=obj_pointer.valor)
                    obj_pointer.label_un.config(text=str(obj_pointer.un))
                    obj_pointer.label_total.config(text=obj_pointer.total)
                    self.frame_item_produto.pack_forget()
                    self.botao_novo_item.pack(padx=10, pady=10, expand=True)
                    return self.update()
            else:
                if(obj_pointer == None):
                    self.adiciona_item(self.orcamento.novo_servico(self.entry_servico_descricao.get(),self.entry_servico_valor.get().replace(",", ".")))
                    return self.cancela()
                else:
                    obj_pointer.atualiza(self.entry_servico_descricao.get(),self.entry_servico_valor.get().replace(",", "."))
                    obj_pointer.label_nome.config(text=obj_pointer.nome[0:15])
                    obj_pointer.label_valor.config(text=obj_pointer.valor)
                    self.frame_item_servico.pack_forget()
                    self.botao_novo_item.pack(padx=10, pady=10, expand=True)
                    return self.update()
        except:
            messagebox.showinfo("Erro", "Verifique as informações digitadas!") 
#   REMOVE OU RECUPERA ITEM - PARA TIRAR DO PDF    
    def remove_item(self, obj_pointer):
        self.cancela()
        if (obj_pointer.remove):
            if (obj_pointer.tipo == "produto"):
                obj_pointer.botao_edita.grid(row=obj_pointer.row, column=4, padx=10, pady=7, sticky="ew")
                obj_pointer.checkbox.grid(row=obj_pointer.row, column=6, sticky="ew", padx=(15,10))
            else:
                obj_pointer.botao_edita.grid(row=obj_pointer.row, column=2, padx=10, pady=7, sticky="ew")
            obj_pointer.botao_remove.config(text="Remove")
            obj_pointer.removedor.grid_forget()
            obj_pointer.remove = False
        else:
            obj_pointer.botao_edita.grid_forget()
            obj_pointer.botao_remove.config(text="Recupera")
            if (obj_pointer.tipo == "produto"):
                obj_pointer.removedor.grid(row=obj_pointer.row, column=0, columnspan=4, sticky="ew")
                obj_pointer.checkbox.grid_forget()
            else:
                obj_pointer.removedor.grid(row=obj_pointer.row, column=0, columnspan=2, sticky="ew")
            obj_pointer.remove = True
#   EXIBI PDF
    def exibir_pdf(self):
        cria_pdf_orcamento(self, self.orcamento)
