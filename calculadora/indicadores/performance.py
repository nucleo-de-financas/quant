import pandas as pd
import numpy as np


def drawdown(janela: int, serie: pd.Series):
    maximo_movel = serie.rolling(janela).max()
    return serie / maximo_movel - 1


def indice_de_sharpe_movel(r_livre_risco: pd.Series,
                           r_ativo: pd.Series,
                           janela: int):
    excesso_retorno = r_ativo - r_livre_risco
    rolling = excesso_retorno.rolling(window=janela)
    return np.sqrt(janela) * rolling.mean() / rolling.std()


def indice_de_treynor():
    pass


def indice_var():
    pass


def alfa_de_jensen():
    pass


def indice_black_treynor():
    pass


def information_ratio():
    pass


def indice_de_modigliani():
    pass


def indice_de_sortino():
    pass
