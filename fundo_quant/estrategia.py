from abc import ABC, abstractmethod
import pandas as pd
from fundo_quant.operacional import AtivoComSaldo, Ordem


class Estrategia(ABC):

    @abstractmethod
    def obter_ordem(self) -> Ordem:
        pass

    @abstractmethod
    def setar_dia(self, i):
        pass


class GoldenCrossLongOnly(Estrategia):

    _dia_atual = 0

    def __init__(self, ativo: AtivoComSaldo,
                 media_curta: pd.Series,
                 media_longa: pd.Series):
        self.media_curta = media_curta
        self.media_longa = media_longa
        self.ativo = ativo

    def deve_comprar(self):
        if self.media_curta.iloc[self._dia_atual] > self.media_longa.iloc[self._dia_atual] and \
                self.ativo.obter_posicao() == 0:
            return Ordem.COMPRAR

    def deve_vender(self):
        if self.media_curta.iloc[self._dia_atual] < self.media_longa.iloc[self._dia_atual] and \
                self.ativo.obter_posicao() > 0:
            return Ordem.VENDER

    def obter_ordem(self) -> Ordem:
        ordem = self.deve_comprar()
        if ordem is not None:
            return ordem
        return self.deve_vender()

    def setar_dia(self, i):
        self._dia_atual = i
