import pandas as pd
import scipy


def centralizar(serie: pd.Series, numero: int) -> pd.Series:
    """ Subtrai a mediana móvel de n períodos da série para centralizá-la.
        Como analogia, insere uma espécie de força gravitacional em torno do número 0,
        adicinando uma força em prol da estacionariedade da série.

        Observação: pode destruir potencialmente informações valiosas como o
        sinal da variável e a magnitude."""
    return serie - serie.rolling(numero).median()


def reescalar(serie: pd.Series) -> pd.Series:
    f25 = serie.quantile(0.25)
    f75 = serie.quantile(0.75)
    serie_reescalada = 100 * scipy.stats.norm.cdf(0.25 * serie/(f75-f25)) - 50
    return pd.Series(serie_reescalada, index=serie.index)


def normalizar(serie: pd.Series) -> pd.Series:
    f25 = serie.quantile(0.25)
    f50 = serie.quantile(0.5)
    f75 = serie.quantile(0.75)
    serie_normalizada = 100 * scipy.stats.norm.cdf(0.5 * (serie - f50) / (f75 - f25)) - 50
    return pd.Series(serie_normalizada, index=serie.index)
