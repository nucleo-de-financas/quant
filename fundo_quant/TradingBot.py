from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class Posicao(Enum):
    COMPRADO = auto()
    VENDIDO = auto()
    ZERADO = auto()


class Sinalizacao(Enum):
    COMPRAR = auto()
    VENDER = auto()
    STOPAR_COMPRA = auto()
    STOPAR_VENDA = auto()
    MANTER = auto()


class EstrategiaCompra(ABC):

    @abstractmethod
    def deve_comprar(self) -> Union[Sinalizacao.MANTER, Sinalizacao.COMPRAR]:
        pass


class EstrategiaVenda(ABC):

    @abstractmethod
    def deve_vender(self) -> Union[Sinalizacao.MANTER, Sinalizacao.VENDER]:
        pass


class StopLoss(ABC):

    @abstractmethod
    def deve_stopar_perda(self) -> Union[Sinalizacao.STOPAR_COMPRA, Sinalizacao.STOPAR_VENDA, Sinalizacao.MANTER]:
        pass


class StopGain(ABC):
    @abstractmethod
    def deve_stopar_ganho(self) -> Union[Sinalizacao.STOPAR_COMPRA, Sinalizacao.STOPAR_VENDA, Sinalizacao.MANTER]:
        pass


@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    stop_loss: StopLoss | None = None
    stop_gain: StopGain | None = None

    # Não acessíveis
    _posicao = Posicao.ZERADO

    def iniciar(self):

        # Acionando os stops, tanto de 'loss' quanto de 'gain'.
        if self._posicao != Posicao.ZERADO:
            if self.stop_loss is not None:
                self.stop_loss.deve_stopar_perda()
            if self.stop_gain is not None:
                self.stop_gain.deve_stopar_ganho()

        # Acionando estratégia
        self.estrategia_compra.deve_comprar()
        self.estrategia_venda.deve_vender()


# Colocar executor de sinais para ordens.
