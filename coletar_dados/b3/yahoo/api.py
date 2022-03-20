from coletar_dados.b3.ativo import AtivoB3, Pregao
import pandas as pd
from yfinance import download
from coletar_dados.b3.yahoo.seletores import YahooIntervalo, YahooPeriodo, YahooTickers


class YahooRequisitor:

    def __init__(self, intervalo: YahooIntervalo, periodo: YahooPeriodo, ticker: YahooTickers):
        self.intervalo = intervalo.value
        self.periodo = periodo.value
        self.ticker = ticker.value

    def historico(self) -> pd.DataFrame:
        return download(self.ticker, period=self.periodo, interval=self.intervalo)


tradutor_col = {'close': 'fechamento',
                'adj close': 'fechamento_ajustado',
                'open': 'abertura',
                'adj open': 'abertura_ajustada',
                'low': 'minima',
                'adj low': 'minima_ajustada',
                'high': 'maxima',
                'adj high': 'maxima_ajustada',
                'volume': 'volume'}


class YahoooProcessador:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _minimizar_tamanho_letras_col(self):
        self.df.columns = [coluna.lower() for coluna in self.df.columns]

    def _traduzir_colunas(self):
        self.df.columns = [tradutor_col[coluna] for coluna in self.df.columns]

    def criar_dias_negociacao(self):

        self._minimizar_tamanho_letras_col()
        self._traduzir_colunas()

        negociacoes = self.df

        dias_negociacao = []
        for dia in negociacoes.index:
            negociacao = Pregao(horario=dia, **negociacoes.loc[dia].to_dict())
            dias_negociacao.append(negociacao)

        return dias_negociacao

    def criar_ativob3(self):
        ativob3 = AtivoB3()
        negociacoes = self.criar_dias_negociacao()
        for negociacao in negociacoes:
            ativob3.add_dia(negociacao)

        return ativob3


class YahooAPI:

    def __init__(self, intervalo: YahooIntervalo, periodo: YahooPeriodo, ticker: YahooTickers):
        self.requisitor = YahooRequisitor(intervalo, periodo, ticker)
        self.ticker = ticker

    def historico(self):
        yahoo_df = self.requisitor.historico()
        return YahoooProcessador(yahoo_df).criar_ativob3()


if __name__ == "__main__":
    PETR4 = YahooAPI(intervalo=YahooIntervalo.DIA_1, periodo=YahooPeriodo.DIA_5, ticker=YahooTickers.PETR4).historico()
