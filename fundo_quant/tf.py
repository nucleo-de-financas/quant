from dataclasses import dataclass
import pandas as pd
from fundo_quant.TradingBot import EstrategiaCompra, EstrategiaVenda, Sinalizacao, Posicao, TrendFollowingBot
from api.yahoo import HistoricoApi, Tickers
from calculadora.analise_tecnica import MediaMovel





@dataclass
class GoldenCrossCompra(EstrategiaCompra):

    fechamento: pd.Series
    janela_curta: int
    janela_longa: int

    _dias_correntes: int = 1

    def deve_comprar(self, posicao: Posicao) -> Sinalizacao:
        media_curta = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_curta)
        media_longa = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_longa)

        if media_curta.iloc[-1] > media_longa.iloc[-1] and posicao == Posicao.ZERADO:
            return Sinalizacao.COMPRAR
        return Sinalizacao.MANTER

    def avancar_dia(self):
        self._dias_correntes += 1


@dataclass
class GoldenCrossVenda(EstrategiaVenda):
    fechamento: pd.Series
    janela_curta: int
    janela_longa: int

    _dias_correntes: int = 1

    def deve_vender(self, posicao: Posicao) -> Sinalizacao:
        media_curta = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_curta)
        media_longa = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_longa)

        if media_curta.iloc[-1] < media_longa.iloc[-1] and posicao == Posicao.COMPRADO:
            return Sinalizacao.VENDER
        return Sinalizacao.MANTER

    def avancar_dia(self):
        self._dias_correntes += 1


if __name__ == "__main__":
    # Coletando Dados
    dados = HistoricoApi(Tickers.PETR4).obter(frequencia='1d', quanto_tempo='1y')
    x = dados['Fechamento']
    compra = GoldenCrossCompra(fechamento=dados['Fechamento'], janela_curta=15, janela_longa=30)
    venda = GoldenCrossVenda(fechamento=dados['Fechamento'], janela_curta=15, janela_longa=30)

    backtest = TrendFollowingBot(compra, venda).track_um_ativo(timeseries=dados['Fechamento'], pl_inicial=100)
