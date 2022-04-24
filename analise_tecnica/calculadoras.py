import pandas as pd
import pandas_ta as ta
from coletar_dados.b3.ativo import AtivoB3
from enum import Enum
from dataclasses import dataclass
from typing import List
from coletar_dados.b3.yahoo.api import YahooAPI, YahooIntervalo, YahooTickers, YahooPeriodo


class SeletorMediaMovel(Enum):

    ARNAUD_LEGOUX = 'alma'
    DUPLA_EXPONENCIAL = 'dema'
    EXPONENCIAL = 'ema'
    FIBONACCI_PONDERADA = 'fwma'
    GAIN_HIGH_LOW = 'hilo'
    HIGH_LOW = 'hl2'
    HIGH_LOW_CLOSE = 'hlc3'
    HULL = 'hma'
    HOLT_WINTER = 'hwma'
    ICHIMOKU = 'ichimoku'
    JURIK = 'jma'
    KAUFMAN_ADAPTIVE = 'kama'
    LINEAR_REGRESSION = 'linreg'
    MC_GINLEY_DYNAMIC = 'mcgd'
    MIDPOINT = 'midpoint'
    MIDPRICE = 'midprice'
    OPEN_HIGH_CLOSE_LOW_AVERAGE = 'ohlc4'
    PASCAL_PONDERADA = 'pwma'
    WILDER = 'rma'
    SENO_MM = 'sinwma'
    SIMPLES = 'sma'
    EHLER_SMOOTH_FILTER = 'ssf'
    SUPERTREND = 'supertrend'
    SIMETRICAMENTE_PONDERADA = 'swma'
    T3 = 't3'
    TRIPLO_EXPONENCIAL = 'tema'
    MOVIMENTO_TRIANGULAR = 'trima'
    VARIABLE_INDEX_DYNAMIC = 'vidya'
    VWAP = 'vwap'
    FECHAMENTO_PONDERADA = 'wcp'
    PONDERADA = 'wma'
    ZERO_LAG = 'zlma'


@dataclass
class CalculadoraMediaMovel:
    """ Calcula oa indicadares. """

    ativo: AtivoB3
    media_movel: List[SeletorMediaMovel] | SeletorMediaMovel | None
    janela: int
    como_sinal: bool = True
    _dataframe: pd.DataFrame | None = None

    @staticmethod
    def _juntar_coluna_ao_df(coluna: pd.Series, df: pd.DataFrame):
        return pd.concat([coluna, df], axis=1)

    def _calcular_media_movel(self, media_movel: SeletorMediaMovel) -> pd.Series:
        if self._dataframe is None:
            self._dataframe = self.ativo.para_df()

        func = getattr(self._dataframe.ta, media_movel.value)
        serie_temporal = func(length=self.janela, close='fechamento', high='maxima', low='minima', open='abertura',
                              volume='volume')
        return serie_temporal

    def _calular_medias_moveis(self) -> List[pd.Series]:
        return [self._calcular_media_movel(media_movel) for media_movel in self.media_movel]

    def calcular(self) -> List[pd.Series] | pd.Series | None:
        if None:
            return None
        if not isinstance(self.media_movel, List):
            return self._calcular_media_movel(self.media_movel)
        return self._calular_medias_moveis()


if __name__ == "__main__":
    PETR4 = YahooAPI(YahooIntervalo.DIA_1, YahooPeriodo.ANO_1, YahooTickers.PETR4).historico()

    print(CalculadoraMediaMovel(ativo=PETR4,
                                media_movel=[seletor for seletor in SeletorMediaMovel], janela=10).calcular())
