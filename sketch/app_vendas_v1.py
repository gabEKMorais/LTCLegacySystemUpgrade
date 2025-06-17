import os
import win32print
import tempfile
import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import fitz
from extras import dividir_string
from database import ProdutoVenda, ServicoVenda
from app_db_registra_venda import RegistrarVenda
from app_db_seleciona_cliente import AppDefinirClienteVenda

class ClienteVenda():
    def __init__(self):
        self.id = 1
        self.nome = "Não Identificado"
    def atualiza(self, id, nome):
        self.id = int(id)
        self.nome = nome

class AppTelaRecibo(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        #   PARAMETROS E DEFINIÇÕES
        self.title("RECIBO") 
        self.geometry("250x600")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        #   CENTRALIZAR TELA
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        #deslocamento_para_cima = int(altura_tela * 0.15)
        y = (altura_tela // 2) - (altura // 2) #- deslocamento_para_cima
        self.geometry(f"+{x}+{y}")
        #   DADOS DO RECIBO
        #       DATA
        self.data = datetime.datetime.now().strftime("%d/%m/%Y")
        #       DEFININDO COMPRADOR
        entry_comprador = str(master.entry_comprador_venda.get())
        if (len(entry_comprador) < 2):
            self.comprador = "Não identificado"
        else:
            self.comprador = entry_comprador[:20]
        #       DEFININDO OBS VENDA
        self.observacao_venda = ("Não impresso " + str(master.entry_obs_venda.get()))
        #       DESCONTO
        try:
            self.desconto = float(master.entry_desconto_venda.get().replace(",","."))
        except:
            self.desconto = 0
        #       CALCULO DO TOTAL E VALOR PAGO APOS DESCONTO
        self.total = 0
        for item in master.itens_venda_produto:
            self.total += item.total
        for item in master.itens_venda_servico:
            self.total += item.total
        try:   
            self.valor_pago = float(self.total) - float(self.desconto)
        except:
            self.valor_pago = self.total
        #   GERAÇÃO DO PEDIDO
        if (master.checkbox_gera_pedido_var.get()):
            try:
                self.registro = RegistrarVenda(self, master)
            except Exception as ex:
                print(f"Erro: {ex}")
        #   GERAÇÃO DO PDF E VIZUALIZAÇÃO
        self.pdf_path = self.gerar_pdf(master)
        doc = fitz.open(self.pdf_path)
        pix = doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pagina = ImageTk.PhotoImage(img) 
        #   BOTOES
        botao_imprimir = ttk.Button(self, text="Imprimir", command=lambda: self.imprimir_recibo(self.pdf_path))
        botao_imprimir.pack()
        botao_sair = ttk.Button(self, text="Sair", command = self.fechar_tela)
        botao_sair.pack()
        try:
            label_imagem = ttk.Label(self)
            label_imagem.config(image = pagina)
            label_imagem.image = pagina
            label_imagem.pack() 
        except Exception as ex:
            print(ex)

    def gerar_pdf(self, master):
        largura_mm = 80
        altura_mm = 327#297
        largura_pt = largura_mm * 2.83465
        altura_pt = altura_mm * 2.83465
        pdf = FPDF(orientation='P', unit='pt', format=(largura_pt, altura_pt))
        pdf.add_page()
        #   Titulo              .set_font("Helvetica", "B", 14)
        #   Numeros             .set_font("Helvetica", "B", 12)
        #   Texto               .set_font("Courier", "B", 12)
        #   LOGO E HEADER
        pdf.image('logo.png', 20, 10, 40)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 14, 'LTC TECNOLOGIA', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, 'RECIBO DE PAGAMENTO', 0, 1, 'C')
        pdf.cell(0, 28, '', 0, 1, 'C')
        #   CORPO - VALORES
        #       VALOR PAGO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 14, 'Recebemos a quantia de', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, f'R${self.valor_pago:.2f}', 0, 1, 'C')
        #       DATA PAGAMENTO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(50, 14, 'No dia', 0, 0, 'C')
        pdf.cell(0, 14, self.data, 0, 1, 'C')
        pdf.cell(0, 20, '', 0, 1, 'C')
        #       DADOS PEDIDO
        if (master.checkbox_gera_pedido_var.get()):
            if (self.registro.registrado):
                pdf.set_font("Courier", "B", 12) 
                pdf.cell(0, 20, 'Referente ao pedido', 0, 1, 'C')  
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 14, f'Nº {self.registro.numero_pedido}', 0, 1, 'C')
            else:
                pdf.set_font("Courier", "B", 12)       
                pdf.cell(0, 10, 'Referente ao pedido', 0, 1, 'C')
        else:
                pdf.set_font("Courier", "B", 12)       
                pdf.cell(0, 10, 'Referente ao pedido', 0, 1, 'C')
        #       VALOR PEDIDO
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 20, 'De valor', 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 14, f'R${self.total:.2f}', 0, 1, 'C')
        #       DESCONTO
        if (isinstance(self.desconto, float)):
            if (self.desconto > 0):
                pdf.set_font("Courier", "B", 12)
                pdf.cell(0, 20, 'Decrescido em', 0, 1, 'C')
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 14, f'R${self.desconto:.2f}', 0, 1, 'C')
                pdf.set_font("Courier", "B", 12)
                pdf.cell(0, 20, 'De desconto', 0, 1, 'C')
        #       DESCRIÇÃO DOS PRODUTOS
        if (master.itens_venda_produto):
            pdf.cell(0, 20, '', 0, 1, 'C')
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 20, 'Descrição Produto', 0, 1, 'C')
            pdf.cell(0, 20, ' Código | Preço | Un | Total', 0, 1, 'C')
            for produto in master.itens_venda_produto:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        #       DESCRIÇÃO DOS SERVIÇOS
        if (master.itens_venda_servico):
            pdf.cell(0, 20, '', 0, 1, 'C')
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 20, 'Descrição Serviço', 0, 1, 'C')
            pdf.cell(0, 20, ' Código | Preço | Un | Total', 0, 1, 'C')
            for produto in master.itens_venda_servico:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        #   PARA CONTROLE INTERNO
        if (master.checkbox_controle_interno_var.get()):
            pdf.add_page()
            pdf.cell(0, 20, 'CONTROLE INTERNO', 0, 1, 'C')
            #       DATA
            pdf.set_font("Courier", "B", 12)
            pdf.cell(0, 14, (datetime.datetime.now().strftime("%d/%m/%y %H:%M")), 0, 1, 'C')
            #       NUMERO PEDIDO
            if (master.checkbox_gera_pedido_var.get()):
                if (self.registro.registrado):
                    pdf.set_font("Courier", "B", 12) 
                    pdf.cell(0, 20, 'Referente ao pedido', 0, 1, 'C')  
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 14, f'Pedido Nº {self.registro.numero_pedido}', 0, 1, 'C')
            #       VALOR PAGO
            pdf.cell(0, 14, 'Valor pago', 0, 1, 'C')
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 20, f'R${self.valor_pago:.2f}', 0, 1, 'C')
            #       METODO DE PAGAMENTO
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 14, f'Método: {master.metodo_pagamento.get()}', 0, 1, 'C')
            #       DESCRIÇÃO DOS PRODUTOS
            pdf.set_font("Courier", "B", 12)
            for produto in master.itens_venda_produto:
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
            #       DESCRIÇÃO DOS SERVIÇOS
            for produto in master.itens_venda_servico:
                pdf.cell(0, 10, ' ----------------------- ', 0, 1, 'C')
                if(len(produto.nome) < 30):
                    pdf.cell(0, 14, produto.nome, 0, 1, 'C')
                else:
                    p1, p2 = dividir_string(produto.nome, 30)
                    pdf.cell(0, 14, p1, 0, 1, 'C')
                    pdf.cell(0, 14, p2, 0, 1, 'C')
                pdf.cell(55, 20, f"{produto.id}")
                pdf.cell(58, 20, f"{produto.preco:.2f}")
                pdf.cell(34, 20, str(produto.quantidade))
                pdf.cell(0, 20, f"{produto.total:.2f}", 0, 1)
        return self.criar_pdf_temporario_fpdf(pdf)
    def criar_pdf_temporario_fpdf(self, pdf):
        conteudo_pdf = pdf.output(dest='S') # Obter a saída em bytes
        arquivo_temporario = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        arquivo_temporario.write(conteudo_pdf)
        arquivo_temporario.close()
        return arquivo_temporario.name
    def excluir_pdf_temporario(self):
        try:
            os.remove(self.pdf_path)
        except FileNotFoundError:
            print(f"Arquivo {self.pdf_path} não encontrado.")
    def imprimir_recibo(self, pdf_temporario):
        #   FAZ A IMPRESSÃO
        impressora_padrao_atual = win32print.GetDefaultPrinter()
        try:
            win32print.SetDefaultPrinter("RECIBOS")
            caminho_pdf_abs = os.path.abspath(pdf_temporario)
            os.startfile(caminho_pdf_abs, "print")
        finally:
            # Restaura a impressora padrão original
            win32print.SetDefaultPrinter(impressora_padrao_atual)
    def fechar_tela(self):
        self.excluir_pdf_temporario()
        self.grab_release()
        self.destroy()

class AppTelaItem(tk.Toplevel):
    def __init__(self, master, item):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        #   DEFINIÇÕES DA TELA
        self.ponteiro = item
        self.title("Adicionar Produto")
        self.geometry("320x220")
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
        #   CONTEUDO    
        #       NOME   
        frame_nome = ttk.Frame(self)
        label_nome = ttk.Label(frame_nome, text="Nome:")
        label_nome.pack(padx=(10,2), side="left")
        self.entry_nome = tk.Entry(frame_nome, justify='center')
        self.entry_nome.insert(0,self.ponteiro.nome)
        self.entry_nome.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_nome.pack(padx=10, pady=10, expand=True, fill='x')
        #       QUANTIDADE
        frame_quantidade = ttk.Frame(self)
        label_quantidade = ttk.Label(frame_quantidade, text="Quantidade:")
        label_quantidade.pack(padx=(10,2), side="left")
        self.entry_quantidade = tk.Entry(frame_quantidade, justify='center')
        self.entry_quantidade.insert(0,str(self.ponteiro.quantidade))
        self.entry_quantidade.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_quantidade.pack(padx=10, pady=10, expand=True, fill='x')
        #       PREÇO
        frame_preco = ttk.Frame(self)
        label_preco = ttk.Label(frame_preco, text="Preço:")
        label_preco.pack(padx=(10,2), side="left")
        self.entry_preco = tk.Entry(frame_preco, justify='center')
        self.entry_preco.insert(0,str(self.ponteiro.preco).replace(".", ","))
        self.entry_preco.pack(padx=(0,10), expand=True, fill='x', side="left")
        frame_preco.pack(padx=10, pady=10, expand=True, fill='x')
        #       BOTOES
        botao_adiciona_produto = ttk.Button(self, text="Salvar", command = self.salvar_item)
        botao_adiciona_produto.pack(padx=10)
        botao_cancela = ttk.Button(self, text="Cancela", command = self.fechar_tela)
    def salvar_item(self):
        try:
            self.ponteiro.atualiza(self.entry_nome.get(),self.entry_quantidade.get(),self.entry_preco.get().replace(",", "."))
            self.fechar_tela()
        except:
            messagebox.showinfo("Erro", "Verifique as informações digitadas")
    def fechar_tela(self):
        self.grab_release()
        self.destroy()
 
class AppTelaSelecionaServ(tk.Toplevel):
    def __init__(self, master, item):
        super().__init__(master)
        self.ponteiro = item
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tela)
        #   DEFINIÇÕES DA TELA
        self.title("Adicionar Serviço")
        self.geometry("230x180")
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
        #   CONTEUDO
        label_header = ttk.Label(self, text="Escolha um serviço:", font=("Arial", 12, "bold"))
        label_header.pack()
        botao_servico_xerox = ttk.Button(self, text="Xerox", command=lambda: self.servico(108))
        botao_servico_xerox.pack(pady=10)
        botao_servico_solda_limpeza = ttk.Button(self, text="Solda/Limpeza", command=lambda: self.servico(20))
        botao_servico_solda_limpeza.pack(pady=(0,10))
        botao_servico_taxa_banca = ttk.Button(self, text="Taxa Teste Banca", command=lambda: self.servico(23))
        botao_servico_taxa_banca.pack(pady=(0,10))
        botao_cancela = ttk.Button(self, text="Cancelar", command = self.fechar_tela)
        botao_cancela.pack()
    def servico(self, id):
        self.ponteiro.escolhe(id)
        return self.fechar_tela()    
    def fechar_tela(self):
        self.grab_release()
        self.destroy()

class AppVendas(tk.Frame):
    def __init__(self, master, reinicia_app):
        super().__init__(master)
        #   PARAMETROS INICIAIS
        self.func_reiniciar = reinicia_app
        self.itens_venda_produto = []
        self.itens_venda_servico = []
        self.cliente = ClienteVenda()
        #   PAGINA - FRAMES
        self.frame_header = ttk.Frame(self)
        self.frame_header.pack(expand=True, pady=10)
        self.frame_itens = ttk.Frame(self, borderwidth=2, relief="solid")
        self.frame_itens.pack(expand=True)
        self.frame_footer = ttk.Frame(self)
        self.frame_footer.pack(expand=True)
        #   PAGINA HEADER
        self.label_header = ttk.Label(self.frame_header, text="Adicione itens ao pedido:", font=("Arial", 12, "bold"))
        self.label_header.grid(row=0, column=0, columnspan=2,sticky="ew", padx=10)
        self.entry_produto = tk.Entry(self.frame_header)
        self.entry_produto.grid(row=1, column=0,sticky="ew", padx=10)
        self.botao_adiciona_produto = ttk.Button(self.frame_header, text="Adicionar", command=lambda: self.novo_produto(self.entry_produto.get()))
        self.botao_adiciona_produto.grid(row=1, column=1,sticky="ew", padx=10)
        self.botao_adiciona_servico = ttk.Button(self.frame_header, text="Adicionar Serviço", command = self.novo_servico)
        self.botao_adiciona_servico.grid(row=2, column=0, columnspan=2,sticky="ew", padx=10, pady=6)
        #   PAGINA FRAME PRODUTOS
        label_nome = ttk.Label(self.frame_itens, text="Descrição item", font=("Arial", 12, "bold"))
        label_nome.grid(row=0, column=0, padx=5)
        label_quantidade = ttk.Label(self.frame_itens, text="UN/M", font=("Arial", 12, "bold"))
        label_quantidade.grid(row=0, column=1, padx=5)
        label_preco = ttk.Label(self.frame_itens, text="R$", font=("Arial", 12, "bold"))
        label_preco.grid(row=0, column=2, padx=5)
        label_total = ttk.Label(self.frame_itens, text="Total", font=("Arial", 12, "bold"))
        label_total.grid(row=0, column=3, padx=5)
        self.cont_row_frame_produtos = 1
        #   PAGINA FOOTER
        #       LABEL TOTAL VENDA
        self.label_total_venda = ttk.Label(self.frame_footer, text="Total Venda R$0", font=("Arial", 14, "bold"), anchor="center")
        self.label_total_venda.grid(row=0, column=0, columnspan=7, sticky="ew", padx=20, pady=10)
        #       LABEL/ENTRY DESCONTO
        label_desconto = ttk.Label(self.frame_footer, text="Desconto:", font=("Arial", 12))
        label_desconto.grid(row=1, column=0,sticky="ew", padx=(20, 4))
        self.entry_desconto_venda = tk.Entry(self.frame_footer, justify='center')
        self.entry_desconto_venda.grid(row=1, column=1,sticky="ew", padx=(0,4))
        #       MENU METODO PAGAMENTO
        self.metodo_pagamento = tk.StringVar(self)
        opcoes_metodo_pagamento = ["Dinheiro", "Cartão", "Pix"]
        self.metodo_pagamento.set(opcoes_metodo_pagamento[0])
        menu_selecao = tk.OptionMenu(self.frame_footer, self.metodo_pagamento, *opcoes_metodo_pagamento)
        menu_selecao.grid(row=1, column=2, sticky="ew", pady=10)
        #       BOTAO FINALIZA
        self.botao_finaliza_venda = ttk.Button(self.frame_footer, text="Recibo", command = self.abrir_recibo)
        self.botao_finaliza_venda.grid(row=1, column=3,sticky="ew", padx=(4,10), pady=10)
        #       CHECKBOX GERAR PEDIDO
        self.checkbox_gera_pedido_var = tk.BooleanVar(value=True)
        checkbox_gera_pedido = tk.Checkbutton(self.frame_footer, text = "Gerar Pedido", variable = self.checkbox_gera_pedido_var)
        checkbox_gera_pedido.grid(row=1, column=4, pady=10, padx=2)
        #       CHECKBOX IMPRIMIR CONTROLE INTERNO
        self.checkbox_controle_interno_var = tk.BooleanVar(value=True)
        checkbox_controle_interno = tk.Checkbutton(self.frame_footer, text = "Controle Interno", variable = self.checkbox_controle_interno_var)
        checkbox_controle_interno.grid(row=1, column=5, pady=10)
        #       BOTAO CANCELAR/LIMPAR TELA
        self.botao_cancela_venda = ttk.Button(self.frame_footer, text="Cancela/Limpa", command = reinicia_app)
        self.botao_cancela_venda.grid(row=1, column=6,sticky="ew", padx=20, pady=10)
        #       FRAME SEC FOOTER    OBS E COMPRADOR
        self.frame_footer_sec = ttk.Frame(self.frame_footer)
        self.frame_footer_sec.grid(row=2, column=0, columnspan=10, sticky="ew", padx=20, pady=10)
        label_obs = ttk.Label(self.frame_footer_sec, text="Observação:", font=("Arial", 12))
        label_obs.pack(side="left", expand=True, pady=10)
        self.entry_obs_venda = tk.Entry(self.frame_footer_sec, justify='center')
        self.entry_obs_venda.pack(side="left", expand=True, pady=10)
        label_comprador = ttk.Label(self.frame_footer_sec, text="Comprador:", font=("Arial", 12))
        label_comprador.pack(side="left", expand=True, pady=10)
        self.entry_comprador_venda = tk.Entry(self.frame_footer_sec, justify='center')
        self.entry_comprador_venda.pack(side="left", expand=True, pady=10)
        #       FRAME TER FOOTER    CLIENTE SIS
        frame_footer_ter = ttk.Frame(self.frame_footer)
        frame_footer_ter.grid(row=3, column=0, columnspan=10, sticky="ew", padx=20, pady=10)
        footer_ter_inner = ttk.Frame(frame_footer_ter)
        footer_ter_inner.pack(pady=5)
        botao_selecionar_cliente = ttk.Button(footer_ter_inner, text="Identificar Cliente", command = self.selecionar_cliente)
        botao_selecionar_cliente.pack(side="left", pady=10, padx=50)
        label_cliente = ttk.Label(footer_ter_inner, text="Cliente:", font=("Arial", 12))
        label_cliente.pack(side="left", pady=10, padx=5)
        self.label_cliente_nome = ttk.Label(footer_ter_inner, text=self.cliente.nome, font=("Arial", 12))
        self.label_cliente_nome.pack(side="left", pady=10)

    def selecionar_cliente(self):
        self.cliente_selecionado = None
        self.wait_window(AppDefinirClienteVenda(self))
        if (self.cliente_selecionado):
            self.cliente.atualiza(self.cliente_selecionado[0],self.cliente_selecionado[1])
            self.label_cliente_nome.config(text=self.cliente.nome)
        return
    def novo_produto(self, id):
        try:
            id = int(id)
            try:
                item = ProdutoVenda(id)
                if (item):
                    self.entry_produto.delete(0, tk.END)
                    self.wait_window(AppTelaItem(self, item))
                    self.itens_venda_produto.append(item)
                    return self.adiciona_item(item)
                else:
                    messagebox.showinfo("Erro", "O código de produto informado é inválido (tela)")
            except:
                messagebox.showinfo("Erro", "O código de produto informado é inválido (db/tela)")
        except:
            messagebox.showinfo("Erro", "O código de produto informado é inválido (int)")
    def novo_servico(self):
        item = ServicoVenda()
        self.wait_window(AppTelaSelecionaServ(self, item))
        if (item.id != 0):
            self.wait_window(AppTelaItem(self, item))
            self.itens_venda_servico.append(item)
            return self.adiciona_item(item)
        else:
            return 
    def adiciona_item(self, item):
        item.lnome = ttk.Label(self.frame_itens, text=item.nome[0:15], font=("Arial", 12))
        item.lnome.grid(row=self.cont_row_frame_produtos, column=0, padx=5)
        item.lquantidade = ttk.Label(self.frame_itens, text=str(item.quantidade), font=("Arial", 12))
        item.lquantidade.grid(row=self.cont_row_frame_produtos, column=1, padx=5)
        item.lpreco = ttk.Label(self.frame_itens, text=str(item.preco), font=("Arial", 12))
        item.lpreco.grid(row=self.cont_row_frame_produtos, column=2, padx=5)
        item.ltotal = ttk.Label(self.frame_itens, text=str(item.total), font=("Arial", 12))
        item.ltotal.grid(row=self.cont_row_frame_produtos, column=3, padx=5)
        item.bedita = ttk.Button(self.frame_itens, text="Edita", command=lambda: self.atualiza_item_venda(item))
        item.bedita.grid(row=self.cont_row_frame_produtos, column=4, padx=5)
        item.bremove = ttk.Button(self.frame_itens, text="Remove", command=lambda: self.remove_item_venda(item))
        item.bremove.grid(row=self.cont_row_frame_produtos, column=5, padx=5)
        self.cont_row_frame_produtos += 1
        return self.atualiza_total_venda()
    def atualiza_total_venda (self):
        total_atual = 0
        for item in self.itens_venda_produto:
            total_atual += item.total
        for item in self.itens_venda_servico:
            total_atual += item.total
        self.label_total_venda.config(text=f"Total R${total_atual:.2f}")
        return
    def atualiza_item_venda(self, item):
        self.wait_window(AppTelaItem(self, item))
        item.lnome.config(text=item.nome[0:15])
        item.lquantidade.config(text=str(item.quantidade))
        item.lpreco.config(text=str(item.preco))
        item.ltotal.config(text=str(item.total))
        return self.atualiza_total_venda()
    def remove_item_venda(self, item):
        item.lnome.destroy()
        item.lquantidade.destroy()
        item.lpreco.destroy()
        item.ltotal.destroy()
        item.bedita.destroy()
        item.bremove.destroy()
        if (item.tipo == "produto"):
            self.itens_venda_produto.remove(item)
        else:
            self.itens_venda_servico.remove(item)
        del item
        return self.atualiza_total_venda()
    def abrir_recibo(self):
        if (self.itens_venda_produto or self.itens_venda_servico):
            self.wait_window(AppTelaRecibo(self))
            messagebox.showinfo("Aviso", "Venda concluida!")
            self.func_reiniciar()
        else:
             messagebox.showinfo("Erro", "Você ainda não adicionou nenhum produto!")