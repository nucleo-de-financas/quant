from api.coinmarketcap import Api, Moeda
from calculadora.indicadores.tendencia import MediaMovel
from fundo_quant.operacional import Ativo
from fundo_quant.estrategia import GoldenCrossLongOnly
from fundo_quant.executores import ExecutorLongOnly
from fundo_quant.backtest import WalkForward
import matplotlib.pyplot as plt


def fundo_cripto_v1(moeda: Moeda):
    # Coletando Dados
    dados = Api(moeda).obter()

    # Configurando ativo
    bitcoin = Ativo(saldo_inicial=10_000)

    # Configurando estratégia
    media_curta = MediaMovel.exponencial(dados['Fechamento'], window=7)
    media_longa = MediaMovel.exponencial(dados['Fechamento'], window=14)
    estrategia = GoldenCrossLongOnly(bitcoin, media_curta=media_curta, media_longa=media_longa)

    # Configurando executor
    ex = ExecutorLongOnly(bitcoin)

    # Rodando BackTest
    retorno = WalkForward(estrategia=estrategia, ex=ex, precos=dados['Fechamento']).obter_serie_retorno_teste()

    # Plotando resultado
    plt.plot(retorno)
    plt.show()
