from fundo_quant.executores import ExecutorLongOnly
from fundo_quant.operacional import Ativo, Ordem
from datetime import datetime


def teste_compra():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 10


def teste_compra_e_venda():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=Ordem.VENDER, preco=8, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0


def teste_pl_dps_da_compra_e_venda():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=Ordem.VENDER, preco=8, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=10) == 80


def teste_compra_depois_compra():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=8, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 10


def teste_venda_a_descoberto():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo)
    ex.executar_ordem(ordem=Ordem.VENDER, preco=10, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0


def teste_stop_loss_valor_positivo():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo, stop_loss=0.03)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=None, preco=8, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0


def teste_stop_loss_valor_negativo():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo, stop_loss=-0.03)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=None, preco=8, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0


def teste_stop_gain_valor_positivo():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo, stop_gain=0.03)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=None, preco=12, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0


def teste_stop_gain_valor_negativo():
    ativo = Ativo(100)
    ex = ExecutorLongOnly(ativo, stop_gain=-0.03)
    ex.executar_ordem(ordem=Ordem.COMPRAR, preco=10, horario=datetime(2022, 1, 1))
    ex.executar_ordem(ordem=None, preco=12, horario=datetime(2022, 1, 1))
    assert ativo.obter_posicao() == 0
