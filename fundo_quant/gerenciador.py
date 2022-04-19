from dataclasses import dataclass
from enum import Enum, auto


class AumentarPosicaoErro(Exception):
    """ Erro retornado quando não é permitido aumentar posição. """
    def __init__(self, message):
        self.message = message
        super.__init__(self.message)

    def __str__(self):
        return self.message


class Posicao(Enum):
    comprado = auto()
    vendido = auto()
    zerado = auto()


@dataclass
class Gerenciamento:

    qntde: int = 0
    aumentar_pos: bool = True

    def posicao(self) -> Posicao:
        """ Retorna a posição da estratégia. """
        if self.qntde > 0:
            return Posicao.comprado
        elif self.qntde == 0:
            return Posicao.zerado
        return Posicao.vendido

    def comprar(self):
        if self.aumentar_pos and self.qntde > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição e não é permitido pelo gerenciador.")
        self.qntde += 1

    def vender(self):
        if self.aumentar_pos and self.qntde > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição e não é permitido pelo gerenciador.")
        self.qntde -= 1