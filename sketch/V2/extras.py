from tkinter import ttk

# MANIPULAÇÃO DE DADOS - DIVISÃO STRING GRANDE
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

# WIDGET TKINTER
class EntryComTextoInicial(ttk.Entry):
    def __init__(self, master=None, texto_inicial="Digite aqui...", **kwargs):
        super().__init__(master, **kwargs)
        self.texto_inicial = texto_inicial
        self.inserir_texto_inicial()
        self.bind("<FocusIn>", self.limpar_texto)

    def inserir_texto_inicial(self):
        self.insert(0, self.texto_inicial)

    def limpar_texto(self, *args):
        self.delete(0, "end")
        self.unbind("<FocusIn>") # remove o bind para que nao execute novamente.
