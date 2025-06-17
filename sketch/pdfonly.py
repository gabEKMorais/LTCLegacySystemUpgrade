import datetime
from fpdf import FPDF

# VARIAVEIS GLOBAIS CONSTANTES
VERMELHO_PADRAO = [246, 19, 23]
AZUL_PADRAO = [89, 197, 207]
BRANCO = 255
PRETO = 0

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15) # Arial bold 15
        w = self.get_string_width(title) + 6 # Calculate width of title and position
        self.set_x((210 - w) / 2) # set width of title
        self.set_text_color(PRETO) # color of text
        self.cell(w, 9, title, 0, 1, 'C', 0) # Title
        self.ln(10) # Line break

    def footer(self):
        self.set_y(-15) # Position at 1.5 cm from bottom
        self.set_font('Arial', 'I', 8) # Arial italic 8
        self.set_text_color(128) # Text color in gray
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C') # Page number

    def chapter_title(self, num, label):
        self.set_font('Arial', '', 12) # Arial 12
        self.set_fill_color(AZUL_PADRAO[0], AZUL_PADRAO[1], AZUL_PADRAO[2]) # Background color
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1) # Title
        self.ln(4) # Line break

    def chapter_body(self, name):
        with open(name, 'rb') as fh:# Read text file
            txt = fh.read().decode('latin-1')
        self.set_font('Times', '', 12)# Times 12
        self.multi_cell(0, 5, txt) # Output justified text
        self.ln() # Line break
        self.set_font('', 'I') # Mention in italics
        #self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)

pdf = PDF() # inicia o objeto PDF
current_date = datetime.datetime.now().strftime("%d/%m/%Y") # Get current date
title = 'LTC TECNOLOGIA ORÇAMENTO   ' + current_date # define o título
pdf.set_title(title) # define o título do objeto PDF
pdf.set_author('LTC TECNOLOGIA') # define o autor do objeto PDF
pdf.print_chapter(1, 'Texto gerado', '20k_c1.txt')
pdf.print_chapter(2, 'Por que você usa?', '20k_c2.txt')
pdf.output('tuto1.pdf', 'F')