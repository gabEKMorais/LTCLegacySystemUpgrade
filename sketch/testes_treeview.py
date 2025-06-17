import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class Item():
    def __init__(self, id, nome, preco, quantidade):
        self.id = id
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.total = int(quantidade) * float(preco)
    def atualiza(self, id, nome, preco, quantidade):
        self.id = id
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.total = int(quantidade) * float(preco)

class TreeViewVenda(tk.Frame):
    def __init__(self):
        super().__init__()
        #   PARAMETROS
        self.itens = []
        self.tree_item_map = {}
        #
        self.title("Main Application")
        self.geometry("400x400")
        #   Frame para o Treeview e a Scrollbar
        frame_tree = tk.Frame(self)
        frame_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        #   Treeview para exibir os resultados
        self.tree_itens_venda = ttk.Treeview(frame_tree, columns=("item_id", "item_nome", "item_preço", "item_quantidade", "item_total"), show="headings") 
        #   Define os cabeçalhos das colunas
        self.tree_itens_venda.heading("item_id", text="ID")
        self.tree_itens_venda.heading("item_nome", text="Nome")
        self.tree_itens_venda.heading("item_preço", text="Preço")
        self.tree_itens_venda.heading("item_quantidade", text="Quantidade")
        self.tree_itens_venda.heading("item_total", text="Total")
        #   Define a largura das colunas
        self.tree_itens_venda.column("item_id", width=20, anchor="center")
        self.tree_itens_venda.column("item_nome", width=170, anchor="center")
        self.tree_itens_venda.column("item_preço", width=40, anchor="center")
        self.tree_itens_venda.column("item_quantidade", width=55, anchor="center")
        self.tree_itens_venda.column("item_total", width=40, anchor="center")
        # --- ADICIONANDO A BARRA DE ROLAGEM VERTICAL ---
        #   Cria a scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_itens_venda.yview)
        #   Configura o Treeview para usar a scrollbar
        self.tree_itens_venda.configure(yscrollcommand=scrollbar_y.set)
        #   Posiciona o Treeview e a scrollbar no frame
        self.tree_itens_venda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_itens_venda.bind("<Double-1>", self.atualizar) # <Double-1> é duplo clique do botão esquerdo do mouse
        #
        tk.Button(text="Adicionar item", command = self.adiciona).pack()

    def popular_treeview(self, lista_de_objetos_item):
        for item_id_treeview in self.tree_itens_venda.get_children():
            self.tree_itens_venda.delete(item_id_treeview)
        self.tree_item_map.clear() # Limpa o mapa ao recarregar

        for item_obj in lista_de_objetos_item:
            treeview_id = self.tree_itens_venda.insert("", "end", values=(
                item_obj.id,
                item_obj.nome,
                f"R$ {item_obj.preco:.2f}",
                item_obj.quantidade,
                f"R$ {item_obj.total:.2f}"
            ))
            self.tree_item_map[treeview_id] = item_obj

    def adiciona(self):
        try:
            id_novo = simpledialog.askstring("Adicionar Item", "ID do Item:")
            if not id_novo: return # Se o usuário cancelar
            nome_novo = simpledialog.askstring("Adicionar Item", "Nome do Item:")
            if not nome_novo: return
            preco_novo = simpledialog.askfloat("Adicionar Item", "Preço do Item:")
            if preco_novo is None: return
            quantidade_nova = simpledialog.askinteger("Adicionar Item", "Quantidade:")
            if quantidade_nova is None: return
            novo_item = Item(id_novo, nome_novo, preco_novo, quantidade_nova)
            self.popular_treeview(list(self.tree_item_map.values()) + [novo_item])
        except Exception as e:
            messagebox.showerror("Erro de Entrada", f"Dados inválidos. Por favor, insira números válidos para preço e quantidade.\nErro: {e}")

    def atualizar(self, event):
        item_selecionado_id_treeview = self.tree_itens_venda.focus()
        if item_selecionado_id_treeview:
            item_obj = self.tree_item_map.get(item_selecionado_id_treeview)
            if item_obj:
                try:
                    novo_id = simpledialog.askstring("Atualizar Item", f"Novo ID (atual: {item_obj.id}):", initialvalue=item_obj.id)
                    if novo_id is None: return
                    novo_nome = simpledialog.askstring("Atualizar Item", f"Novo Nome (atual: {item_obj.nome}):", initialvalue=item_obj.nome)
                    if novo_nome is None: return
                    novo_preco = simpledialog.askfloat("Atualizar Item", f"Novo Preço (atual: {item_obj.preco:.2f}):", initialvalue=item_obj.preco)
                    if novo_preco is None: return
                    nova_quantidade = simpledialog.askinteger("Atualizar Item", f"Nova Quantidade (atual: {item_obj.quantidade}):", initialvalue=item_obj.quantidade)
                    if nova_quantidade is None: return
                    item_obj.atualiza(novo_id, novo_nome, novo_preco, nova_quantidade)
                    self.tree_itens_venda.item(item_selecionado_id_treeview, values=(
                        item_obj.id,
                        item_obj.nome,
                        f"R$ {item_obj.preco:.2f}",
                        item_obj.quantidade,
                        f"R$ {item_obj.total:.2f}"
                    ))
                    #messagebox.showinfo("Sucesso", f"Item '{item_obj.nome}' atualizado com sucesso!")
                except Exception as e:
                    messagebox.showerror("Erro de Atualização", f"Ocorreu um erro ao atualizar o item: {e}\nVerifique os valores inseridos.")
            else:
                messagebox.showwarning("Item Não Encontrado", "Objeto Item não encontrado para a seleção.")
        else:
            messagebox.showinfo("Nenhum Item Selecionado", "Por favor, selecione um item na lista para atualizar.")

teste = TreeViewVenda()
teste.mainloop()