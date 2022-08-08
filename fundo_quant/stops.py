from abc import ABC, abstractmethod
from dataclasses import dataclass

from fundo_quant.operacional import Posicao, Sinalizacao


class StopLoss(ABC):

    @abstractmethod
    def deve_stopar_perda(self, preco_atual: float, posicao: Posicao, preco_medio: float) -> Sinalizacao:
        pass


class StopGain(ABC):
    @abstractmethod
    def deve_stopar_ganho(self, preco_atual: float, posicao: Posicao, preco_medio: float) -> Sinalizacao:
        pass


@dataclass
class StopLossBasico(StopLoss):

    max_loss: float = 0.03

    def deve_stopar_perda(self,  preco_atual: float, posicao: Posicao, preco_medio: float) -> Sinalizacao:
        if posicao == Posicao.COMPRADO and (preco_atual/preco_medio - 1) < -self.max_loss:
            return Sinalizacao.STOP_VENDER
        elif posicao == Posicao.VENDIDO and (preco_medio/preco_atual - 1) < -self.max_loss:
            return Sinalizacao.STOP_COMPRAR
        return Sinalizacao.MANTER


@dataclass
class StopGainBasico(StopGain):

    max_gain: float = 0.03

    def deve_stopar_ganho(self,  preco_atual: float, posicao: Posicao, preco_medio: float) -> Sinalizacao:
        if posicao == Posicao.COMPRADO and (preco_atual/preco_medio - 1) > self.max_gain:
            return Sinalizacao.STOP_VENDER
        elif posicao == Posicao.VENDIDO and (preco_medio/preco_atual - 1) > self.max_gain:
            return Sinalizacao.STOP_COMPRAR
        return Sinalizacao.MANTER
