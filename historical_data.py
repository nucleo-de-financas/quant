import pandas_ta as pd
from yfinance import download
from enum import Enum
from typing import List


class Periodo(Enum):
    DIA_1 = '1d'
    DIA_5 = '5d'
    MES_1 = '1mo'
    MES_3 = '3mo'
    MES_6 = '6mo'
    ANO_1 = '1y'
    ANO_2 = '2y'
    ANO_5 = '5y'
    ANO_10 = '10y'
    ANO_ATUAL = 'ytd'
    YTD = 'ytd'
    MAX = 'max'


class Intervalo(Enum):
    """ Determina os períodos possíveis para a API"""
    MIN_1 = '1m'
    MIN_2 = '2m'
    MIN_5 = '5m'
    MIN_15 = '15m'
    MIN_30 = '30m'
    MIN_60 = '60m'
    MIN_90 = '90m'
    HORA_1 = '1h'
    DIA_1 = '1d'
    DIA_5 = '5d'
    SEMANA_1 = '1wk'
    MES_1 = '1mo'
    MES_3 = '3mo'


class Tickers(Enum):
    PETR3 = 'PETR4' + '.SA'
    PETR4 = 'PETR4' + '.SA'


class Requisitor:

    def __init__(self, intervalo: Intervalo, periodo: Periodo, ticker: Tickers):
        self.intervalo = intervalo.value
        self.periodo = periodo.value
        self.ticker = ticker.value

    def historico(self) -> pd.DataFrame:
        return download(self.ticker, period=self.periodo, interval=self.intervalo)


class AtivoB3:
    """Pandas Dataframe padronizado para return."""
    def __init__(self, datas: List, adj_close: List, open_: List, high: List, low: List):
        self._tabela = pd.DataFrame(index=datas)
        self._tabela['adj close'] = adj_close
        self._tabela['open'] = open_
        self._tabela['high'] = high
        self._tabela['low'] = low

    def get(self):
        return self._tabela

    def print(self):
        return print(self._tabela)


class Tratamento:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def obter(self) -> AtivoB3:

        index = self.df.index.tolist()

        self.df.columns = [column.lower() for column in self.df.columns]

        close = self.df['adj close'].tolist()
        open_ = self.df['open'].tolist()
        high = self.df['low'].tolist()
        low = self.df['high'].tolist()

        historico = AtivoB3(datas=index,
                            adj_close=close,
                            open_=open_,
                            high=high,
                            low=low)

        return historico


class Api:

    def __init__(self, intervalo: Intervalo, periodo: Periodo, ticker: Tickers):
        self.requisitor = Requisitor(intervalo, periodo, ticker).historico()
        self.ticker = ticker

    def historico(self):
        return Tratamento(self.requisitor).obter()


if __name__ == "__main__":
    PETR4 = Api(Intervalo.DIA_1, periodo=Periodo.DIA_5, ticker=Tickers.PETR4).historico()
    PETR4.print()
