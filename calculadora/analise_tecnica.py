from dataclasses import dataclass
import pandas as pd


@dataclass
class MediaMovel:

    @classmethod
    def simples(cls, serie: pd.Series, window: int):
        return serie.rolling(window=window).mean()

    @classmethod
    def exponencial(cls, serie: pd.Series, window: int):
        alpha = 2/(window+1)
        return serie.ewm(alpha=alpha, adjust=False).mean()
