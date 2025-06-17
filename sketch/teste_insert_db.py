import pyodbc
import time
import datetime

#ACESSO AO DB
MDB = r'C:\Users\LTC Recepcao\Desktop\PY\sketch\TESTES.MDB'  #r'C:\Users\LTC\Desktop\gabe\PY\DBPARATESTE.MDB'
DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
CONN_STR = ';'.join(['DRIVER=' + DRV, 'DBQ=' + MDB])

class RegistrarVendaTeste():
    def __init__(self):
        self.con = pyodbc.connect(CONN_STR)
        self.cur = self.con.cursor()  
        self.data = datetime.datetime.now()
        self.numero_pedido = 1999
        self.numero_pedido_nominal = f"PED{str(self.numero_pedido)}-01"
        #print(self.numero_pedido_nominal)
        #self.tabela_pagamentos_cre()
        #self.pegar_dados_por_id("Cre", "Número do documento", self.numero_pedido_nominal)
        #self.pegar_dados_por_id("Pagamentos cre", "Número do documento")
        #self.pegar_dados_com_nomes_de_campo("Pagamentos cre", "Número do documento")
        #self.tabela_pagamentos_cre_via_passthrough()
        #print(self.definir_numero_pedido())
        print(self.baixa_estoque())

    def baixa_estoque(self, item):
        nome_tabela = "Produtos" # Colchetes para o nome com espaço
        coluna_valor = "Estoque"
        coluna_where = "Código do produto"
        valor_where = item.id
        try:
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
            self.cur.execute(sql_select, (valor_where,))
            resultado = self.cur.fetchone()
            if resultado:
                set_coluna = "Estoque"
                valor = resultado[0] - item.quantidade
                where_coluna = "Código do produto"
                where_valor = item.id
                set_clause = f"[{set_coluna}] = ?"
                sql_update = f"UPDATE [{nome_tabela}] SET {set_clause} WHERE [{where_coluna}] = ?;"
                valores = (valor, where_valor)
                self.cur.execute(sql_update, valores)
                self.con.commit()
                return resultado[0], valor
            else:
                return 0
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return 0

    def definir_numero_pedido(self):
        nome_tabela = "SYS~Sequencial" # Colchetes para o nome com espaço
        coluna_valor = "Valor"
        coluna_where = "Tabela"
        valor_where = "Pedidos"
        try:
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
            self.cur.execute(sql_select, (valor_where,))
            resultado = self.cur.fetchone()
            if resultado:
                return resultado[0] 
            else:
                return 0
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return 0

    def pegar_dados_por_id(self, nome_tabela, nome_campo_id, id_valor="OS17727-03"):
        try:
            # Usando colchetes para o nome da tabela e do campo para lidar com espaços ou palavras reservadas
            sql_select = f"SELECT * FROM [{nome_tabela}] WHERE [{nome_campo_id}] = ?;"
            
            print(f"DEBUG SELECT SQL: {sql_select}")
            print(f"DEBUG SELECT ID Valor: {id_valor}")

            self.cur.execute(sql_select, (id_valor,))
            
            resultados = self.cur.fetchall() # Pega todas as linhas que correspondem
            
            if resultados:
                print(f"DEBUG: Registros encontrados na tabela '{nome_tabela}' para ID '{id_valor}':")
                for row in resultados:
                    print(row)
                return resultados
            else:
                print(f"DEBUG: Nenhum registro encontrado na tabela '{nome_tabela}' para ID '{id_valor}'.")
                return []
                
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao pegar dados por ID na tabela '{nome_tabela}': {sqlstate}")
            return []
        except Exception as e:
            print(f"Ocorreu um erro ao pegar dados por ID na tabela '{nome_tabela}': {e}")
            return []        

    def pegar_dados_com_nomes_de_campo(self, nome_tabela, nome_campo_id, id_valor="OS25448-01"):
        try:
            sql_select = f"SELECT * FROM [{nome_tabela}] WHERE [{nome_campo_id}] = ?;"
            
            print(f"DEBUG SELECT SQL (para nomes de campo): {sql_select}")
            print(f"DEBUG SELECT ID Valor (para nomes de campo): {id_valor}")

            self.cur.execute(sql_select, (id_valor,))
            
            # Pega os nomes das colunas a partir da descrição do cursor
            colunas = [column[0] for column in self.cur.description]
            
            resultados = self.cur.fetchall()
            
            if resultados:
                print(f"DEBUG: Registros encontrados na tabela '{nome_tabela}' para ID '{id_valor}' (com nomes de campo):")
                for row in resultados:
                    # Cria um dicionário para cada linha, mapeando nome do campo para o valor
                    registro_formatado = dict(zip(colunas, row))
                    print(registro_formatado)
                return resultados
            else:
                print(f"DEBUG: Nenhum registro encontrado na tabela '{nome_tabela}' para ID '{id_valor}'.")
                return []
                
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao pegar dados por ID com nomes de campo na tabela '{nome_tabela}': {sqlstate}")
            return []
        except Exception as e:
            print(f"Ocorreu um erro ao pegar dados por ID com nomes de campo na tabela '{nome_tabela}': {e}")
            return [] 

    def inserir(self, nome_tabela, colunas_para_inserir, valores_para_inserir):
        try:
            nomes_colunas_str = "(" + ", ".join([f"[{c}]" for c in colunas_para_inserir]) + ")"
            placeholders_str = "(" + ", ".join(["?"] * len(valores_para_inserir)) + ")"
            sql_insert = f"INSERT INTO {nome_tabela} {nomes_colunas_str} VALUES {placeholders_str}"
            print(sql_insert, valores_para_inserir)
            self.cur.execute(sql_insert, valores_para_inserir)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao inserir registro: {sqlstate}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
            return False
        self.con.commit()
        return True
        
    def tabela_pagamentos_cre(self):
        nome_tabela = "[Pagamentos cre]"
        valores_para_inserir = [
            self.numero_pedido_nominal,
            datetime.datetime(2025, 5, 27, 0, 0),
            float(1),
            "Teste OBS"
        ]
        colunas_para_inserir = [
            "Número do documento",
            "Data",
            "Valor",
            "Obs"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)

    def inserir_via_passthrough(self, nome_query_passthrough: str, valores: list):
        try:
            print(f"DEBUG Executando Pass-Through Query: {nome_query_passthrough}")
            print(f"DEBUG Valores para Pass-Through: {valores}")
            print(f"DEBUG Tipos dos Valores para Pass-Through: {[type(v) for v in valores]}")
            self.cur.execute(nome_query_passthrough, valores)
            self.con.commit()
            print(f"DEBUG: Execução da Pass-Through Query '{nome_query_passthrough}' bem-sucedida.")
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao executar Pass-Through Query '{nome_query_passthrough}': {sqlstate}")
            return False
        except Exception as e:
            print(f"Ocorreu um erro ao executar Pass-Through Query '{nome_query_passthrough}': {e}")
            return False

    def tabela_pagamentos_cre_via_passthrough(self):
        nome_query = "qpy_InsertPagamentosCre"
        valores_para_inserir = [
            self.numero_pedido_nominal, 
            self.data, 
            1.0, 
            "Teste OBS", 
        ]
        return self.inserir_via_passthrough(nome_query, valores_para_inserir)

RegistrarVendaTeste()