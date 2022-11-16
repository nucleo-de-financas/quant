import pandas as pd
from yfinance import download
from enum import Enum
from dataclasses import dataclass


class Tickers(Enum):
    ABEV3 = 'ABEV3' + '.SA'
    AZUL4 = 'AZUL4' + '.SA'
    B3SA3 = 'B3SA3' + '.SA'
    BBAS3 = 'BBAS3' + '.SA'
    BBDC3 = 'BBDC3' + '.SA'
    BBDC4 = 'BBDC4' + '.SA'
    BBSE3 = 'BBSE3' + '.SA'
    BEEF3 = 'BEEF3' + '.SA'
    BPAC11 = 'BPAC11' + '.SA'
    BRAP4 = 'BRAP4' + '.SA'
    BRDT3 = 'BRDT3' + '.SA'
    BRFS3 = 'BRFS3' + '.SA'
    BRML3 = 'BRML3' + '.SA'
    BTOW3 = 'BTOW3' + '.SA'
    CCRO3 = 'CCRO3' + '.SA'
    CIEL3 = 'CIEL3' + '.SA'
    CMIG4 = 'CMIG4' + '.SA'
    COGN3 = 'COGN3' + '.SA'
    CPFE3 = 'CPFE3' + '.SA'
    CRFB3 = 'CRFB3' + '.SA'
    CSAN3 = 'CSAN3' + '.SA'
    CSNA3 = 'CSNA3' + '.SA'
    CVCB3 = 'CVCB3' + '.SA'
    CYRE3 = 'CYRE3' + '.SA'
    ECOR3 = 'ECOR3' + '.SA'
    EGIE3 = 'EGIE3' + '.SA'
    ELET3 = 'ELET3' + '.SA'
    ELET6 = 'ELET6' + '.SA'
    EMBR3 = 'EMBR3' + '.SA'
    ENBR3 = 'ENBR3' + '.SA'
    ENGI11 = 'ENGI11' + '.SA'
    EQTL3 = 'EQTL3' + '.SA'
    EZTC3 = 'EZTC3' + '.SA'
    FLRY3 = 'FLRY3' + '.SA'
    GGBR4 = 'GGBR4' + '.SA'
    GNDI3 = 'GNDI3' + '.SA'
    GOAU4 = 'GOAU4' + '.SA'
    GOLL4 = 'GOLL4' + '.SA'
    HAPV3 = 'HAPV3' + '.SA'
    HGTX3 = 'HGTX3' + '.SA'
    HYPE3 = 'HYPE3' + '.SA'
    IGTA3 = 'IGTA3' + '.SA'
    IRBR3 = 'IRBR3' + '.SA'
    ITSA4 = 'ITSA4' + '.SA'
    ITUB4 = 'ITUB4' + '.SA'
    JBSS3 = 'JBSS3' + '.SA'
    KLBN11 = 'KLBN11' + '.SA'
    LAME4 = 'LAME4' + '.SA'
    LREN3 = 'LREN3' + '.SA'
    MGLU3 = 'MGLU3' + '.SA'
    MRFG3 = 'MRFG3' + '.SA'
    MRVE3 = 'MRVE3' + '.SA'
    MULT3 = 'MULT3' + '.SA'
    NTCO3 = 'NTCO3' + '.SA'
    PCAR3 = 'PCAR3' + '.SA'
    PETR3 = 'PETR3' + '.SA'
    PETR4 = 'PETR4' + '.SA'
    PRIO3 = 'PRIO3' + '.SA'
    QUAL3 = 'QUAL3' + '.SA'
    RADL3 = 'RADL3' + '.SA'
    RAIL3 = 'RAIL3' + '.SA'
    RENT3 = 'RENT3' + '.SA'
    SANB11 = 'SANB11' + '.SA'
    SBSP3 = 'SBSP3' + '.SA'
    SULA11 = 'SULA11' + '.SA'
    SUZB3 = 'SUZB3' + '.SA'
    TAEE11 = 'TAEE11' + '.SA'
    TIMS3 = 'TIMS3' + '.SA'
    TOTS3 = 'TOTS3' + '.SA'
    USIM5 = 'USIM5' + '.SA'
    VALE3 = 'VALE3' + '.SA'
    VIVT4 = 'VIVT4' + '.SA'
    VVAR3 = 'VVAR3' + '.SA'
    WEGE3 = 'WEGE3' + '.SA'
    YDUQ3 = 'YDUQ3' + '.SA'


@dataclass
class HistoricoApi:

    ticker: Tickers

    def __post_init__(self):
        self.ticker = self.ticker

    def obter(self, frequencia, quanto_tempo) -> pd.DataFrame:
        df = download(self.ticker.value, period=quanto_tempo, interval=frequencia)
        df.columns = ['Abertura', 'Maxima', 'Minima', 'Fechamento', 'Fechamento Ajustado', 'Volume']
        df.index.name = 'Data'
        return df


if __name__ == "__main__":
    x = HistoricoApi(Tickers.PETR3).obter(frequencia='1d', quanto_tempo='1m')
    print(x)

