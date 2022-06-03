import datetime

import pytest

from fundo_quant.operacional import Operacao, TipoOperacao, InconsistenciaNaOperacaoError

import random


def test_compra():
    x = Operacao(horario=datetime.datetime.now(), quantidade=1, preco=1)
    assert x.tipo == TipoOperacao.COMPRA


def test_venda():
    x = Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=1)
    assert x.tipo == TipoOperacao.VENDA


def test_valor_financeiro():
    for i in range(1000):
        qtde = random.randint(1, 20)
        lista = [-1, 1]
        random.shuffle(lista)
        preco = random.random()
        x = Operacao(horario=datetime.datetime.now(), quantidade=lista[-1] * qtde, preco=preco)
        print(x)
        assert x.valor_financeiro() == lista[-1] * qtde * preco


def test_restricoes_operacoes():
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=datetime.datetime.now(), preco=2, quantidade=0)
        assert exc == InconsistenciaNaOperacaoError

    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        preco = -2
        Operacao(horario=datetime.datetime.now(), preco=2, quantidade=0)
        assert exc == InconsistenciaNaOperacaoError


def test_atributos():
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=1, preco=2.2, quantidade=-1)
        assert exc == InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=1, preco=2.2, quantidade=-1)
        assert exc == InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=datetime.datetime.now(), preco='2.2', quantidade=-1)
        assert exc == InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=datetime.datetime.now(), preco=2, quantidade='1')
        assert exc == InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")
    with pytest.raises(InconsistenciaNaOperacaoError) as exc:
        Operacao(horario=datetime.datetime.now(), preco=2, quantidade=1.1)
        assert exc == InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")

    Operacao(horario=datetime.datetime.now(), preco=2, quantidade=1)
