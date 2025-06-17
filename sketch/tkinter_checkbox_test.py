import tkinter as tk

def mostrar_selecao():
    """Exibe a seleção atual dos checkboxes."""
    selecoes = [
        (opcao, var.get()) for opcao, var in variaveis_checkboxes.items()
    ]
    resultado = ", ".join([f"{opcao}: {valor}" for opcao, valor in selecoes if valor])
    label_resultado.config(text=f"Selecionado(s): {resultado}" if resultado else "Nenhuma opção selecionada")

# Dados para os checkboxes (exemplo)
opcoes = ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]

# Cria a janela principal
janela = tk.Tk()
janela.title("Exemplo Checkboxes Dinâmicos")

# Dicionário para armazenar as variáveis de controle de cada checkbox
variaveis_checkboxes = {}

# Loop para criar os checkboxes
for opcao in opcoes:
    # Cria uma variável de controle para este checkbox
    var = tk.BooleanVar(value=False)
    variaveis_checkboxes[opcao] = var

    # Cria o checkbox
    check = tk.Checkbutton(janela, text=opcao, variable=var, command=mostrar_selecao)
    check.pack()

# Rótulo para exibir o resultado
label_resultado = tk.Label(janela, text="Nenhuma opção selecionada")
label_resultado.pack()

# Inicia o loop principal da aplicação
janela.mainloop()