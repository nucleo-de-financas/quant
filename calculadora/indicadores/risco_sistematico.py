import numpy as np
import pandas as pd


class JanelaNegativa(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


def _validar_janela(valor: float | int):
    """ Verifica se a janela é positiva. """
    if not valor > 0:
        raise JanelaNegativa(f'Janela de {valor}. Porém, a janela não pode ser negativa.')


def _filtrar_df(df: pd.DataFrame):
    df = df.copy()
    # Limpando ativos completamente sem preços na série inteira.
    df = df.dropna(how='all')
    # Limpando qualquer dia em que tenho pelo menos um ativo sem dado.
    df = df.dropna(axis=1, how='any')
    return df


class Mahalanobis:

    def __init__(self, df_precos: pd.DataFrame):
        self._df = _filtrar_df(df_precos.pct_change())

    @property
    def _criar_matriz_de_cov_inv(self):
        cov = self._df.cov()
        cov_inversa = np.linalg.pinv(cov.values)
        return pd.DataFrame(cov_inversa)

    def _obter_distancia_de_mahalanobis(self, linha: pd.DataFrame, df: pd.DataFrame):

        # Vetor de médias
        medias = df.mean()

        # Centralizando cada coluna em torno da sua média histórica.
        linha_centralizada = (linha - medias)

        # Multiplicação matricial da linha centralizada com a matriz de covariância inversa.
        primeiro_termo = np.dot(linha_centralizada, self._criar_matriz_de_cov_inv)

        # # Multiplicação matricial da matriz de covariância inversa com a linha centralizada transposta.
        resultado = np.dot(primeiro_termo, linha_centralizada.transpose())

        # Coletando o resultado para aquela linha.
        return resultado.reshape(1)[0]

    @staticmethod
    def _gerar_inicio_nulo_serie(janela: int) -> list[np.nan]:
        return [np.nan] * (janela - 1)

    def _obter_janela(self, linha_atual: int, janela: int):
        return self._df.iloc[linha_atual - janela:linha_atual]

    def _obter_serie_mahalanobis(self, janela: int):
        serie = self._gerar_inicio_nulo_serie(janela=janela)
        for linha in range(janela, len(self._df) + 1):
            # Selecionando somente os dados correspondentes a janela.
            df_janela = self._obter_janela(linha_atual=linha, janela=janela)
            # Seleciona a última linha
            linha = self._df.iloc[linha - 1]
            serie.append(self._obter_distancia_de_mahalanobis(linha, df_janela))
        return pd.Series(serie, index=self._df.index)

    def obter_serie(self, janela: int = 252) -> pd.Series:
        """
        Usado em contextos que queremos saber como as interelações entre séries mudam. Por exemplo, se dois mercados
        costumam subir simultameanente e, de repente, deixam de fazer isso, esse indicador vai captar essa mudança
        de comportamento."""

        # Valida o valor da janela.
        _validar_janela(janela)

        # Caso em que todos serão nulos
        if len(self._df) < janela:
            serie = [np.nan] * len(self._df)
            return pd.Series(serie, index=self._df.index)

        return self._obter_serie_mahalanobis(janela=janela)

    def obter_series_dif(self, janela: int = 252) -> pd.Series:
        mahalanobis = self.obter_serie(janela)
        return mahalanobis - mahalanobis.shift(1)


class AbsortionRatio:

    def __init__(self, df: pd.DataFrame):
        self._df = df

    @staticmethod
    def _calcular_valor_de_eigen(df: pd.DataFrame, pct_relevante: float = 0.2):
        """ Calcula o Eigen value para a dataframe especificada. """
        cov_matrix = df.cov()
        eigen_values, eigen_vector = np.linalg.eig(cov_matrix)
        eigen_variancias = pd.Series(eigen_values).sort_values(ascending=False).reset_index(drop=True)
        return eigen_variancias[eigen_variancias.index <= pct_relevante * len(eigen_variancias)]

    def _calcular_abortion_ratio(self, df: pd.DataFrame,  pct_relevante: float = 0.2):
        eigen_value_soma = self._calcular_valor_de_eigen(df, pct_relevante).sum()
        variancia_total = df.var().sum()
        return eigen_value_soma / variancia_total

    def obter(self, janela: int = 252) -> pd.Series:
        """ Primeiramente, esse indicador identifica estatisticamente quais fatores são relevantes para explicar a
        variância de mercado e elenca os mais relevantes com base no parâmetro.

        A ideia, no entanto, segue em analisar o quão distribuída esta revelância está entre os fatores. Com isso,
        quanto mais concentrado a revelância em alguns fatores, maior é o risco sistemático, portanto, provalvemente
        alguma notícia (seja positiva ou negativa) será mais impactante para o mercado. Por outro lado, quanto mais
        distribuído for a relevância dos fatores, provável que menos impactante seja cada notícia. """
        # Valida o valor da janela.
        _validar_janela(janela)
        df_precos = _filtrar_df(self._df.pct_change())
        # Caso em que todos serão nulos
        if len(df_precos) < janela:
            serie = [np.nan] * len(df_precos)
            return pd.Series(serie, index=df_precos.index)
        # 'Abs ratios' serão guardadas aqui.
        abs_ratios = [np.nan] * (janela - 1)
        for linha in range(janela, len(df_precos)+1):
            # Selecionando somente os dados correspondentes a janela.
            df_janela = df_precos.iloc[linha-janela:linha]
            abs_ratio = self._calcular_abortion_ratio(df=df_janela, pct_relevante=0.2)
            abs_ratios.append(abs_ratio)
        return pd.Series(abs_ratios, index=df_precos.index)

    def obter_dif(self, janela: int = 252) -> pd.Series:
        abs_ratio = self.obter(janela)
        return abs_ratio - abs_ratio.shift(1)
