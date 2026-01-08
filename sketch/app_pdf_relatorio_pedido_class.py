import tkinter as tk
from tkinter import ttk, messagebox

from database import consulta_pedido_relatorio
from pdf import cria_pdf_relatorio_pedido

class app_pdf_relatorio_pedido(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        #   Parametros-variaveis utilizados | INICIALIZAÇÃO
        self.pedidos_carregados = []
        self.page_master = master
        #   COLUNAS CONFIG
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        #   WIDGETS
        #       Titulo corpo app
        self.label_principal = tk.Label(self, text="Adicione PEDIDO(S) para gerar o relatório")
        self.label_principal.grid(row=0, column=0, columnspan=2,padx=5, sticky="ew") 
        #       Inicio conteudo
        self.label_recebe_pedido = tk.Label(self, text="Número do Pedido")
        self.label_recebe_pedido.grid(row=1, column=0,padx=5, sticky="e") 
        self.entry_recebe_pedido = tk.Entry(self)
        self.entry_recebe_pedido.grid(row=1, column=1, padx=5, pady=3, sticky="w") 
        self.botao_carregar_pedido = ttk.Button(self, text="CARREGAR PEDIDO", command=lambda: self.carrega_pedido(self.entry_recebe_pedido.get()))
        self.botao_carregar_pedido.grid(row=2, column=0, columnspan=2, padx=5, pady=3, sticky="ew")
        #       Checkbox unificar
        self.checkbox_unificar = tk.BooleanVar() # Variável de controle do checkbox
        self.checkbox = tk.Checkbutton(
            self,
            text="Unificar Pedidos",
            variable=self.checkbox_unificar
        )
        self.checkbox.grid(row=3, column=0, columnspan=2, padx=5, pady=3, sticky="ew")
        #       Botoes final do corpo app
        self.botao_mostrar_pdf = ttk.Button(self, text="Exibir PDF", command=lambda: self.exibir_pdf())
        self.botao_mostrar_pdf.grid(row=98, column=0, columnspan=2, padx=5, pady=3, sticky="ew") 
        #   FRAME CONTEUDO
        self.frame_pedidos = ttk.Frame(self, borderwidth=2, relief="solid") 
        self.frame_pedidos.grid(row=10, column=0, columnspan=2, padx=5, pady=8, sticky="ew") 

    def carrega_pedido(self, id_pedido):
        try:
            consulta_temp = consulta_pedido_relatorio(id_pedido)
            if (consulta_temp.array_itens):
                self.pedidos_carregados.append(consulta_temp)
                self.entry_recebe_pedido.delete(0, tk.END)
                return self.atualiza_lista_pedidos()
            else:
                messagebox.showinfo("Erro", "O número de pedido informado é inválido ou não existe nenhum item lançado")
        except Exception as ex:
            print(f"Erro ao atualizar a lista: {ex}")

    def atualiza_lista_pedidos(self):
        try:
            self.pedidos_carregados = sorted(self.pedidos_carregados, key=lambda obj: int(obj.id))
            cont_row_ped = 3
            for ped in self.pedidos_carregados:
                try:
                    ped.frame.destroy()
                except:
                    None
                ped.frame = ttk.Frame(self.frame_pedidos)
                ped.label1 = tk.Label(ped.frame, text=f"Pedido {ped.id} Adicionado!")
                ped.label1.grid(row=0, column=0,padx=5, sticky="e") 
                ped.botao = ttk.Button(ped.frame, text="Retira Pedido", command=lambda obj_pointer = ped: self.deleta_pedido(obj_pointer))
                ped.botao.grid(row=0, column=1,padx=5, sticky="w") 
                ped.frame.grid(row=cont_row_ped, column=0, columnspan=2, padx=5, sticky="ew")
                cont_row_ped += 1
        except Exception as ex:
            print(f"Erro ao atualizar a lista: {ex}")
    def deleta_pedido(self, obj_pointer):
        try:
            obj_pointer.frame.destroy()
            self.pedidos_carregados.remove(obj_pointer)
            del obj_pointer
            return self.atualiza_lista_pedidos()
        except Exception as ex:
            print(f"Erro apagar o PEDIDO: {ex}")
    def exibir_pdf(self):
        try:
            cria_pdf_relatorio_pedido(self)
        except Exception as e:
            print (f"Erro ao criar PDF: {e}")
