from fundo_quant.estrategia import GoldenCrossVenda, GoldenCrossCompra
from fundo_quant.stops import StopGainBasico, StopLossBasico
from fundo_quant.bots import *
from api.yahoo import HistoricoApi, Tickers


def fundo_v0():
    # Coletando Dados
    dados = HistoricoApi(Tickers.PETR4).obter(frequencia='1d', quanto_tempo='1y')
    fechamento = dados['Fechamento']
    fechamento.name = Tickers.PETR4.name
    compra = GoldenCrossCompra(fechamento=fechamento, janela_curta=15, janela_longa=30)
    venda = GoldenCrossVenda(fechamento=fechamento, janela_curta=15, janela_longa=30)
    stop_loss = StopLossBasico()
    stop_gain = StopGainBasico()

    bot = TrendFollowingBot(compra, venda, stop_loss, stop_gain)
    op, ret = bot.track_um_ativo(timeseries=fechamento, pl_inicial=100)
    return op, ret


if __name__ == "__main__":
    operacoes, retorno = fundo_v0()
