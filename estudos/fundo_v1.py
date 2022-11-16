from api.coinmarketcap import Api, Moeda
from calculadora.indicadores.tendencia import MediaMovel
from fundo_quant.operacional import Ativo
from fundo_quant.estrategia import GoldenCrossLongOnly
from fundo_quant.executores import ExecutorLongOnly
from fundo_quant.backtest import WalkForward
from dataclasses import dataclass
import pandas as pd


@dataclass()
class GoldenCrossResults:
    janela_curta: int
    janela_longa: int
    retornos: pd.Series


def gerar_parametros_a_testar(limites_curta: tuple[int, int], limites_longa: tuple[int, int]):
    combinacoes = []
    for curta in range(limites_curta[0], limites_curta[1]):
        for longa in range(limites_longa[0], limites_longa[1]):
            if longa <= curta:
                continue
            combinacoes.append((curta, longa))
    return combinacoes


def obter_parametros_otimos(moeda: Moeda):

    # Coletando Dados
    dados = Api(moeda).obter()

    parametros = gerar_parametros_a_testar((10, 30), (30, 120))

    # Configurando estratégia
    resultados = []
    for janela_curta, janela_longa in parametros:
        # Configurando ativo
        bitcoin = Ativo(saldo_inicial=10_000)
        media_curta = MediaMovel.exponencial(dados['Fechamento'], window=janela_curta)
        media_longa = MediaMovel.exponencial(dados['Fechamento'], window=janela_longa)
        estrategia = GoldenCrossLongOnly(bitcoin, media_curta=media_curta, media_longa=media_longa)

        # Configurando executor
        ex = ExecutorLongOnly(bitcoin)

        # Rodando BackTest
        backtest = WalkForward(estrategia=estrategia, ex=ex, precos=dados['Fechamento'], atraso=1)
        retorno = backtest.obter_serie_retorno_teste()
        resultados.append(GoldenCrossResults(retornos=retorno,
                                             janela_curta=janela_curta,
                                             janela_longa=janela_longa))

    return resultados
