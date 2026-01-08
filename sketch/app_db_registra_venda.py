import pyodbc
from config import CONN_STR

class RegistrarVenda():
    def __init__(self, recibo, app_venda):
        self.registrado = False
        self.venda = recibo
        self.app_master = app_venda
        self.con = pyodbc.connect(CONN_STR)
        self.cur = self.con.cursor()  
        self.numero_pedido = (self.definir_numero_pedido() + 1)
        if isinstance(self.numero_pedido, int):
            self.numero_pedido_nominal = f"PED{str(self.numero_pedido)}-01"
        else:
            return
        if not (self.tabela_pedidos()):
            return
        if not (self.atualiza_sequencial()):
            return
        self.con.commit()
        cont_indice_item = 1
        for item in app_venda.itens_venda_produto:
            if not (self.tabela_pedidos_itens(item, cont_indice_item)):
                print("Parou: Produto")
                return
            self.baixa_estoque(item)
            cont_indice_item += 1
        for item in app_venda.itens_venda_servico:
            if not (self.tabela_pedidos_itens(item, cont_indice_item)):
                print("Parou: Serviço")
                return
            cont_indice_item += 1
        self.con.commit()
        if not (self.tabela_cre()):
            print("Parou: Cre")
            return
        if not (self.tabela_pagamentos_cre()):
            print("Parou: Pagamentos Cre")
            return
        self.registrado = True
        return self.fechar_conexao()

    def atualiza_sequencial(self):
        #print(f"Iniciado: Sequencial")
        try:
            nome_tabela = "SYS~Sequencial"
            set_colunas = {"Valor": str(self.numero_pedido), "Valor Anterior": str(self.numero_pedido-1)}
            where_coluna = "Tabela"
            where_valor = "Pedidos"
            set_parts = [f"[{col}] = ?" for col in set_colunas.keys()]
            set_clause = ", ".join(set_parts)
            valores = list(set_colunas.values())
            valores.append(where_valor)
            sql_update = f"UPDATE [{nome_tabela}] SET {set_clause} WHERE [{where_coluna}] = ?;"
            self.cur.execute(sql_update, valores)
            #print(f"DEBUG: Atualização em '{nome_tabela}' bem-sucedida para '{where_coluna}' = '{where_valor}'")
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
        return True         
    def inserir(self, nome_tabela, colunas_para_inserir, valores_para_inserir):
        #print(f"Iniciado: {nome_tabela}")
        try:
            nomes_colunas_str = "(" + ", ".join([f"[{c}]" for c in colunas_para_inserir]) + ")"
            placeholders_str = "(" + ", ".join(["?"] * len(valores_para_inserir)) + ")"
            sql_insert = f"INSERT INTO {nome_tabela} {nomes_colunas_str} VALUES {placeholders_str}"
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
        #print(f"Finalizado: {nome_tabela}")
        return True
    def tabela_pedidos(self):    
        nome_tabela = "[Pedidos]"
        valores_para_inserir = [
            self.numero_pedido,
            self.venda.data,
            self.app_master.cliente.id,
            self.venda.comprador,
            1,
            "01",
            self.venda.total,
            self.venda.observacao_venda,
            1,
            self.venda.data
        ]
        colunas_para_inserir = [
            "Número do pedido", # numero
            "Data", # data/hora
            "Código do cliente", # numero
            "Comprador", # texto curto
            "Código da condição", # numero
            "Código da forma de pgto", # texto curto
            "Total", # numero
            "Observações", # texto longo
            "Código do vendedor", # numero
            "Data conclusão" # data/hora
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def tabela_pedidos_itens(self, item, indice_item):
        nome_tabela = "[Pedidos_itens]"
        if (item.tipo == "produto"):
            valores_para_inserir = [
                self.numero_pedido,
                item.id,
                item.quantidade,
                item.preco,
                item.preco,
                0,
                "UN",
                indice_item
            ]
        else:
            valores_para_inserir = [
                self.numero_pedido,
                0,
                item.quantidade,
                item.preco,
                item.preco,
                item.id,
                "UN",
                indice_item
            ]
        colunas_para_inserir = [
            "Número do pedido",
            "Código do produto",
            "Quantidade",
            "Valor unitário",
            "Valor",
            "Código do servico",
            "Um",
            "Sequencial"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def baixa_estoque(self, item):
        nome_tabela = "Produtos" # Colchetes para o nome com espaço
        coluna_valor = "Estoque"
        coluna_where = "Código do produto"
        valor_where = item.id
        try:
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            #print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            #print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
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
                return resultado[0], valor
            else:
                return 0
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return 0
    def tabela_cre(self):
        nome_tabela = "[Cre]"
        valores_para_inserir = [
            self.numero_pedido_nominal,
            1,
            self.venda.data,
            self.venda.data,
            self.app_master.cliente.id,
            1,
            "GERADO AUTOMATICAMENTE PELO SISTEMA DE VENDAS",
            self.venda.total,
            self.venda.desconto,
            self.venda.valor_pago,
            0,
            self.venda.data,
            self.venda.data,
            self.numero_pedido,
            1,
            "01",
            0,
            1,
            0,
            True,
            0
        ]
        colunas_para_inserir = [
            "Número do documento",
            "Parcela",
            "Data do lançamento",
            "Vencimento",
            "Código do cliente",
            "Código do vendedor",
            "Observações",
            "Valor",
            "Abatimentos",
            "Valor pago",
            "Saldo",
            "Datajuros",
            "Datadescontos",
            "Número do pedido",
            "Código da condição",
            "Código da forma de pgto",
            "Número da os",
            "Código do banco",
            "Número impresso",
            "Baixa automaticamente",
            "Juros cre"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def tabela_pagamentos_cre(self):
        nome_tabela = "[Pagamentos cre]"
        valores_para_inserir = [
            self.numero_pedido_nominal,
            self.venda.data,
            self.venda.valor_pago,
            self.app_master.metodo_pagamento.get()
        ]
        colunas_para_inserir = [
            "Número do documento",
            "Data",
            "Valor",
            "Obs"
        ]
        return self.inserir(nome_tabela, colunas_para_inserir, valores_para_inserir)
    def definir_numero_pedido(self):
        try:
            nome_tabela = "SYS~Sequencial"
            coluna_valor = "Valor"
            coluna_where = "Tabela"
            valor_where = "Pedidos"
            sql_select = f"SELECT [{coluna_valor}] FROM [{nome_tabela}] WHERE [{coluna_where}] = ?;"
            #print(f"DEBUG SQL SELECT (valor sequencial): {sql_select}")
            #print(f"DEBUG Valor WHERE (valor sequencial): {valor_where}")
            self.cur.execute(sql_select, (valor_where,))
            resultado = self.cur.fetchone()
            if resultado:
                return int(resultado[0] )
            else:
                return False
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao ler o atributo: {sqlstate}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        return False
    def fechar_conexao(self):
        try:
            self.con.commit()
            #print("Dados salvos com sucesso!")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
