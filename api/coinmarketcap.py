from cryptocmd import CmcScraper
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Moeda(Enum):
    AVALANCHE = 'AVAX'
    BITCOIN = 'BTC'
    CARDANO = 'ADA'
    DOGECOIN = 'DOGE'
    DAI = 'DAI'
    ETHEREUM = 'ETH'
    TETHER = 'USDT'
    SOLANA = 'SOL'


@dataclass
class Api:
    moeda: Moeda
    inicio: datetime | str | None = None
    fim: datetime | str | None = None

    def __post_init__(self):
        self._scraper = CmcScraper(self.moeda.value, self.inicio, self.fim)

    def obter(self) -> pd.DataFrame:
        df = self._scraper.get_dataframe()
        df.columns = ['Data', 'Abertura', 'Maxima', 'Minima', 'Fechamento', 'Volume', 'MarketCap']
        df.set_index('Data', inplace=True)
        return df
