from fundo_quant.estrategia import GoldenCrossVenda, GoldenCrossCompra
from fundo_quant.gerenciamento_risco import StopGainBasico, StopLossBasico
from fundo_quant.bots import *
from api.yahoo import HistoricoApi, Tickers


if __name__ == "__main__":
    # Coletando Dados
    dados = HistoricoApi(Tickers.PETR4).obter(frequencia='1d', quanto_tempo='1y')
    fechamento = dados['Fechamento']
    fechamento.name = Tickers.PETR4.name
    compra = GoldenCrossCompra(fechamento=fechamento, janela_curta=15, janela_longa=30)
    venda = GoldenCrossVenda(fechamento=fechamento, janela_curta=15, janela_longa=30)
    stop_loss = StopLossBasico()
    stop_gain = StopGainBasico()

    op, ret = TrendFollowingBot(compra, venda, stop_loss, stop_gain).track_um_ativo(timeseries=fechamento, pl_inicial=100)
    print(op.obter_df())
    import matplotlib.pyplot as plt
    plt.plot(ret)
    plt.show()
    plt.plot(op.retornos_por_operacao().rentabilidade)
    plt.show()
    print(op)
