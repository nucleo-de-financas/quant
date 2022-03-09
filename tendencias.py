from coletar_dados.yahoo.historical_data import Api, Intervalo, Periodo, Tickers, AtivoB3


class MediaMovel:

    def __init__(self, serie: AtivoB3):
        self.df = serie.get()

    def simples(self, length: int = 10):
        close = self.df.columns[0]
        return self.df.ta.sma(lengh=length, close=close)

    def exponencial(self, length: int = 10):
        close = self.df.columns[0]
        return self.df.ta.ema(lengh=length, close=close)

    def ponderada(self, length: int = 10):
        close = self.df.columns[0]
        return self.df.ta.wma(lengh=length, close=close)

    def adx(self, length: int = 10):
        close = self.df.columns[0]
        return self.df.ta.adx(lengh=length, close=close)



PETR4 = Api(intervalo=Intervalo.DIA_1, periodo=Periodo.ANO_5, ticker=Tickers.PETR4).historico()
x = MediaMovel(PETR4).adx()
print(x)
