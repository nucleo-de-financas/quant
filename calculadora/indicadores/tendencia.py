from dataclasses import dataclass
import pandas as pd
import numpy as np
from dados.preprocessamento import normalizar, reescalar


class JanelaNegativa(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


@dataclass
class MediaMovel:

    @classmethod
    def simples(cls, serie: pd.Series, window: int):
        return serie.rolling(window=window).mean()

    @classmethod
    def exponencial(cls, serie: pd.Series, window: int):
        alpha = 2/(window+1)
        return serie.ewm(alpha=alpha, adjust=False).mean()


@dataclass()
class IndiceForcaRelativa:
    serie: pd.Series

    def _media_simples_subidas(self, janela: int):
        subidas = self.serie.mask(self.serie > 0, 0)
        return subidas.rolling(janela).mean()

    def _media_exp_subidas(self, janela: int):
        subidas = self.serie.mask(self.serie > 0, 0)
        return subidas.ewm(alpha=2 / (1 + janela)).mean()

    def _media_simples_quedas(self, janela: int):
        quedas = self.serie.mask(self.serie < 0, 0)
        return quedas.rolling(janela).mean()

    def _media_exp_quedas(self, janela: int):
        quedas = self.serie.mask(self.serie < 0, 0)
        return quedas.ewm(alpha=2 / (1 + janela)).mean()

    def simples(self, janela: int) -> pd.Series:
        """ Precisa receber os valores em porcentagem. """
        if janela <= 0:
            raise ValueError('Janela não pode ser menor ou igual a zero.')
        forca_relativa = self._media_simples_subidas(janela) / -self._media_simples_quedas(janela)
        indice = 100 - 100 / (1 + forca_relativa)
        indice.columns = ['IFR']
        return indice['IFR']

    def exp(self, janela: int):
        """ Precisa receber os valores em porcentagem. """
        if janela <= 0:
            raise ValueError('Janela não pode ser menor ou igual a zero.')
        forca_relativa = self._media_exp_subidas(janela) / -self._media_exp_quedas(janela)
        indice = 100 - 100 / (1 + forca_relativa)
        indice.columns = ['IFR']
        return indice['IFR']


def atr(maxima: pd.Series, minima: pd.Series, fechamento: pd.Series, janela: int):
    fechamento_anterior = fechamento.shift()

    maxima_para_minima = maxima - minima
    maxima_para_fechamento = np.abs(maxima - fechamento_anterior)
    minima_para_fechamento = np.abs(minima - fechamento_anterior)
    amplitudes = pd.concat([maxima_para_minima, maxima_para_fechamento, minima_para_fechamento], axis=1)
    amplitude_verdadeira = amplitudes.max(axis=1)

    return amplitude_verdadeira.rolling(janela).sum() / janela


@dataclass()
class DiferencaEntreMedias:

    maxima: pd.Series
    minima: pd.Series
    fechamento: pd.Series

    def calcular(self,
                 media_curta: pd.Series,
                 media_longa: pd.Series,
                 janela_curta: int,
                 janela_longa: int):
        media_longa = media_longa.shift(-janela_curta)
        dif = media_curta - media_longa
        atr_ = atr(self.maxima, self.minima, self.fechamento, janela=janela_longa + janela_curta)
        atr_series = dif.values.reshape(len(media_curta)) / atr_.values
        atr_series = pd.Series(atr_series, index=self.fechamento.index)
        return normalizar(atr_series)


class Preco:

    def __init__(self,
                 maxima: pd.Series,
                 minima: pd.Series,
                 fechamento: pd.Series,
                 abertura: pd.Series,
                 janela: int,
                 atr_janela: int):
        self.maxima = maxima
        self.minima = minima
        self.fechamento = fechamento
        self.abertura = abertura
        self._validar_janela(janela)
        self.janela = janela
        self.atr_janela = atr_janela

    @staticmethod
    def _validar_janela(valor: float | int):
        """ Verifica se a janela é positiva. """
        if not valor > 0:
            raise JanelaNegativa(f'Janela de {valor}. Porém, '
                                 f'a janela não pode ser negativa.')

    @staticmethod
    def _obter_coef_lagrange(ordem: int, precos: pd.Series):

        # Criar a series
        x = list(range(len(precos)))
        y = precos.tolist()

        polinomio = np.polynomial.legendre.legfit(x, y, deg=ordem)
        return polinomio[ordem - 1]

    def _obter_serie_coeficientes(self, ordem: int):
        self._validar_janela(self.janela)

        df = pd.concat([self.maxima, self.minima, self.abertura, self.fechamento], axis=1)
        log_da_media = np.log(df.mean(axis=1))
        log_da_media = log_da_media.dropna()

        # Caso em que todos serão nulos
        if len(log_da_media) < self.janela:
            serie = [np.nan] * len(log_da_media)
            return pd.Series(serie, index=log_da_media.index)

        # Distâncias serão guardadas aqui.
        coeficientes = [np.nan] * (self.janela - 1)

        for linha in range(self.janela, len(log_da_media) + 1):
            # Selecionando somente os dados correspondentes a janela.
            log_da_media_janela = log_da_media.iloc[linha - self.janela:linha]

            # Calcular o coeficiente
            coeficiente = self._obter_coef_lagrange(precos=log_da_media_janela, ordem=ordem)
            coeficientes.append(coeficiente)

        return pd.Series(coeficientes, index=log_da_media.index)

    def obter_velocidade(self) -> pd.Series:
        return self._obter_serie_coeficientes(1)

    def obter_aceleracao(self) -> pd.Series:
        aceleracoes = self._obter_serie_coeficientes(2)
        atr_ = atr(self.maxima, self.minima, self.fechamento, janela=self.atr_janela)
        aceleracao_atr = pd.Series(np.array(aceleracoes) / atr_.values, index=self.fechamento.index)
        return reescalar(aceleracao_atr)

    def obter_concavidade(self) -> pd.Series:
        aceleracoes = self._obter_serie_coeficientes(3)
        atr_ = atr(self.maxima, self.minima, self.fechamento, janela=self.atr_janela)
        aceleracao_atr = pd.Series(np.array(aceleracoes) / atr_.values, index=self.fechamento.index)
        return reescalar(aceleracao_atr)
