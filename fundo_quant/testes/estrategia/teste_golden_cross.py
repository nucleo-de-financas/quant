import pandas as pd
from fundo_quant.estrategia import GoldenCrossLongOnly
from fundo_quant.operacional import Ativo, Ordem
from datetime import datetime

media_curta = [2, 1, 3]
media_longa = [1, 2, 4]
dias = [datetime(2022, 1, 1), datetime(2022, 1, 2), datetime(2022, 1, 3)]
media_curta = pd.Series(media_curta, index=dias)
media_longa = pd.Series(media_longa, index=dias)


def teste_sinal_compra():
    ativo = Ativo(100)
    es = GoldenCrossLongOnly(ativo=ativo, media_curta=media_curta, media_longa=media_longa)
    assert es.obter_ordem() == Ordem.COMPRAR


def teste_sinal_venda_a_descoberta():
    ativo = Ativo(100)
    es = GoldenCrossLongOnly(ativo=ativo, media_curta=media_curta, media_longa=media_longa)
    es.setar_dia(1)
    assert es.obter_ordem() is None


def teste_sinal_depois_de_uma_compra():
    ativo = Ativo(100)
    es = GoldenCrossLongOnly(ativo=ativo, media_curta=media_curta, media_longa=media_longa)
    ativo.comprar(preco=10, quantidade=10, horario=dias[0])
    es.setar_dia(1)
    assert es.obter_ordem() == Ordem.VENDER
