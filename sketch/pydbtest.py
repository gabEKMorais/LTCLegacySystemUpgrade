import pyodbc

# Dados de conexão com o banco de dados Access
MDB = r'\\LTC-SV\G & M Systens\PRINCIPAL.MDB'  # Substitua pelo caminho do seu arquivo .accdb
DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
conn_str = ';'.join(['DRIVER=' + DRV, 'DBQ=' + MDB])

try:
    # Estabelece a conexão com o banco de dados
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Executa a consulta SQL para selecionar o primeiro registro da tabela Clientes
    conteudo = cursor.execute("SELECT * FROM Clientes").fetchall()  # Substitua "Clientes" pelo nome da sua tabela, se for diferente

    # Verifica se há resultados e imprime o primeiro registro
    if conteudo:
        print(conteudo)
    else:
        print("A tabela Clientes está vazia.")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Erro de banco de dados: {sqlstate}")

finally:
    # Fecha a conexão com o banco de dados
    if conn:
        conn.close()