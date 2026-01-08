#CORES UTILIZADAS
VERMELHO_PADRAO = [246, 19, 23]
AZUL_PADRAO = [89, 197, 207]
BRANCO = 255
PRETO = 0
CINZA = 128
FUNDO_TEXTO_ITENS = 220
FUNDO_APP_PRINCIPAL_HEADER = "#59C5CF"
FUNDO_APP_PRINCIPAL_HEADER_SELECAO = "lightblue"

#ACESSO AO DB
MDB = r'C:\Users\Gabriel\Desktop\PY\TESTES.MDB'
DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
CONN_STR = ';'.join(['DRIVER=' + DRV, 'DBQ=' + MDB])

#API GEMINI
API_KEY = "AIzaSyD9CtcWlzO3wgBFOuEG3ZHEE0oPEYLYXzU"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
