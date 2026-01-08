import tkinter as tk
from tkinter import ttk, messagebox

from database import consulta_os_relatorio
from pdf import cria_pdf_relatorio
from extras import EntryComTextoInicial

class app_pdf_relatorio(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        #   Parametros-variaveis utilizados | INICIALIZAÇÃO
        self.os_carregadas = []
        #   COLUNAS CONFIG
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        #   WIDGETS
        #       Titulo corpo app
        self.label_principal = tk.Label(self, text="Adicione OS para gerar relatório")
        self.label_principal.grid(row=0, column=0, columnspan=2,padx=5, sticky="ew") 
        #       Inicio conteudo
        self.label_recebe_os = tk.Label(self, text="Número OS")
        self.label_recebe_os.grid(row=1, column=0,padx=5, sticky="e") 
        self.entry_recebe_os = tk.Entry(self)
        self.entry_recebe_os.grid(row=1, column=1, padx=5, pady=3, sticky="w") 
        self.botao_carregar_os = ttk.Button(self, text="CARREGAR OS", command=lambda: self.carrega_os(self.entry_recebe_os.get()))
        self.botao_carregar_os.grid(row=2, column=0, columnspan=2, padx=5, pady=3, sticky="ew")  
        #       Botoes final do corpo app
        self.botao_mostrar_pdf = ttk.Button(self, text="Exibir PDF", command=lambda: self.exibir_pdf())
        self.botao_mostrar_pdf.grid(row=98, column=0, columnspan=2, padx=5, pady=3, sticky="ew") 
        #   FRAME CONTEUDO/OS
        self.frame_os = ttk.Frame(self, borderwidth=2, relief="solid") 
        self.frame_os.grid(row=3, column=0, columnspan=2, padx=5, pady=8, sticky="ew")
        #   FRAME UNIFICAR
        self.frame_unificar_os = ttk.Frame(self, borderwidth=2, relief="solid") 
        #       Label titulo principal frame e Checkbox para ativar unificação
        self.label_frame1 = tk.Label(self.frame_unificar_os, text=f"Unificar Todas OS: ")
        self.label_frame1.grid(row=0, column=0, padx=5, sticky="ew") 
        self.unifica_os_var = tk.BooleanVar(value=False)
        self.unifica_checkbox = ttk.Checkbutton(self.frame_unificar_os, variable=self.unifica_os_var)
        self.unifica_checkbox.grid(row=0, column=1, padx=5, sticky="ew")
        #       Label e checkbox para detalhar os serviços por OS ou mostrar apenas valor final
        self.label_frame2 = tk.Label(self.frame_unificar_os, text=f"Detalhar serviços: ")
        self.label_frame2.grid(row=0, column=2, padx=5, sticky="ew") 
        self.unifica_os_detalha_var = tk.BooleanVar(value=False)
        self.unifica_detalha_checkbox = ttk.Checkbutton(self.frame_unificar_os, variable=self.unifica_os_detalha_var)
        self.unifica_detalha_checkbox.grid(row=0, column=3, padx=5, sticky="ew")
        #       Label para descrever manualmente o serviço solicitado\executado
        self.label_frame3 = tk.Label(self.frame_unificar_os, text=f"Descreva Serviços: ")
        self.label_frame3.grid(row=1, column=0, padx=5, sticky="ew") 
        self.entry_detalha = EntryComTextoInicial(self.frame_unificar_os, "Descrição")
        self.entry_detalha.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.frame_unificar_os.grid(row=97, column=0, columnspan=2, padx=5, pady=8, sticky="ew")

    def carrega_os(self, id_os):
        try:
            self.os_carregadas.append(consulta_os_relatorio(id_os))
            self.entry_recebe_os.delete(0, tk.END)
            return self.atualiza_lista_os()
        except:
            messagebox.showinfo("Erro", "O número de OS informado é inválido")
    def atualiza_lista_os(self):
        try:
            self.os_carregadas = sorted(self.os_carregadas, key=lambda obj: int(obj.os))
            cont_row_os = 3
            for os in self.os_carregadas:
                try:
                    os.frame.destroy()
                except:
                    None
                os.frame = ttk.Frame(self.frame_os)
                os.label1 = tk.Label(os.frame, text=f"OS {os.os} Adicionada!")
                os.label1.grid(row=0, column=0,padx=5, sticky="e") 
                os.botao = ttk.Button(os.frame, text="Retira OS", command=lambda obj_pointer = os: self.deleta_os(obj_pointer))
                os.botao.grid(row=0, column=1,padx=5, sticky="w") 
                os.label2 = tk.Label(os.frame, text=f"Detalhar serviços: ")
                os.label2.grid(row=0, column=2,padx=5, sticky="e") 
                os.detalha_servico_var = tk.BooleanVar(value=os.detalha_servicos) #variavel tkinter que começa com o valor de os.detalha_servicos
                os.checkbox = ttk.Checkbutton(os.frame, variable=os.detalha_servico_var,
                                            command=lambda obj_pointer=os: self.atualiza_detalha_servico(obj_pointer))
                os.checkbox.grid(row=0, column=3, padx=5, sticky="w")
                os.frame.grid(row=cont_row_os, column=0, columnspan=2, padx=5, sticky="ew")
                cont_row_os += 1
        except Exception as ex:
            print(f"Erro ao atualizar a lista: {ex}")
    def atualiza_detalha_servico(self, os_obj):
        os_obj.detalha_servicos = os_obj.detalha_servico_var.get()
    def deleta_os(self, obj_pointer):
        try:
            obj_pointer.frame.destroy()
            self.os_carregadas.remove(obj_pointer)
            del obj_pointer
            return self.atualiza_lista_os()
        except Exception as ex:
            print(f"Erro apagar a OS: {ex}")
    def exibir_pdf(self):
        try:
            cria_pdf_relatorio(self.os_carregadas, self.unifica_os_var.get(), self.unifica_os_detalha_var.get(), self.entry_detalha.get(), self)
        except Exception as e:
            print (f"Erro ao criar PDF: {e}")
