from dataclasses import dataclass
from enum import Enum, auto
import pandas as pd
from datetime import datetime


class AumentarPosicaoErro(Exception):
    """ Erro retornado quando não é permitido aumentar posição. """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuantidadeNegativaParaCompraErro(Exception):
    """ Erro retornado quando é pedido uma compra negativa. """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuantidadeNulaParaCompraErro(Exception):
    """ Erro retornado quando é pedido uma compra nula, isto é, quantidade negativa. """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Posicao(Enum):
    comprado = auto()
    vendido = auto()
    zerado = auto()


@dataclass
class HistoricoTransacoes:

    transacoes: pd.DataFrame = pd.DataFrame(columns=['Preço', 'Quantidade'])

    def __str__(self):
        return str(self.transacoes)

    def adicionar(self, preco, quantidade, data: datetime = None):
        if data is None:
            data = datetime.now()
        nova_linha = {'Preço': preco, 'Quantidade': quantidade}
        nova_linha = pd.DataFrame(nova_linha, index=[data])
        self.transacoes = pd.concat([nova_linha, self.transacoes])

    def quantidade_posicionada(self):
        return self.transacoes['Quantidade'].sum()

    def preco_medio(self):
        if self.quantidade_posicionada() == 0:
            return None
        return (self.transacoes['Preço'] * self.transacoes['Quantidade']).sum() / self.quantidade_posicionada()

    def compras(self):
        return self.transacoes[self.transacoes['Quantidade'] > 0].copy()

    def vendas(self):
        return self.transacoes[self.transacoes['Quantidade'] < 0].copy()


@dataclass
class Gerenciador:

    transacoes: HistoricoTransacoes = HistoricoTransacoes()
    proibir_aumentar_pos: bool = False

    def posicao(self) -> Posicao:
        """ Retorna a posição da estratégia. """
        if self.transacoes.quantidade_posicionada() > 0:
            return Posicao.comprado
        if self.transacoes.quantidade_posicionada() == 0:
            return Posicao.zerado
        return Posicao.vendido

    def comprar(self, preco: float | int, quantidade=1):
        if self.proibir_aumentar_pos and self.transacoes.quantidade_posicionada() > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de compra "
                                      "e não é permitido pelo gerenciador.")

        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou comprar 0 quantidades')
        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou comprar {quantidade} quantidades.")
        self.transacoes.adicionar(preco=preco, quantidade=quantidade)

    def vender(self, preco: float | int, quantidade=1):
        if self.proibir_aumentar_pos and self.transacoes.quantidade_posicionada() > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de venda "
                                      "e não é permitido pelo gerenciador.")
        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou vender 0 quantidades')
        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou vender {quantidade} quantidades.")
        self.transacoes.adicionar(preco=preco, quantidade=-quantidade)


if __name__ == '__main__':
    ger = Gerenciador(proibir_aumentar_pos=False)
    ger.comprar(2)
    ger.vender(3)
    print(ger.transacoes)
