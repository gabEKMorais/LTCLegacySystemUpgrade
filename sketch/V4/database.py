import pyodbc
from config import CONN_STR
 
class ConectarDB:
    def __init__(self):
        # Criando conexão.
        self.con = pyodbc.connect(CONN_STR)
        # Criando cursor.
        self.cur = self.con.cursor()
    def consultar_cliente_name(self, id_cliente):
        try:
            self.cur.execute(f'SELECT "Nome do cliente" FROM Clientes WHERE "Código do cliente" = {id_cliente}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []       
    def consultar_produto_name(self, id_produto):
        try:
            self.cur.execute(f'SELECT "Descrição do produto" FROM Produtos WHERE "Código do produto" = {id_produto}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []    
    def consultar_orçamento_orc(self, id_orcamento):
        try:
            self.cur.execute(f'SELECT "Código do cliente" FROM Vendas WHERE "Número da venda" = {id_orcamento}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consultar_itens_orçamento_orc(self, id_orcamento):
        try:
            self.cur.execute(f'SELECT "Código do produto","Quantidade","Valor unitário" FROM Vendas_itens WHERE "Número da venda" = {id_orcamento}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_services(self, array_services):
        try:
            if (array_services):
                interrogacoes = ", ".join("?" * len(array_services))  # Cria "?, ?, ?, ?"
                sql = f'SELECT "Descrição do serviço", "Valor" FROM Servicos WHERE "Código do servico" IN ({interrogacoes})'
                self.cur.execute(sql, tuple(array_services))
                return self.cur.fetchall()
            else:
                print("Erro ao executar a consulta: lista vazia")
                return [] 
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_service_name(self,id_service):
        try:
            self.cur.execute(f'SELECT "Descrição do serviço" FROM Servicos WHERE "Código do servico" = {id_service}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_itens_os(self,id_os):
        try:
            self.cur.execute(f'SELECT "Código do servico","Código do produto","Quantidade","Valor unitário" FROM "OS itens" WHERE "Número da os" = {id_os}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def consulta_os_problema(self,id_os):
        try:
            self.cur.execute(f'SELECT "problema" FROM "OS" WHERE "Número da os" = {id_os}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def fechar_conexao(self):
        if self.con:
            self.con.close()

def consulta_orcamento_itens(id_orc):
    banco = ConectarDB()
    orc = banco.consultar_orçamento_orc(id_orc)
    nomeCliente = banco.consultar_cliente_name(orc[0][0])
    totalorc = 0
    orcItens = banco.consultar_itens_orçamento_orc(id_orc)
    orcItensArray = []
    for item in orcItens:
        orcItemArray = []
        if (item[0] != 0): # nome un valor total
            produtoOrc = banco.consultar_produto_name(int(item[0]))
            orcItemArray.append(produtoOrc[0][0])
            orcItemArray.append(int(item[1]))
            orcItemArray.append(item[2])
            orcItemArray.append(item[1] * item[2])
            orcItemArray.append(False)
            orcItensArray.append(orcItemArray)
    banco.fechar_conexao()
    return totalorc, orcItensArray, nomeCliente[0][0]

def consulta_orcamento_servicos(array_services):
    banco = ConectarDB()
    array_servicos = []
    array_servicos_temp = banco.consulta_services(array_services)
    for item in array_servicos_temp:
        array_servicos_temp2 = []
        array_servicos_temp2.append(item[0])
        array_servicos_temp2.append(1)
        array_servicos_temp2.append(item[1])
        array_servicos_temp2.append(0)
        array_servicos.append(array_servicos_temp2)
    banco.fechar_conexao()
    return array_servicos

class consulta_os_relatorio:
    def __init__(self, id_os):
        banco = ConectarDB()
        self.os = id_os
        self.array_produtos = []
        self.array_servicos = []
        self.valor_total_os = 0
        self.detalha_servicos = True
        consulta = banco.consulta_itens_os(self.os)
        for item in consulta: # serv/prod, nome, un, vl
            if (item[0] != 0):
                obj_temp = relatorio_produto(item[0], banco.consulta_service_name(item[0])[0][0], item[2], item[3])
                self.array_servicos.append(obj_temp)
            else:
                obj_temp = relatorio_servico(item[0], banco.consultar_produto_name(item[1])[0][0], item[2], item[3])
                self.array_produtos.append(obj_temp)
            self.valor_total_os += (item[2] * item[3])
        self.problema = banco.consulta_os_problema(id_os)[0][0]
        banco.fechar_conexao()
class relatorio_produto():
    def __init__(self, codigo, nome, un, valor):
        self.codigo = codigo
        self.nome = nome
        self.un = un
        self.valor = valor
        self.total = un*valor
class relatorio_servico():
    def __init__(self, codigo, nome, un, valor):
        self.codigo = codigo
        self.nome = nome
        self.un = un
        self.valor = valor
        self.total = un*valor