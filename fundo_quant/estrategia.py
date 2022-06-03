from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd

from fundo_quant.operacional import Posicao, Sinalizacao
from calculadora.analise_tecnica import MediaMovel


class EstrategiaCompra(ABC):

    @abstractmethod
    def deve_comprar(self, posicao: Posicao) -> Sinalizacao:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class EstrategiaVenda(ABC):

    @abstractmethod
    def deve_vender(self, posicao: Posicao) -> Sinalizacao:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


@dataclass
class GoldenCrossCompra(EstrategiaCompra):

    fechamento: pd.Series
    janela_curta: int
    janela_longa: int

    _dias_correntes: int = 1

    def deve_comprar(self, posicao: Posicao) -> Sinalizacao:
        media_curta = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_curta)
        media_longa = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_longa)

        if media_curta.iloc[-1] > media_longa.iloc[-1] and posicao == Posicao.ZERADO:
            return Sinalizacao.COMPRAR
        return Sinalizacao.MANTER

    def avancar_dia(self):
        self._dias_correntes += 1


@dataclass
class GoldenCrossVenda(EstrategiaVenda):
    fechamento: pd.Series
    janela_curta: int
    janela_longa: int

    _dias_correntes: int = 1

    def deve_vender(self, posicao: Posicao) -> Sinalizacao:
        media_curta = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_curta)
        media_longa = MediaMovel.simples(self.fechamento.iloc[:self._dias_correntes], self.janela_longa)

        if media_curta.iloc[-1] < media_longa.iloc[-1] and posicao == Posicao.COMPRADO:
            return Sinalizacao.VENDER
        return Sinalizacao.MANTER

    def avancar_dia(self):
        self._dias_correntes += 1