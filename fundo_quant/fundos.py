from api.coinmarketcap import Api, Moeda
from calculadora.analise_tecnica import MediaMovel
from fundo_quant.operacional import AtivoComSaldo
from fundo_quant.estrategia import GoldenCrossLongOnly
from fundo_quant.executores import ExecutorLongOnly
from fundo_quant.backtest import WalkForward
import matplotlib.pyplot as plt


def fundo_cripto(moeda: Moeda):
    # Coletando Dados
    dados = Api(moeda).obter()
    bitcoin = AtivoComSaldo(saldo_inicial=10_000)
    ex = ExecutorLongOnly(bitcoin)
    media_curta = MediaMovel.exponencial(dados['Fechamento'], window=7)
    media_longa = MediaMovel.exponencial(dados['Fechamento'], window=14)
    estrategia = GoldenCrossLongOnly(bitcoin, media_curta=media_curta, media_longa=media_longa)
    retorno = WalkForward(estrategia=estrategia, ex=ex, precos=dados['Fechamento']).obter_serie_retorno()
    plt.plot(retorno)
    plt.show()
