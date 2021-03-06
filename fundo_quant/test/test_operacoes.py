import numpy as np
import pandas as pd

from fundo_quant.operacional import Operacoes, Operacao, Posicao
from datetime import datetime


def test_registro_multiplo():
    ops = Operacoes(ativo='PETR', pl_inicial=100)
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
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=1, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 99
    ops.registrar(op)
    assert ops.caixa_atual == 98
    op = Operacao(horario=datetime.now(), quantidade=2, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 96


def test_saldo_venda():
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 101
    ops.registrar(op)
    assert ops.caixa_atual == 102
    op = Operacao(horario=datetime.now(), quantidade=-2, preco=1)
    ops.registrar(op)
    assert ops.caixa_atual == 104


def test_valor_posicao():
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops._calcular_valor_pos(100) == 300

    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops._calcular_valor_pos(100) == -300


def test_valor_pos_comprado():
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 3


def test_pos_qtde():

    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 3

    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == -3

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.obter_pos_atual() == 0


def test_win_rate():
    ops = Operacoes(ativo='PETR', pl_inicial=10000)

    # Teste lado comprado

    # Opera????o Comprada de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)

    assert ops.win_rate() == 1

    # Opera????o Comprada de 3 a R$12 para R$10.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=12)
    ops.registrar(op)

    # N??o ?? para mudar, porque a opera????o ainda n??o se completou.
    assert ops.win_rate() == 1

    op = Operacao(horario=datetime.now(), quantidade=-3, preco=10)
    ops.registrar(op)

    assert ops.win_rate() == 0.5

    # Teste lado vendido

    # Opera????o Vendida de 3 a R$12 para R$10.
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)

    assert ops.win_rate() == 2/3

    # Opera????o Vendida de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=12)
    ops.registrar(op)

    assert ops.win_rate() == 2/4


def test_obter_df():
    ops = Operacoes(ativo='PETR', pl_inicial=10000)

    assert isinstance(ops.obter_df(), pd.DataFrame)
    assert len(ops.obter_df()) == 0

    # Opera????o Comprada de 3 a R$10 para R$12.
    op = Operacao(horario=datetime.now(), quantidade=3, preco=10)
    ops.registrar(op)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=12)
    ops.registrar(op)

    assert isinstance(ops.obter_df(), pd.DataFrame)


def test_preco_medio():
    ops = Operacoes(ativo='PETR', pl_inicial=10000)

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

    ops = Operacoes(ativo='PETR', pl_inicial=10000)

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
    ops = Operacoes(ativo='PETR', pl_inicial=100)

    assert ops.retorno_acumulado(10) == 0

    op = Operacao(horario=datetime.now(), quantidade=1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 101 / 100 - 1

    assert ops.retorno_acumulado(0) == 90 / 100 - 1

    # Aumentando posi????o
    op = Operacao(horario=datetime.now(), quantidade=2, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 103 / 100 - 1

    # Diminuindo posi????o
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(11) == 102 / 100 - 1

    # Diminuindo posi????o
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=11)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1

    # Zerando posi????o
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=9)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 100 / 100 - 1

    assert ops.obter_pos_atual() == 0

    # Abrindo posi????o vendida
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(9) == 101 / 100 - 1
    assert ops.retorno_acumulado(11) == 99 / 100 - 1

    # Aumentando posi????o
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(9) == 102 / 100 - 1

    # Diminuindo posi????o
    op = Operacao(horario=datetime.now(), quantidade=1, preco=9)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1

    # Diminuindo posi????o
    op = Operacao(horario=datetime.now(), quantidade=-1, preco=10)
    ops.registrar(op)

    assert ops.retorno_acumulado(10) == 101 / 100 - 1


# Todo: Reformular comportamento... N??o sei se est?? certo calcular os rendimentos por opera????o dessa maneira.
def test_retornos_por_operacao():
    ops = Operacoes(ativo='PETR', pl_inicial=100)

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
    ops = Operacoes(ativo='PETR', pl_inicial=100)

    assert ops.pos_atual == Posicao.ZERADO

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO

    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.ZERADO

    # Invers??o
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=-3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO

    op = Operacao(horario=datetime.now(), quantidade=4, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    # Invers??o
    ops = Operacoes(ativo='PETR', pl_inicial=100)
    op = Operacao(horario=datetime.now(), quantidade=3, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.COMPRADO

    op = Operacao(horario=datetime.now(), quantidade=-4, preco=1)
    ops.registrar(op)
    assert ops.pos_atual == Posicao.VENDIDO


def test_pl_atual():
    ops = Operacoes(ativo='PETR', pl_inicial=100)

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
