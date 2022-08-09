from fundo_quant.operacional import Ativo, Compra, Venda
from datetime import datetime


def testar_compra():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_posicao() == 5


def testar_venda():
    ativo = Ativo()
    ativo.vender(preco=10, quantidade=2, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_posicao() == -5


def testar_quantidade_comprada():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_quantidade_comprada() == 5


def testar_quantidade_vendida():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_quantidade_vendida() == 6


def testar_fechar_posicao():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.fechar_posicao(preco=10, horario=datetime.now())
    assert ativo.obter_posicao() == 0


def testar_inverter_posicao():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.inverter_posicao(preco=10, horario=datetime.now())
    assert ativo.obter_posicao() == -2


def testar_operacoes_abertas_v1():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 2))
    assert ativo.obter_operacoes_abertas() == [Compra(preco=10, quantidade=5, horario=datetime(2022, 1, 2))]


def testar_operacoes_abertas_v_2():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 2))
    assert ativo.obter_operacoes_abertas() == [Venda(preco=10, quantidade=5, horario=datetime(2022, 1, 2))]


def testar_operacoes_abertas_v_3():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.inverter_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    assert ativo.obter_operacoes_abertas() == [Compra(preco=10, quantidade=1, horario=datetime(2022, 1, 1))]


def testar_preco_medio_comprado():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=20, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 15


def testar_preco_medio_inverter_posicao():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.inverter_posicao(preco=20, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 20


def testar_preco_medio_fechar_posicao():
    ativo = Ativo()
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=20, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 0


def testar_preco_medio_vendido():
    ativo = Ativo()
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.vender(preco=20, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 15
