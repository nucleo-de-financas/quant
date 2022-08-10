import pandas as pd
from scipy.stats import norm


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
    serie_reescalada = 100 * norm.cdf(0.25 * serie/(f75-f25)) - 50
    return pd.Series(serie_reescalada, index=serie.index)


def normalizar(serie: pd.Series) -> pd.Series:
    f25 = serie.quantile(0.25)
    f50 = serie.quantile(0.5)
    f75 = serie.quantile(0.75)
    serie_normalizada = 100 * norm.cdf(0.5 * (serie - f50) / (f75 - f25)) - 50
    return pd.Series(serie_normalizada, index=serie.index)


# Todo: Mudar o output para pd.Series.
def clump60(serie: pd.Series) -> pd.Series:
    """ A mediana indica que pelo menos 50% dos valores estão acima daquele valor.
    Em finanças, a mediana é interpretada como uma medida de consenso.

    No entanto, uma mediana positiva não quer dizer que há um consenso positivo,
    necessariamente.
    Imagine um empate de 50% acima de valor positivo e 50% abaixo de 0. Neste caso,
    haveria um empate, indicando mais uma dúvida do que um consenso.

    O método CLUMP surgiu para filtrar os casos em que a mediana não seria consenso,
    criando uma área em que, caso haja empates, seja retornado zero.  """
    if serie.quantile(0.40) > 0:
        return serie.quantile(0.4)
    elif serie.quantile(0.6) < 0:
        return serie.quantile(0.6)
    return 0
