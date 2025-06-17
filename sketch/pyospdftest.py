from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

# Define as margens da página (opcional)
pdf.set_margins(left=15, top=15, right=15)

# Define a fonte para o cabeçalho
pdf.set_font("Arial", size=10)

# Insere o logo da LTC (substitua pelo caminho da sua imagem)
pdf.image("logo.png", x=10, y=10, w=30)

# Define a posição inicial para o texto
x = 45

# Insere o texto "LTC TECNOLOGIA"
pdf.text(x=x, y=15, txt="LTC TECNOLOGIA")

# Insere os dados da empresa
pdf.set_font_size(8)
pdf.text(x=x, y=20, txt="LUIZ VOLKART, 35")
pdf.text(x=120, y=20, txt="CENTRO")
pdf.text(x=x, y=25, txt="TRES COROAS-RS")

# Insere os telefones e email
pdf.text(x=130, y=15, txt="Telefones:")
pdf.text(x=150, y=15, txt="51 98571-9957")
pdf.text(x=150, y=20, txt="51 3546-2168")
pdf.text(x=130, y=25, txt="E-mail:")
pdf.text(x=150, y=25, txt="ltctecnologiavendas@gmail.com")

# Linha divisória
pdf.line(10, 40, 200, 40)

# Insere "ORDEM DE SERVIÇO" com destaque
pdf.set_font("Arial", size=12, style="B")
pdf.text(x=80, y=50, txt="ORDEM DE SERVIÇO")

# Define a fonte para os campos "OS", "DATA" e "HORA"
pdf.set_font("Arial", size=10)

# Campos "OS", "DATA" e "HORA"
pdf.text(x=160, y=50, txt="OS: xxxxxx")
pdf.text(x=160, y=60, txt="DATA: dd/mm/aaaa")
pdf.text(x=160, y=70, txt="HORA: hh:mm")


# Caixas "SM", "ST" e "SG"
pdf.text(x=10, y=80, txt="SM")
pdf.rect(x=30, y=75, w=3, h=3)

pdf.text(x=50, y=80, txt="ST")
pdf.rect(x=70, y=75, w=3, h=3)

pdf.text(x=90, y=80, txt="SG")
pdf.rect(x=110, y=75, w=3, h=3)

# Salva o PDF
pdf.output("ordem_de_servico.pdf")