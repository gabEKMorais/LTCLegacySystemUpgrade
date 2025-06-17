import time
import tempfile
import os
import fitz
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

from pdf import cria_pdf_orcamento
from database import consulta_orcamento_itens
from database import consulta_orcamento_servicos

def exibir_pdf_samepage(page, id_orc):
    global retorno_orc_db, itens_array, cont_labels
    if (len(retorno_orc_db) == 0):
        #print("Busca inicial")
        total_orc, itens_array, nome_cliente = consulta_orcamento_itens(id_orc)
        retorno_orc_db = [total_orc, itens_array, nome_cliente, id_orc]
        cont_labels = 0
        return alterna_widgets_direita(page)
    elif (id_orc != retorno_orc_db[3]):
        #print("Nova busca")
        total_orc, itens_array, nome_cliente = consulta_orcamento_itens(id_orc)
        retorno_orc_db = [total_orc, itens_array, nome_cliente, id_orc]
        cont_labels = 0
        return alterna_widgets_direita(page)
    return None #print("Sem busca!")
def alterna_widgets_direita(page):
    global retorno_orc_db, labels, buttons, itens_array, controw, cont_labels, contindice, variaveis_checkboxes, checkboxes_itens
    if (len(labels) != 0 and cont_labels == 0):
        try:
            for array in labels:
                array[0].destroy()
                array[1].destroy()
                array[2].destroy()
        except Exception as e:
            print (f"Erro ao apagar labels: {e}")
    if (len(buttons) != 0 and cont_labels == 0):
        try:
            for array in buttons:
                for item in array:
                    item.destroy()
        except Exception as e:
            print (f"Erro ao apagar botoes: {e}")
    if (len(variaveis_checkboxes) != 0 and cont_labels == 0):
        try:
            for item in checkboxes_itens:
                item.destroy()
        except Exception as e:
            print (f"Erro ao apagar checkboxes: {e}")
    page.update()
    time.sleep(0.6) 
    if (cont_labels == 0):
        labels = []
        buttons = []
        checkboxes_itens = []
        variaveis_checkboxes = {}
        controw = 2
        contindice = 0
        for item in retorno_orc_db[1]:
            # labels itens
            labbels_temp = []
            label = tk.Label(page, text=f"{item[0][0:15]}")
            label.grid(row=controw, column=4, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(page, text=f"{item[1]}")
            label.grid(row=controw, column=5, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(page, text=f"{item[2]}")
            label.grid(row=controw, column=6, sticky="ew")
            labbels_temp.append(label)
            label = tk.Frame(page, width=1, bg="black")
            labbels_temp.append(label)
            labbels_temp.append("Temp")
            labels.append(labbels_temp)
            # botoes itens
            botao_edit = ttk.Button(page, text="Editar", command=lambda indice_item=contindice, label_row=controw: botao_item(page, indice_item, 0, label_row))
            botao_edit.grid(row=controw, column=7, sticky="ew")
            botao_delete = ttk.Button(page, text="Remover", command=lambda indice_item=contindice, label_row=controw: botao_item(page, indice_item, 1, label_row))
            botao_delete.grid(row=controw, column=8, sticky="ew")
            buttons_temp = []
            buttons_temp.append(botao_edit)
            buttons_temp.append(botao_delete)
            buttons.append(buttons_temp)
            # checkbox
            var_check = tk.BooleanVar(value=True)
            variaveis_checkboxes[contindice] = var_check
            check = tk.Checkbutton(page, variable=var_check)
            check.grid(row=controw, column=9, pady=3, padx=5, sticky="ew")
            checkboxes_itens.append(check)
            # contadores update
            controw += 1
            contindice += 1
            cont_labels += 1
            page.update()
            time.sleep(0.6)
        botao_novo_item.grid(row=2, column=1, padx=5, sticky="w") 
    else:
        item = retorno_orc_db[1][cont_labels]
        # labels item
        labbels_temp = []
        label = tk.Label(page, text=f"{item[0][0:15]}")
        label.grid(row=controw, column=4, sticky="ew")
        labbels_temp.append(label)
        label = tk.Label(page, text=f"{item[1]}")
        label.grid(row=controw, column=5, sticky="ew")
        labbels_temp.append(label)
        label = tk.Label(page, text=f"{item[2]}")
        label.grid(row=controw, column=6, sticky="ew")
        labbels_temp.append(label)
        label = tk.Frame(page, width=1, bg="black")
        labbels_temp.append(label)
        labbels_temp.append("Temp")
        labels.append(labbels_temp)
        # botoes item
        botao_edit = ttk.Button(page, text="Editar", command=lambda indice_item=contindice, label_row=controw: botao_item(page, indice_item, 0, label_row))
        botao_edit.grid(row=controw, column=7, sticky="ew")
        botao_delete = ttk.Button(page, text="Remover", command=lambda indice_item=contindice, label_row=controw: botao_item(page, indice_item, 1, label_row))
        botao_delete.grid(row=controw, column=8, sticky="ew")
        buttons_temp = []
        buttons_temp.append(botao_edit)
        buttons_temp.append(botao_delete)
        buttons.append(buttons_temp)
        # checkbox
        var_check = tk.BooleanVar(value=True)
        variaveis_checkboxes[contindice] = var_check
        check = tk.Checkbutton(page, variable=var_check)
        check.grid(row=controw, column=9, pady=3, padx=5, sticky="ew")
        checkboxes_itens.append(check)
        # contadores update
        controw += 1
        contindice += 1
        cont_labels += 1
        page.update()
        time.sleep(0.6)
    return page.update()
def botao_item (page, indice, operacao, label_row): 
    global retorno_orc_db, buttons, labels, labels_edit, labels_edit_state, index_item_edit # total_orc, itens, cliente, id_orc
    if (operacao == 0): #EDITA
        #print (f"Edita {indice} na linha {label_row}")
        index_item_edit = indice
        if (not labels_edit_state):
            alterna_widgets_esquerda(page)
        labels_edit[1].delete(0, tk.END)
        labels_edit[1].insert(0,retorno_orc_db[1][indice][0])
        labels_edit[3].delete(0, tk.END)
        labels_edit[3].insert(0,int(retorno_orc_db[1][indice][1]))
        labels_edit[5].delete(0, tk.END)
        labels_edit[5].insert(0,(str(retorno_orc_db[1][indice][2]).replace(".", ",")))
        return page.update()
    else: # DELETA OU RECUPERA
        if (retorno_orc_db[1][indice][0] == "Null"):
            try:
                # edita nome para retornar ao pdf
                retorno_orc_db[1][indice][0] = labels[indice][4]
                # atualiza botões e label
                buttons[indice][0].grid(row=label_row, column=7, sticky="ew")
                buttons[indice][1].config(text="Remover")
                labels[indice][3].grid_forget()
                #print ("Registro recuperado!")
                return page.update()
            except:
                print("Não foi possivel recuperar!")
                return None
        else:
            try:
                if (labels_edit_state):
                    alterna_widgets_esquerda(page)
                labels[indice][4] = retorno_orc_db[1][indice][0]
                # edita nome para sair do pdf
                retorno_orc_db[1][indice][0] = "Null"
                # atualiza valor final
                retorno_orc_db[0] = float(retorno_orc_db[0]) - (int(retorno_orc_db[1][indice][1])*retorno_orc_db[1][indice][2])
                # atualiza botões e label
                buttons[indice][0].grid_forget()
                buttons[indice][1].config(text="Recupera")
                labels[indice][3].grid(row=label_row, column=4, columnspan=3, sticky="ew")
                #print ("Registro removido!")
                return page.update()
            except:
                print("Não foi possivel apagar!")
                return None
def botao_edit (page, operacao):
    global retorno_orc_db, index_item_edit, labels
    if (operacao == 0): # EDITA/SALVA
        if (index_item_edit >= 0):
            try:
                nome_item = labels_edit[1].get().upper()
                quant_item = int(labels_edit[3].get())
                valor_item = float((labels_edit[5].get()).replace(",", "."))
                retorno_orc_db[1][index_item_edit][0] = nome_item
                retorno_orc_db[1][index_item_edit][1] = quant_item
                valor_item_temp = retorno_orc_db[1][index_item_edit][2]
                retorno_orc_db[1][index_item_edit][2] = valor_item
                valor_item_temp = (valor_item*quant_item) - valor_item_temp
                retorno_orc_db[1][index_item_edit][3] = quant_item*valor_item
                labels[index_item_edit][0].config(text=nome_item[:15])
                labels[index_item_edit][1].config(text=str(quant_item))
                labels[index_item_edit][2].config(text=str(valor_item))
                return alterna_widgets_esquerda(page)
            except:
                labels_edit[6].grid(row=6, column=0, columnspan=3, padx=5, pady=3, sticky="ew") 
        else: # NOVO ITEM
            nome_item = labels_edit[1].get().upper()
            quant_item = int(labels_edit[3].get())
            valor_item = float((labels_edit[5].get()).replace(",", "."))
            total_item = quant_item*valor_item
            item_temp_array = [nome_item, quant_item, valor_item, total_item, False]
            # ADICIONA O ITEM NOVO EM TELA E ADICIONA ELE NO ARRAY
            retorno_orc_db[1].append(item_temp_array)
            return alterna_widgets_esquerda(page), alterna_widgets_direita(page)
    else: # CANCELA
        return alterna_widgets_esquerda(page)
def novo_item_widget(page):
    global index_item_edit
    index_item_edit = -1
    return alterna_widgets_esquerda(page)
def alterna_widgets_esquerda(page):
    global labels_edit, buttons_edit, labels_edit_state
    if (labels_edit_state):
        labels_edit[1].delete(0, tk.END)
        labels_edit[3].delete(0, tk.END)
        labels_edit[5].delete(0, tk.END)
        labels_edit[0].grid_forget()
        labels_edit[1].grid_forget()
        labels_edit[2].grid_forget()
        labels_edit[3].grid_forget()
        labels_edit[4].grid_forget()
        labels_edit[5].grid_forget()
        labels_edit[6].grid_forget()
        buttons_edit[1].grid_forget()
        buttons_edit[2].grid_forget()
        buttons_edit[0].grid(row=2, column=1, padx=5, sticky="w")
        labels_edit_state = False
    else:
        labels_edit[0].grid(row=2, column=0, padx=5, sticky="w") 
        labels_edit[1].grid(row=2, column=1, padx=5, pady=3, sticky="ew") 
        labels_edit[2].grid(row=3, column=0, padx=5, sticky="w") 
        labels_edit[3].grid(row=3, column=1, padx=5, pady=3, sticky="ew") 
        labels_edit[4].grid(row=4, column=0, padx=5, sticky="w") 
        labels_edit[5].grid(row=4, column=1, padx=5, pady=3, sticky="ew") 
        buttons_edit[0].grid_forget()
        buttons_edit[1].grid(row=5, column=1, padx=5, pady=3, sticky="ew")
        buttons_edit[2].grid(row=5, column=2, padx=5, pady=3, sticky="ew") 
        labels_edit_state = True
    return page.update()
def exibir_pdf (page):
    global variaveis_checkboxes, retorno_orc_db, services_opt
    # AQUI SEPARO OS ITENS FIXOS E ITENS VARIAVEIS DO ORÇAMENTO
    selecoes = [(opcao, var.get()) for opcao, var in variaveis_checkboxes.items()]
    selecoes2 = [(opcao, valor) for opcao, valor in selecoes if valor]
    for item in retorno_orc_db[1]:
        item[4] = False
    # AQUI CALCULO O VALOR FINAL DO DOCUMENTO
    valor_final = 0
    for item in selecoes2:
        retorno_orc_db[1][item[0]][4] = item[1]
        if (retorno_orc_db[1][item[0]][0] != "Null"):
            valor_final += retorno_orc_db[1][item[0]][3]
    retorno_orc_db[0] = valor_final
    # AQUI RECEBO OS SERVIÇOS E ARMAZENDO EM ARRAY
    services_array = consulta_orcamento_servicos(services_opt)
    # AQUI RETORNA A FUNÇÃO QUE APRESENTA O DOCUMENTO
    return exibir_pdf_orçamento(page, retorno_orc_db, services_array)
def exibir_pdf_orçamento(page, itens_array, services_array): # total_orc, itens, cliente, id_orc
    try:
        pdf_dados = cria_pdf_orcamento(itens_array, services_array, 0)
    except Exception as e:
        print (f"Erro ao criar PDF: {e}")
    try:
            # Gerando nova janela para mostrar pdf
            pdf_view = tk.Toplevel(page)  # Cria a nova janela
            pdf_view.title("Exibidor PDF")  # Define o título da nova janela
            # Adicione widgets à nova janela, se necessário
            label = tk.Label(pdf_view, text="Conteúdo da nova janela")
            label.pack()
            # Cria um arquivo temporário
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_filename = os.path.join(temp_file.name)
                # Escreva o conteúdo do PDF no arquivo temporário
                temp_file.write(pdf_dados.getvalue())
            # Abre o arquivo temporário com PyMuPDF
            doc = fitz.open(temp_filename)

            page = doc[0]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
            # Deleta o arquivo temporário
            doc.close()
            os.remove(temp_filename)
            
    except Exception as e:
        print(f"Erro ao exibir PDF: {e}")
def app_pdf_orcamento ():
    # Parametros-variaveis utilizados
    global retorno_orc_db, labels, buttons, labels_edit, buttons_edit, labels_edit_state, variaveis_checkboxes, services_opt, TAMANHO_PADRAO_TELA
    global botao_novo_item
    retorno_orc_db = []
    labels = []
    buttons = []
    labels_edit = []
    buttons_edit = []
    labels_edit_state = False
    variaveis_checkboxes = {}
    services_opt = [44, 5, 82, 14]
    TAMANHO_PADRAO_TELA = "800x500"

    # 44 m obra - 5 hr tecnico - 82 hr aj tecnico - 14 km a mais

    # GERAÇÃO DO APP | INICIO DO CÓDIGO E APP - pdf_orc
    pdf_orc = tk.Tk()
    pdf_orc.title("ORÇAMENTO LTC")
    pdf_orc.geometry("800x500")
    pdf_orc.resizable(False, False)  #  horizontal e vertical

    # Configura pesos para as colunas 
    pdf_orc.columnconfigure(0, weight=1)
    pdf_orc.columnconfigure(1, weight=1)
    pdf_orc.columnconfigure(2, weight=1)
    pdf_orc.columnconfigure(3, weight=1)
    pdf_orc.columnconfigure(4, weight=8)
    pdf_orc.columnconfigure(5, weight=1)
    pdf_orc.columnconfigure(6, weight=1)
    pdf_orc.columnconfigure(7, weight=1)
    pdf_orc.columnconfigure(8, weight=1)
    pdf_orc.columnconfigure(9, weight=1)
    pdf_orc.columnconfigure(10, weight=1)

    # Widgets da esquerda
    label_esquerda = tk.Label(pdf_orc, text="Código orçamento:")
    label_esquerda.grid(row=0, column=0, padx=5, sticky="w") 
    entry_orcamento = tk.Entry(pdf_orc)
    entry_orcamento.grid(row=0, column=1, padx=5, pady=3, sticky="ew") 
    botao_exibir_pdf = ttk.Button(pdf_orc, text="CARREGAR DADOS", command=lambda: exibir_pdf_samepage(pdf_orc, entry_orcamento.get()))
    botao_exibir_pdf.grid(row=0, column=2, padx=5, pady=3, sticky="ew") 
    # nome item
    label_esquerda_nome = tk.Label(pdf_orc, text="Descrição:")
    entry_esquerda_nome = tk.Entry(pdf_orc)
    labels_edit.append(label_esquerda_nome)
    labels_edit.append(entry_esquerda_nome)
    # unidade item
    label_esquerda_un = tk.Label(pdf_orc, text="Quantidade:")
    entry_esquerda_un = tk.Entry(pdf_orc)
    labels_edit.append(label_esquerda_un)
    labels_edit.append(entry_esquerda_un)
    # valor item
    label_esquerda_valor = tk.Label(pdf_orc, text="Valor unitário:")
    entry_esquerda_valor = tk.Entry(pdf_orc)
    labels_edit.append(label_esquerda_valor)
    labels_edit.append(entry_esquerda_valor)
    # botoes
    botao_novo_item = ttk.Button(pdf_orc, text="NOVO", command=lambda: novo_item_widget(pdf_orc))
    buttons_edit.append(botao_novo_item)
    botao_salva_item = ttk.Button(pdf_orc, text="SALVAR", command=lambda: botao_edit(pdf_orc, 0))
    buttons_edit.append(botao_salva_item)
    botao_cancela_edit = ttk.Button(pdf_orc, text="CANCELA", command=lambda: botao_edit(pdf_orc, 1))
    buttons_edit.append(botao_cancela_edit)
    # aviso erro
    label_esquerda_erro = tk.Label(pdf_orc, text="Valor ou Unidade incorretos!")
    labels_edit.append(label_esquerda_erro)


    # Linha vertical
    separador = tk.Frame(pdf_orc, width=2, bg="black")
    separador.grid(row=2, column=3, rowspan=96, sticky="ns")

    # Widgets da direita
    label_direita = tk.Label(pdf_orc, text="DESCRIÇÃO:")
    label_direita.grid(row=0, column=4, pady=3, sticky="ew") 
    label_unitario = tk.Label(pdf_orc, text="UN/M")
    label_unitario.grid(row=0, column=5, pady=3, sticky="ew") 
    label_valor = tk.Label(pdf_orc, text="R$")
    label_valor.grid(row=0, column=6, pady=3, sticky="ew") 
    label_checkbox = tk.Label(pdf_orc, text="FIXO")
    label_checkbox.grid(row=0, column=9, pady=3, padx=(5,10), sticky="ew") 

    # Widget que ocupa ambas as colunas
    linha_fim = tk.Frame(pdf_orc, width=2, bg="black")
    linha_fim.grid(row=98, column=0, padx=6, pady=5, columnspan=99, sticky="ew")
    botao_abrir_pdf = ttk.Button(pdf_orc, text="ABRIR PDF", command=lambda: exibir_pdf(pdf_orc))
    botao_abrir_pdf.grid(row=99, column=3, pady=5)
    # Divisória acima dos campos 
    linha_esquerda = tk.Frame(pdf_orc, width=2, bg="black")
    linha_esquerda.grid(row=1, column=0, padx=6, pady=5, columnspan=99, sticky="ew")

    return pdf_orc.mainloop()
    
app_pdf_orcamento()