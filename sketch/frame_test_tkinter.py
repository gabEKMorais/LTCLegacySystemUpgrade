import tkinter as tk

class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação Principal")

        # Janela Toplevel para a tela de produtos
        self.janela_produtos = tk.Toplevel(self)
        self.janela_produtos.title("Tela de Produtos")

        # Label para exibir produtos (exemplo)
        self.label_produtos = tk.Label(self.janela_produtos, text="Tela de Produtos")
        self.label_produtos.pack()

        # Janela Toplevel para a tela de clientes
        self.janela_clientes = tk.Toplevel(self)
        self.janela_clientes.title("Tela de Clientes")

        # Label para exibir clientes (exemplo)
        self.label_clientes = tk.Label(self.janela_clientes, text="Tela de Clientes")
        self.label_clientes.pack()

        # Menu para alternar entre as telas
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Produtos", command=self.mostrar_tela_produtos)
        filemenu.add_command(label="Clientes", command=self.mostrar_tela_clientes)
        menubar.add_cascade(label="Telas", menu=filemenu)
        self.config(menu=menubar)

        # Inicialmente, mostra a tela de produtos
        self.mostrar_tela_produtos()

    def mostrar_tela_produtos(self):
        self.janela_produtos.deiconify()  # Exibe a tela de produtos
        self.janela_clientes.withdraw()  # Esconde a tela de clientes

    def mostrar_tela_clientes(self):
        self.janela_clientes.deiconify()  # Exibe a tela de clientes
        self.janela_produtos.withdraw()  # Esconde a tela de produtos

root = Aplicacao()
root.mainloop()