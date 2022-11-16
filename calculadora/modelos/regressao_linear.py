import pandas as pd
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
from typing import List
from scipy.stats.stats import jarque_bera


def _obter_r2_ajustado(r2: float, n: int, n_variaveis_independentes: int):
    return 1 - (1 - r2) * (n - 1) / (n - n_variaveis_independentes - 1)


@dataclass()
class Regressao:
    x: List[pd.Series]
    coeficientes: List[float]
    modelo: LinearRegression
    r2: float
    r2_ajustado: float

    def prever(self, *xs: pd.Series) -> pd.Series:
        xs = pd.concat(xs, axis=1).dropna()
        predicoes = self.modelo.predict(xs.values)
        shape = predicoes.shape[0]
        return pd.Series(predicoes.reshape(shape), index=xs.index, name='predicao')

    def residuos(self, y: pd.Series) -> pd.Series:
        predicoes = self.prever(*self.x)
        df = pd.concat([y, predicoes], axis=1)
        # Residuo = Observado - previsto
        return df[df.columns[0]] - df[df.columns[1]]

    def teste_jarque_bera_residuos(self, y: pd.Series, alpha: float = 0.05) -> str:
        teste = jarque_bera(self.residuos(y).dropna())
        if teste.pvalue <= alpha:
            return f'Não é distribuição normal com {round((1 - alpha)*100, 2)}% de confiança.'
        return f'É distribuição normal com {round((1 - alpha)*100, 2)}% de confiança.'


def regressao_linear(y: pd.Series, *xs: pd.Series):
    """ Faz a regressão linear do modelo. """
    var_independentes = len(xs)

    xs_ = pd.concat(xs, axis=1)

    variaveis = pd.concat([xs_, y], axis=1).dropna().values
    y = variaveis[:, -1].reshape(-1, 1)
    xs_ = variaveis[:, :-1]
    regressao = LinearRegression()

    regressao.fit(X=xs_, y=y)
    r2 = regressao.score(X=xs_, y=y)

    return Regressao(x=[x for x in xs],
                     coeficientes=regressao.coef_.tolist(),
                     modelo=regressao,
                     r2=r2,
                     r2_ajustado=_obter_r2_ajustado(r2, y.shape[0], var_independentes))
