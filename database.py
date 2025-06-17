import pyodbc
from config import CONN_STR
 
class ConectarDB:
    def __init__(self):
        # Criando conexão.
        self.con = pyodbc.connect(CONN_STR)
        # Criando cursor.
        self.cur = self.con.cursor()     
    def consultar_produto_name(self, id_produto):
        try:
            self.cur.execute(f'SELECT "Descrição do produto" FROM Produtos WHERE "Código do produto" = {id_produto}')
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
    def consulta_service(self, id_service):
        try:
            self.cur.execute(f'SELECT "Descrição do serviço", "Valor" FROM Servicos WHERE "Código do servico" = {id_service}')
            return self.cur.fetchall()
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
    def consulta_itens_pedido(self,id_ped):
        try:
            self.cur.execute(f'SELECT "Código do servico","Código do produto","Quantidade","Valor unitário" FROM "Pedidos_itens" WHERE "Número do pedido" = {id_ped}')
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
    def consulta_produto(self, id):
        try:
            self.cur.execute(f'SELECT "Descrição do produto","Valor venda" FROM "Produtos" WHERE "Código do produto" = {id}')
            return self.cur.fetchall()
        except pyodbc.Error as ex:
            print(f"Erro ao executar a consulta: {ex}")
            return []
    def fechar_conexao(self):
        if self.con:
            self.con.close()

class consulta_orcamento:
    def __init__(self, id_orc):        
        services_init = [44, 5, 82, 14]    # 44 m obra - 5 hr tecnico - 82 hr aj tecnico - 14 km a mais
        banco = ConectarDB()
        if (id_orc == None):
            self.array_produtos = []
        else:
            id_orc = int(id_orc)
            itens_temp = banco.consultar_itens_orçamento_orc(id_orc)
            if (itens_temp):
                self.tem_orc = True
                self.array_produtos = []
                for item in itens_temp:
                    if(item[0] != 0):
                        self.array_produtos.append(orcamento_produto(item[0], banco.consultar_produto_name(item[0])[0][0], item[1], item[2]))
            else:
                self.tem_orc = False
        self.array_services = []
        for id in services_init:
            retorno = banco.consulta_service(id)
            self.array_services.append(orcamento_servico(id, retorno[0][0], retorno[0][1])) #[0][0] Nome [0][1] Valor
        banco.fechar_conexao()
    def novo_produto (self, nome, valor, un):
        item = orcamento_produto(None, nome.upper(), int(un), float(valor))
        self.array_produtos.append(item)
        return item
    def novo_servico (self, nome, valor):
        item = orcamento_servico(None, nome.upper(), float(valor))
        self.array_services.append(item)
        return item
class orcamento_produto:
    def __init__(self, codigo, nome, un, valor):
        self.tipo = "produto"
        self.codigo = codigo
        self.nome = nome
        self.un = int(un)
        self.valor = valor
        self.total = un*valor   
        self.fixo = True
        self.remove = False
    def atualiza(self, nome, valor, un):
        self.nome = nome.upper()
        self.valor = valor
        self.un = int(un)
        self.total = float(self.valor)*self.un
class orcamento_servico:
    def __init__(self, codigo, nome, valor):
        self.tipo = "servico"
        self.codigo = codigo
        self.nome = nome
        self.valor = valor
        self.remove = False
    def atualiza(self, nome, valor):
        self.nome = nome
        self.valor = valor

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
                obj_temp = relatorio_item(item[0], banco.consulta_service_name(item[0])[0][0], item[2], item[3])
                self.array_servicos.append(obj_temp)
            else:
                obj_temp = relatorio_item(item[1], banco.consultar_produto_name(item[1])[0][0], item[2], item[3])
                self.array_produtos.append(obj_temp)
            self.valor_total_os += (item[2] * item[3])
        self.problema = banco.consulta_os_problema(id_os)[0][0]
        banco.fechar_conexao()
class consulta_pedido_relatorio:
    def __init__(self, id_ped):
        banco = ConectarDB()
        self.id = id_ped
        self.array_itens = []
        self.valor_total_ped = 0
        consulta = banco.consulta_itens_pedido(self.id)
        for item in consulta: # serv/prod, nome, un, vl
            if (item[0] != 0):
                obj_temp = relatorio_item(item[0], banco.consulta_service_name(item[0])[0][0], item[2], item[3])
                self.array_itens.append(obj_temp)
            else:
                obj_temp = relatorio_item(item[1], banco.consultar_produto_name(item[1])[0][0], item[2], item[3])
                self.array_itens.append(obj_temp)
            self.valor_total_ped += (item[2] * item[3])
        banco.fechar_conexao()

class relatorio_item:
    def __init__(self, codigo, nome, un, valor):
        self.codigo = codigo
        self.nome = nome
        self.un = un
        self.valor = valor
        self.total = un*valor

class ProdutoVenda:
    def __init__(self, id):
        self.id = id
        self.novo = True
        self.tipo = "produto"
        self.quantidade = 1
        banco = ConectarDB()
        consulta = banco.consulta_produto(id)
        if (consulta):
            self.nome = consulta[0][0]
            self.preco = float(consulta[0][1])
            self.total = self.preco
            banco.fechar_conexao()
            return
        else:
            banco.fechar_conexao()
            return False
    def atualiza(self, nome, quantidade, preco):
        self.nome = nome
        self.quantidade = int(quantidade)
        self.preco = float(preco)
        self.total = self.quantidade*self.preco
class ServicoVenda:
    def __init__(self):
        self.id = 0
        self.novo = True
        self.tipo = "servico"
    def escolhe(self, id):
        self.id = id
        self.quantidade = 1
        banco = ConectarDB()
        consulta = banco.consulta_service(id)
        if (consulta):
            self.nome = consulta[0][0]
            self.preco = float(consulta[0][1])
            self.total = self.preco
            banco.fechar_conexao()
            return
        else:
            banco.fechar_conexao()
            return False
    def atualiza(self, nome, quantidade, preco):
        self.nome = nome
        self.quantidade = int(quantidade)
        self.preco = float(preco)
        self.total = self.quantidade*self.preco
