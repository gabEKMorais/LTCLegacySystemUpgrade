import pyodbc

def verificar_campos_tabela_access_pyodbc(caminho_banco_access, nome_tabela):
    """
    Verifica todos os campos de uma tabela do Access e identifica
    se algum deles tem a propriedade de auto incremento usando pyodbc.
    Esta versão verifica o tipo de dados 'COUNTER' para identificar
    campos de auto incremento, caso 'SQL_AUTO_INCREMENT' não seja exposto
    pelo driver.

    Args:
        caminho_banco_access (str): O caminho completo para o arquivo .accdb ou .mdb do Access.
        nome_tabela (str): O nome da tabela a ser verificada.
    """
    conn = None
    cursor = None
    try:
        # String de conexão para o Access via ODBC
        conn_str = (
            f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
            f"DBQ={caminho_banco_access};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print(f"--- Detalhes dos Campos da Tabela '{nome_tabela}' ---")
        encontrou_autoincremento = False

        # Obtém informações sobre as colunas da tabela
        columns_info = cursor.columns(table=nome_tabela)

        for col_info in columns_info:
            nome_campo = col_info.column_name
            is_autoincremento = False

            # Primeira tentativa: verificar o atributo sql_auto_increment (se o driver expuser)
            if hasattr(col_info, 'sql_auto_increment') and col_info.sql_auto_increment:
                is_autoincremento = True
                encontrou_autoincremento = True
            # Segunda tentativa: verificar o tipo de dados se for 'COUNTER' (para Access)
            elif col_info.type_name and col_info.type_name.upper() == 'COUNTER':
                is_autoincremento = True
                encontrou_autoincremento = True
            # Também pode ser interessante verificar o DATA_TYPE numérico
            # Para Access, Counter (AutoIncrement) é geralmente um tipo INTEGER (SQL_INTEGER = 4)
            # mas com características especiais. O 'type_name' 'COUNTER' é mais específico.
            # else:
            #     # Poderíamos verificar outros atributos se necessário,
            #     # como o `data_type` numérico, mas 'COUNTER' é o mais claro para auto incremento.
            #     # print(f"DEBUG: {nome_campo} - data_type: {col_info.data_type}, type_name: {col_info.type_name}")
            #     pass


            print(f"  Campo: {nome_campo}")
            print(f"    Tipo de Dados (ODBC): {col_info.type_name}")
            print(f"    É Auto Incremento: {'Sim' if is_autoincremento else 'Não'}")
            print("-" * 30)

        if not encontrou_autoincremento:
            print(f"Nenhum campo de auto incremento encontrado na tabela '{nome_tabela}' usando os métodos conhecidos.")
            print("Verifique manualmente no Access se existe algum campo de 'Contador'.")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Ocorreu um erro ao conectar ou consultar o banco de dados:")
        print(f"SQLSTATE: {sqlstate}")
        print(f"Mensagem: {ex.args[1]}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Como usar o script ---
if __name__ == "__main__":
    # Substitua pelo caminho real do seu banco de dados Access
    caminho_do_seu_banco = r'\\LTC-SV\G & M Systens\PRINCIPAL.MDB'
    # Substitua pelo nome da tabela que você quer verificar
    nome_da_tabela = "Pedidos"

    verificar_campos_tabela_access_pyodbc(caminho_do_seu_banco, nome_da_tabela)
