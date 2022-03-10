from coletar_dados.yahoo.historical_data import Api, Intervalo, Periodo, Tickers, AtivoB3


class MediaMovel:

    def __init__(self, serie: AtivoB3, janela: int):
        self.df = serie.get()
        self.janela = janela

    def simples(self):
        close = self.df.columns[0]
        return self.df.ta.sma(length=self.janela, close=close)

    def exponencial(self):
        close = self.df.columns[0]
        return self.df.ta.ema(length=self.janela, close=close)

    def ponderada(self):
        close = self.df.columns[0]
        return self.df.ta.wma(length=self.janela, close=close)

    def hull(self):
        close = self.df.columns[0]
        return self.df.ta.hma(length=self.janela, close=close)

    def duplo_exponencial(self):
        close = self.df.columns[0]
        return self.df.ta.dema(length=self.janela, close=close)

    def t3(self):
        close = self.df.columns[0]
        return self.df.ta.t3(length=self.janela, close=close)

    def triplo_exponencial(self):
        close = self.df.columns[0]
        return self.df.ta.tema(length=self.janela, close=close)

    def vwap(self):
        close = self.df.columns[0]
        df = self.df.copy()
        df.index = pd.to_datetime(df.index)
        return df.ta.vwap(length=self.janela, close=close)

    def zero_lag(self):
        close = self.df.columns[0]
        return self.df.ta.zlma(length=self.janela, close=close)

    def kaufman_adaptive(self):
        close = self.df.columns[0]
        return self.df.ta.kama(length=self.janela, close=close)


class Volatilidade:
    def __init__(self, serie: AtivoB3):
        self.df = serie.get()

    def bandas_de_bollinger(self, janela: int, dp: float):
        """Output: (1) Banda inferior, (2) Média móvel, (3) Banda Superior"""
        close = self.df.columns[0]
        columns = self.df.columns[:3]
        return self.df.ta.bbands(length=janela, std=dp, close=close)[columns]

    def band_width(self, janela: int, dp: float):
        """Output: (1) Largura da Banda """
        close = self.df.columns[0]
        columns = self.df.columns[3]
        return self.df.ta.bbands(length=janela, std=dp, close=close)[columns]

    def band_percentage(self, janela: int, dp: float):
        """Retorna a Band Percentage"""
        close = self.df.columns[0]
        columns = self.df.columns[4]
        return self.df.ta.bbands(length=janela, std=dp, close=close)[columns]

    def average_true_range(self, janela: int):
        """Retorna uma série de ATR"""
        close = self.df.columns[0]
        return self.df.ta.atr(length=janela, close=close)



PETR4 = Api(intervalo=Intervalo.DIA_1, periodo=Periodo.ANO_5, ticker=Tickers.PETR4).historico()
x = MediaMovel(PETR4).adx()
print(x)
