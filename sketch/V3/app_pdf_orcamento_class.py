import time
import fitz
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

from pdf import cria_pdf_orcamento
from database import consulta_orcamento_itens
from database import consulta_orcamento_servicos
from app_pdf_view import app_pdf_view

class app_pdf_orcamento(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Parametros-variaveis utilizados | INICIALIZAÇÃO
        self.retorno_orc_db = []
        self.labels = []
        self.buttons = []
        self.labels_edit = []
        self.buttons_edit = []
        self.labels_edit_state = False
        self.variaveis_checkboxes = {}
        self.checkboxes_itens = []
        self.services_opt = [44, 5, 82, 14]
        # 44 m obra - 5 hr tecnico - 82 hr aj tecnico - 14 km a mais
        self.id_orc = None
        self.cont_labels = None
        self.contindice = None
        self.controw = None
        self.index_item_edit = None
        # COLUNAS CONFIG
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=8)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.columnconfigure(9, weight=1)
        self.columnconfigure(10, weight=1)
        # WIDGETS ESQUERDA
        self.label_esquerda = tk.Label(self, text="Código orçamento:")
        self.label_esquerda.grid(row=0, column=0, padx=5, sticky="w") 
        self.entry_orcamento = tk.Entry(self)
        self.entry_orcamento.grid(row=0, column=1, padx=5, pady=3, sticky="ew") 
        self.botao_exibir_pdf = ttk.Button(self, text="CARREGAR DADOS", command=lambda: self.exibir_pdf_samepage(self.entry_orcamento.get()))
        self.botao_exibir_pdf.grid(row=0, column=2, padx=5, pady=3, sticky="ew") 
        # nome item
        self.label_esquerda_nome = tk.Label(self, text="Descrição:")
        self.entry_esquerda_nome = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_nome)
        self.labels_edit.append(self.entry_esquerda_nome)
        # unidade item
        self.label_esquerda_un = tk.Label(self, text="Quantidade:")
        self.entry_esquerda_un = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_un)
        self.labels_edit.append(self.entry_esquerda_un)
        # valor item
        self.label_esquerda_valor = tk.Label(self, text="Valor unitário:")
        self.entry_esquerda_valor = tk.Entry(self)
        self.labels_edit.append(self.label_esquerda_valor)
        self.labels_edit.append(self.entry_esquerda_valor)
        # botoes
        self.botao_novo_item = ttk.Button(self, text="NOVO PRODUTO", command=lambda: self.novo_item_widget())
        self.buttons_edit.append(self.botao_novo_item)
        self.botao_salva_item = ttk.Button(self, text="SALVAR", command=lambda op=0: self.botao_edit(op))
        self.buttons_edit.append(self.botao_salva_item)
        self.botao_cancela_edit = ttk.Button(self, text="CANCELA", command=lambda op=1: self.botao_edit(op))
        self.buttons_edit.append(self.botao_cancela_edit)
        # aviso erro
        self.label_esquerda_erro = tk.Label(self, text="Valor ou Unidade incorretos!")
        self.labels_edit.append(self.label_esquerda_erro)
        # LINHA VERTICAL
        self.separador = tk.Frame(self, width=2, bg="black")
        self.separador.grid(row=2, column=3, rowspan=96, sticky="ns")
        # WIDGETS DIREITA
        self.label_direita = tk.Label(self, text="DESCRIÇÃO:")
        self.label_direita.grid(row=0, column=4, pady=3, sticky="ew") 
        self.label_unitario = tk.Label(self, text="UN/M")
        self.label_unitario.grid(row=0, column=5, pady=3, sticky="ew") 
        self.label_valor = tk.Label(self, text="R$")
        self.label_valor.grid(row=0, column=6, pady=3, sticky="ew") 
        self.label_checkbox = tk.Label(self, text="FIXO")
        self.label_checkbox.grid(row=0, column=9, pady=3, padx=(5,10), sticky="ew") 
        # WIDGETS OUTROS
        self.linha_fim = tk.Frame(self, width=2, bg="black")
        self.linha_fim.grid(row=98, column=0, padx=6, pady=5, columnspan=99, sticky="ew")
        self.botao_salvar_pdf = ttk.Button(self, text="SALVAR PDF", command=lambda: self.exibir_pdf(1))
        self.botao_salvar_pdf.grid(row=99, column=2, pady=5)
        self.botao_abrir_pdf = ttk.Button(self, text="ABRIR PDF", command=lambda: self.exibir_pdf(0))
        self.botao_abrir_pdf.grid(row=99, column=3, pady=5)
        # DIVISORIA CAMPOS 
        self.linha_esquerda = tk.Frame(self, width=2, bg="black")
        self.linha_esquerda.grid(row=1, column=0, padx=6, pady=5, columnspan=99, sticky="ew")

    def exibir_pdf_samepage(self, id_orc_entry):
        self.id_orc = id_orc_entry
        if (len(self.retorno_orc_db) == 0):
            #print("Busca inicial")
            total_orc, itens_array, nome_cliente = consulta_orcamento_itens(self.id_orc)
            self.retorno_orc_db = [total_orc, itens_array, nome_cliente, self.id_orc]
            self.cont_labels = 0
            self.alterna_widgets_direita()
        elif (self.id_orc != self.retorno_orc_db[3]):
            #print("Nova busca")
            total_orc, itens_array, nome_cliente = consulta_orcamento_itens(self.id_orc)
            self.retorno_orc_db = [total_orc, itens_array, nome_cliente, self.id_orc]
            self.cont_labels = 0
            self.alterna_widgets_direita()
        None #print("Sem busca!")
    def alterna_widgets_direita(self):
        if (self.labels and self.cont_labels == 0):
            try:
                for array in self.labels:
                    array[0].destroy()
                    array[1].destroy()
                    array[2].destroy()
            except Exception as e:
                print (f"Erro ao apagar labels: {e}")
        if (self.buttons and self.cont_labels == 0):
            try:
                for array in self.buttons:
                    for item in array:
                        item.destroy()
            except Exception as e:
                print (f"Erro ao apagar botoes: {e}")
        if (self.variaveis_checkboxes and self.cont_labels == 0):
            try:
                for item in self.checkboxes_itens:
                    item.destroy()
            except Exception as e:
                print (f"Erro ao apagar checkboxes: {e}")
        self.update()
        time.sleep(0.6) 
        if (self.cont_labels == 0):
            self.labels = []
            self.buttons = []
            self.checkboxes_itens = []
            self.variaveis_checkboxes = {}
            self.controw = 2
            self.contindice = 0
            for item in self.retorno_orc_db[1]:
                # labels itens
                labbels_temp = []
                label = tk.Label(self, text=f"{item[0][0:15]}")
                label.grid(row=self.controw, column=4, sticky="ew")
                labbels_temp.append(label)
                label = tk.Label(self, text=f"{item[1]}")
                label.grid(row=self.controw, column=5, sticky="ew")
                labbels_temp.append(label)
                label = tk.Label(self, text=f"{item[2]}")
                label.grid(row=self.controw, column=6, sticky="ew")
                labbels_temp.append(label)
                label = tk.Frame(self, width=1, bg="black")
                labbels_temp.append(label)
                labbels_temp.append("Temp")
                self.labels.append(labbels_temp)
                # botoes itens
                botao_edit = ttk.Button(self, text="Editar", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 0, label_row))
                botao_edit.grid(row=self.controw, column=7, sticky="ew")
                botao_delete = ttk.Button(self, text="Remover", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 1, label_row))
                botao_delete.grid(row=self.controw, column=8, sticky="ew")
                buttons_temp = []
                buttons_temp.append(botao_edit)
                buttons_temp.append(botao_delete)
                self.buttons.append(buttons_temp)
                # checkbox
                var_check = tk.BooleanVar(value=True)
                self.variaveis_checkboxes[self.contindice] = var_check
                check = tk.Checkbutton(self, variable=var_check)
                check.grid(row=self.controw, column=9, pady=3, padx=5, sticky="ew")
                self.checkboxes_itens.append(check)
                # contadores update
                self.controw += 1
                self.contindice += 1
                self.cont_labels += 1
                self.update()
                time.sleep(0.6)
            self.buttons_edit[0].grid(row=2, column=1, padx=5, sticky="w") 
        else:
            item = self.retorno_orc_db[1][self.cont_labels]
            # labels item
            labbels_temp = []
            label = tk.Label(self, text=f"{item[0][0:15]}")
            label.grid(row=self.controw, column=4, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(self, text=f"{item[1]}")
            label.grid(row=self.controw, column=5, sticky="ew")
            labbels_temp.append(label)
            label = tk.Label(self, text=f"{item[2]}")
            label.grid(row=self.controw, column=6, sticky="ew")
            labbels_temp.append(label)
            label = tk.Frame(self, width=1, bg="black")
            labbels_temp.append(label)
            labbels_temp.append("Temp")
            self.labels.append(labbels_temp)
            # botoes item
            botao_edit = ttk.Button(self, text="Editar", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 0, label_row))
            botao_edit.grid(row=self.controw, column=7, sticky="ew")
            botao_delete = ttk.Button(self, text="Remover", command=lambda indice_item=self.contindice, label_row=self.controw: self.botao_item(indice_item, 1, label_row))
            botao_delete.grid(row=self.controw, column=8, sticky="ew")
            buttons_temp = []
            buttons_temp.append(botao_edit)
            buttons_temp.append(botao_delete)
            self.buttons.append(buttons_temp)
            # checkbox
            var_check = tk.BooleanVar(value=True)
            self.variaveis_checkboxes[self.contindice] = var_check
            check = tk.Checkbutton(self, variable=var_check)
            check.grid(row=self.controw, column=9, pady=3, padx=5, sticky="ew")
            self.checkboxes_itens.append(check)
            # contadores update
            self.controw += 1
            self.contindice += 1
            self.cont_labels += 1
            self.update()
            time.sleep(0.6)
        return self.update()
    def botao_item (self, indice, operacao, label_row): 
        if (operacao == 0): #EDITA
            #print (f"Edita {indice} na linha {label_row}")
            self.index_item_edit = indice
            if (not self.labels_edit_state):
                self.alterna_widgets_esquerda()
            self.labels_edit[1].delete(0, tk.END)
            self.labels_edit[1].insert(0,self.retorno_orc_db[1][indice][0])
            self.labels_edit[3].delete(0, tk.END)
            self.labels_edit[3].insert(0,int(self.retorno_orc_db[1][indice][1]))
            self.labels_edit[5].delete(0, tk.END)
            self.labels_edit[5].insert(0,(str(self.retorno_orc_db[1][indice][2]).replace(".", ",")))
            return self.update()
        else: # DELETA OU RECUPERA
            if (self.retorno_orc_db[1][indice][0] == "Null"):
                try:
                    # edita nome para retornar ao pdf
                    self.retorno_orc_db[1][indice][0] = self.labels[indice][4]
                    # atualiza botões e label
                    self.buttons[indice][0].grid(row=label_row, column=7, sticky="ew")
                    self.buttons[indice][1].config(text="Remover")
                    self.labels[indice][3].grid_forget()
                    #print ("Registro recuperado!")
                    return self.update()
                except:
                    print("Não foi possivel recuperar!")
                    return None
            else:
                try:
                    if (self.labels_edit_state):
                        self.alterna_widgets_esquerda()
                    self.labels[indice][4] = self.retorno_orc_db[1][indice][0]
                    # edita nome para sair do pdf
                    self.retorno_orc_db[1][indice][0] = "Null"
                    # atualiza valor final
                    self.retorno_orc_db[0] = float(self.retorno_orc_db[0]) - (int(self.retorno_orc_db[1][indice][1])*self.retorno_orc_db[1][indice][2])
                    # atualiza botões e label
                    self.buttons[indice][0].grid_forget()
                    self.buttons[indice][1].config(text="Recupera")
                    self.labels[indice][3].grid(row=label_row, column=4, columnspan=3, sticky="ew")
                    #print ("Registro removido!")
                    return self.update()
                except:
                    print("Não foi possivel apagar!")
                    return None
    def alterna_widgets_esquerda(self):
        if (self.labels_edit_state):
            self.labels_edit[3].delete(0, tk.END)
            self.labels_edit[5].delete(0, tk.END)
            self.labels_edit[1].delete(0, tk.END)
            self.labels_edit[0].grid_forget()
            self.labels_edit[1].grid_forget()
            self.labels_edit[2].grid_forget()
            self.labels_edit[3].grid_forget()
            self.labels_edit[4].grid_forget()
            self.labels_edit[5].grid_forget()
            self.labels_edit[6].grid_forget()
            self.buttons_edit[1].grid_forget()
            self.buttons_edit[2].grid_forget()
            self.buttons_edit[0].grid(row=2, column=1, padx=5, sticky="w")
            self.labels_edit_state = False
        else:
            self.labels_edit[0].grid(row=2, column=0, padx=5, sticky="w") 
            self.labels_edit[1].grid(row=2, column=1, padx=5, pady=3, sticky="ew") 
            self.labels_edit[2].grid(row=3, column=0, padx=5, sticky="w") 
            self.labels_edit[3].grid(row=3, column=1, padx=5, pady=3, sticky="ew") 
            self.labels_edit[4].grid(row=4, column=0, padx=5, sticky="w") 
            self.labels_edit[5].grid(row=4, column=1, padx=5, pady=3, sticky="ew") 
            self.buttons_edit[0].grid_forget()
            self.buttons_edit[1].grid(row=5, column=1, padx=5, pady=3, sticky="ew")
            self.buttons_edit[2].grid(row=5, column=2, padx=5, pady=3, sticky="ew") 
            self.labels_edit_state = True
        return self.update()
    def novo_item_widget(self):
        self.index_item_edit = -1
        return self.alterna_widgets_esquerda()
    def botao_edit (self, operacao):
        if (operacao == 0): # EDITA/SALVA
            if (self.index_item_edit >= 0):
                try:
                    nome_item = self.labels_edit[1].get().upper()
                    quant_item = int(self.labels_edit[3].get())
                    valor_item = float((self.labels_edit[5].get()).replace(",", "."))
                    self.retorno_orc_db[1][self.index_item_edit][0] = nome_item
                    self.retorno_orc_db[1][self.index_item_edit][1] = quant_item
                    valor_item_temp = self.retorno_orc_db[1][self.index_item_edit][2]
                    self.retorno_orc_db[1][self.index_item_edit][2] = valor_item
                    valor_item_temp = (valor_item*quant_item) - valor_item_temp
                    self.retorno_orc_db[1][self.index_item_edit][3] = quant_item*valor_item
                    self.labels[self.index_item_edit][0].config(text=nome_item[:15])
                    self.labels[self.index_item_edit][1].config(text=str(quant_item))
                    self.labels[self.index_item_edit][2].config(text=str(valor_item))
                    return self.alterna_widgets_esquerda()
                except:
                    self.labels_edit[6].grid(row=6, column=0, columnspan=3, padx=5, pady=3, sticky="ew") 
            else: # NOVO ITEM
                nome_item = self.labels_edit[1].get().upper()
                quant_item = int(self.labels_edit[3].get())
                valor_item = float((self.labels_edit[5].get()).replace(",", "."))
                total_item = quant_item*valor_item
                item_temp_array = [nome_item, quant_item, valor_item, total_item, False]
                # ADICIONA O ITEM NOVO EM TELA E ADICIONA ELE NO ARRAY
                self.retorno_orc_db[1].append(item_temp_array)
                return self.alterna_widgets_esquerda(), self.alterna_widgets_direita()
        else: # CANCELA
            return self.alterna_widgets_esquerda()
    def exibir_pdf (self, op):
        # AQUI SEPARO OS ITENS FIXOS E ITENS VARIAVEIS DO ORÇAMENTO
        selecoes = [(opcao, var.get()) for opcao, var in self.variaveis_checkboxes.items()]
        selecoes2 = [(opcao, valor) for opcao, valor in selecoes if valor]
        for item in self.retorno_orc_db[1]:
            item[4] = False
        # AQUI CALCULO O VALOR FINAL DO DOCUMENTO
        valor_final = 0
        for item in selecoes2:
            self.retorno_orc_db[1][item[0]][4] = item[1]
            if (self.retorno_orc_db[1][item[0]][0] != "Null"):
                valor_final += self.retorno_orc_db[1][item[0]][3]
        self.retorno_orc_db[0] = valor_final
        # AQUI RECEBO OS SERVIÇOS E ARMAZENDO EM ARRAY
        services_array = consulta_orcamento_servicos(self.services_opt)
        # AQUI RETORNA A FUNÇÃO QUE APRESENTA O DOCUMENTO
        return self.exibir_pdf_orçamento(services_array, op)
    def exibir_pdf_orçamento(self, services_array, op): # total_orc, itens, cliente, id_orc
        try:
            if (op == 0):
                pdf_dados = cria_pdf_orcamento(self.retorno_orc_db, services_array, 0)
                try:
                        doc = fitz.open(stream=pdf_dados.getvalue(), filetype="pdf")
                        page = doc[0]
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        photo = ImageTk.PhotoImage(img)
                        # ENVIA A IMAGEM GERADA PARA UMA INSTANCIA DE CLASSE RESPONSAVEL POR MOSTRAR EM TELA
                        app_pdf_view_instance = app_pdf_view(self, [photo])
                        app_pdf_view_instance.mainloop()
                except Exception as e:
                    print(f"Erro ao exibir PDF: {e}")
            else:
                cria_pdf_orcamento(self.retorno_orc_db, services_array, 1)
        except Exception as e:
            print (f"Erro ao criar PDF: {e}")
