import numpy as np
import pandas as pd

from fundo_quant.operacional import Historico, Operacao, Posicao
from datetime import datetime


def test_registro_multiplo():
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=1, preco=1)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=2, preco=1)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=5, preco=1)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=2, preco=1)
    ops.registrar(op)
    assert len(ops._operacoes) == 5


def test_saldo():
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=1, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 99
    ops.registrar(op)
    assert ops.caixa_atual == 98
    op = Operacao(horario=datetime.now(), quantidade=2, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 96


def test_saldo_venda():
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 101
    ops.registrar(op)
    assert ops.caixa_atual == 102
    op = Operacao(horario=datetime.now(), quantidade=-2, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 104


def test_valor_posicao():
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops._calcular_valor_pos(100) == 300

    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops._calcular_valor_pos(100) == -300


def test_valor_pos_comprado():
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 3


def test_pos_qtde():

    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 3

    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == -3

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 0


def test_win_rate():
    ops = Historico(ativo='PETR', pl_inicial=10000)

    # Teste lado comprado

    # Operação Comprada de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)

    assert ops.win_rate() == 1

    # Operação Comprada de 3 a R$12 para R$10.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=12)
    ops.registrar(op)

    # Não é para mudar, porque a operação ainda não se completou.
    assert ops.win_rate() == 1

    op = Operacao(horario=datetime.now(), quantidade=-3, preco=10)
    ops.registrar(op)

    assert ops.win_rate() == 0.5

    # Teste lado vendido

    # Operação Vendida de 3 a R$12 para R$10.
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)

    assert ops.win_rate() == 2/3

    # Operação Vendida de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=12)
    ops.registrar(op)

    assert ops.win_rate() == 2/4


def test_obter_df():
    ops = Historico(ativo='PETR', pl_inicial=10000)

    assert isinstance(ops.obter_df(), pd.DataFrame)
    assert len(ops.obter_df()) == 0

    # Operação Comprada de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)

    assert isinstance(ops.obter_df(), pd.DataFrame)


def test_preco_medio():
    ops = Historico(ativo='PETR', pl_inicial=10000)

    assert np.isnan(ops.preco_medio())

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    assert ops.preco_medio() == 10

    op = Operacao(horario=datetime.now(), quantidade=1, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 15

    op = Operacao(horario=datetime.now(), quantidade=2, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 70/4

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 70/4

    ops = Historico(ativo='PETR', pl_inicial=10000)

    assert np.isnan(ops.preco_medio())

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.preco_medio() == 10

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 15

    op = Operacao(horario=datetime.now(), quantidade=-2, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 70 / 4

    op = Operacao(horario=datetime.now(), quantidade=1, preco=20)
    ops.registrar(op)

    assert ops.preco_medio() == 70 / 4


def test_retorno_acumulado():
    ops = Historico(ativo='PETR', pl_inicial=100)

    assert ops.retorno_acumulado(10) == 0

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 101 / 100 - 1

    assert ops.retorno_acumulado(0) == 90 / 100 - 1

    # Aumentando posição
    op = Operacao(horario=datetime.now(), quantidade=2, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 103 / 100 - 1

    # Diminuindo posição
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 102 / 100 - 1

    # Diminuindo posição
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=11)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1

    # Zerando posição
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=9)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 100 / 100 - 1

    assert ops.obter_pos_atual() == 0

    # Abrindo posição vendida
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(9) == 101 / 100 - 1
    assert ops.retorno_acumulado(11) == 99 / 100 - 1

    # Aumentando posição
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(9) == 102 / 100 - 1

    # Diminuindo posição
    op = Operacao(horario=datetime.now(), quantidade=1, preco=9)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1

    # Diminuindo posição
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1


# Todo: Reformular comportamento... Não sei se está certo calcular os rendimentos por operação dessa maneira.
def test_retornos_por_operacao():
    ops = Historico(ativo='PETR', pl_inicial=100)

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=11)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=9)
    ops.registrar(op)

    assert ops.retornos_por_operacao()['rentabilidade'].round(9).tolist() == [0.1, -0.1]

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=11)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=9)
    ops.registrar(op)

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    assert ops.retornos_por_operacao()['rentabilidade'].round(9).tolist() == [0.1, -0.1, 0.1, -0.1]


def test_pos_atual():
    ops = Historico(ativo='PETR', pl_inicial=100)

    assert ops.pos_atual == Posicao.ZERADO

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.ZERADO

    # Inversão
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO

    op = Operacao(horario=datetime.now(), quantidade=4, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    # Inversão
    ops = Historico(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    op = Operacao(horario=datetime.now(), quantidade=-4, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO


def test_pl_atual():
    ops = Historico(ativo='PETR', pl_inicial=100)

    assert ops.pl_atual(preco_atual=100000000000) == 100

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    assert ops.pl_atual(preco_atual=10) == 100

    assert ops.pl_atual(preco_atual=11) == 101

    assert ops.pl_atual(preco_atual=9) == 99

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.pl_atual(preco_atual=10) == 100

    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.pl_atual(preco_atual=0) == 110
