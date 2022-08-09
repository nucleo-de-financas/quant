from dataclasses import dataclass, field
import datetime
from typing import List
from enum import Enum


class SaldoError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Ordem(Enum):
    COMPRAR = 1
    VENDER = 2


@dataclass(order=True)
class Compra:
    preco: float
    quantidade: int | float
    horario: datetime = field(compare=True)

    @property
    def valor_financeiro(self):
        return self.preco * self.quantidade


@dataclass(order=True)
class Venda:
    preco: float
    quantidade: int
    horario: datetime = field(compare=True)

    @property
    def valor_financeiro(self):
        return self.preco * self.quantidade


class Ativo:

    def __init__(self):
        self._operacoes: list[Compra | Venda] = []

    def obter_compras(self) -> List[Compra] | None:
        if self._operacoes is not None:
            return [operacao for operacao in self._operacoes if isinstance(operacao, Compra)]

    def obter_vendas(self) -> List[Venda] | None:
        if self._operacoes is not None:
            return [operacao for operacao in self._operacoes if isinstance(operacao, Venda)]

    def obter_quantidade_comprada(self) -> int:
        compras = self.obter_compras()
        if compras is not None:
            return sum([compra.quantidade for compra in compras])
        return 0

    def obter_quantidade_vendida(self) -> int:
        vendas = self.obter_vendas()
        if vendas is not None:
            return sum([venda.quantidade for venda in vendas])
        return 0

    def _adicionar_compra(self, preco: float, quantidade: int, horario: datetime):
        self._operacoes.append(Compra(preco=preco, quantidade=quantidade, horario=horario))

    def _adicionar_venda(self, preco: float, quantidade: int, horario: datetime):
        self._operacoes.append(Venda(preco=preco, quantidade=quantidade, horario=horario))

    def comprar(self, preco: float, quantidade: int, horario: datetime):
        posicao = self.obter_posicao()
        if quantidade > abs(posicao) and posicao < 0:
            self.fechar_posicao(preco=preco, horario=horario)
            self._adicionar_compra(preco=preco, quantidade=quantidade+posicao, horario=horario)
        else:
            self._adicionar_compra(preco=preco, quantidade=quantidade, horario=horario)

    def vender(self, preco: float, quantidade: int, horario: datetime):
        posicao = self.obter_posicao()
        if quantidade > posicao > 0:
            self.fechar_posicao(preco=preco, horario=horario)
            self._adicionar_venda(preco=preco, quantidade=quantidade-posicao, horario=horario)
        else:
            self._adicionar_venda(preco=preco, quantidade=quantidade, horario=horario)

    def obter_posicao(self) -> int:
        return self.obter_quantidade_comprada() - self.obter_quantidade_vendida()

    def fechar_posicao(self, preco: float, horario: datetime):
        posicao = self.obter_posicao()
        if posicao > 0:
            self._adicionar_venda(preco=preco, quantidade=posicao, horario=horario)
        elif posicao < 0:
            self._adicionar_compra(preco=preco, quantidade=-posicao, horario=horario)

    def inverter_posicao(self, preco: float, horario: datetime):
        posicao = self.obter_posicao()
        if posicao > 0:
            self.vender(preco=preco, quantidade=2 * posicao, horario=horario)
        elif posicao < 0:
            self.comprar(preco=preco, quantidade=-2 * posicao, horario=horario)

    def obter_operacoes_abertas(self) -> List[Compra | Venda] | None:
        posicao = self.obter_posicao()
        if posicao == 0:
            return
        if posicao > 0:
            operacoes = self.obter_compras()
        else:
            operacoes = self.obter_vendas()
        operacoes.reverse()
        soma = 0
        operacoes_abertas = []
        for operacao in operacoes:
            soma = soma + operacao.quantidade
            operacoes_abertas.append(operacao)
            if soma == abs(posicao):
                return operacoes_abertas

    def preco_medio(self):
        operacoes = self.obter_operacoes_abertas()
        if operacoes is None:
            return 0
        quantidade = sum([operacao.quantidade for operacao in operacoes])
        valor_financeiro = sum([operacao.valor_financeiro for operacao in operacoes])
        return round(abs(valor_financeiro / quantidade), 10)


class AtivoComSaldo:

    def __init__(self, saldo_inicial):
        self._operacoes: list[Compra | Venda] = []
        self.saldo = saldo_inicial
        self.principal = saldo_inicial

    def adicionar_capital(self, valor: float):
        self.saldo += valor
        self.principal += valor

    def retirar_capital(self, valor: float):
        if valor > self.saldo:
            raise SaldoError(f"Não há saldo disponível para retirar o valor de {valor}.")
        self.saldo -= valor
        self.principal -= valor

    def obter_compras(self) -> List[Compra] | None:
        if self._operacoes is not None:
            return [operacao for operacao in self._operacoes if isinstance(operacao, Compra)]

    def obter_vendas(self) -> List[Venda] | None:
        if self._operacoes is not None:
            return [operacao for operacao in self._operacoes if isinstance(operacao, Venda)]

    def obter_quantidade_comprada(self) -> int:
        compras = self.obter_compras()
        if compras is not None:
            return sum([compra.quantidade for compra in compras])
        return 0

    def obter_quantidade_vendida(self) -> int:
        vendas = self.obter_vendas()
        if vendas is not None:
            return sum([venda.quantidade for venda in vendas])
        return 0

    def _verificar_saldo_compra(self, preco: float, quantidade: int):
        valor_financeiro = preco * quantidade
        if valor_financeiro > self.saldo:
            raise SaldoError(f"Saldo de {round(self.saldo ,2)}"
                             f" insuficiente para compra no valor de {round(valor_financeiro,2)}")

    def _adicionar_compra(self, preco: float, quantidade: int, horario: datetime):
        self._verificar_saldo_compra(preco=preco, quantidade=quantidade)
        self.saldo -= preco * quantidade
        self._operacoes.append(Compra(preco=preco, quantidade=quantidade, horario=horario))

    def _adicionar_venda(self, preco: float, quantidade: int, horario: datetime):
        self._operacoes.append(Venda(preco=preco, quantidade=quantidade, horario=horario))
        self.saldo += preco * quantidade

    def comprar(self, preco: float, quantidade: int, horario: datetime):
        posicao = self.obter_posicao()
        if quantidade > abs(posicao) and posicao < 0:
            self.fechar_posicao(preco=preco, horario=horario)
            self._adicionar_compra(preco=preco, quantidade=quantidade+posicao, horario=horario)
        else:
            self._adicionar_compra(preco=preco, quantidade=quantidade, horario=horario)

    def vender(self, preco: float, quantidade: int, horario: datetime):
        posicao = self.obter_posicao()
        if quantidade > posicao > 0:
            self.fechar_posicao(preco=preco, horario=horario)
            self._adicionar_venda(preco=preco, quantidade=quantidade-posicao, horario=horario)
        else:
            self._adicionar_venda(preco=preco, quantidade=quantidade, horario=horario)

    def obter_posicao(self) -> int:
        return self.obter_quantidade_comprada() - self.obter_quantidade_vendida()

    def fechar_posicao(self, preco: float, horario: datetime):
        posicao = self.obter_posicao()
        if posicao > 0:
            self._adicionar_venda(preco=preco, quantidade=posicao, horario=horario)
        elif posicao < 0:
            self._adicionar_compra(preco=preco, quantidade=-posicao, horario=horario)

    def inverter_posicao(self, preco: float, horario: datetime):
        posicao = self.obter_posicao()
        if posicao > 0:
            self.vender(preco=preco, quantidade=2 * posicao, horario=horario)
        elif posicao < 0:
            self.comprar(preco=preco, quantidade=-2 * posicao, horario=horario)

    def obter_operacoes_abertas(self) -> List[Compra | Venda] | None:
        posicao = self.obter_posicao()
        if posicao == 0:
            return
        if posicao > 0:
            operacoes = self.obter_compras()
        else:
            operacoes = self.obter_vendas()
        operacoes.reverse()
        soma = 0
        operacoes_abertas = []
        for operacao in operacoes:
            soma = soma + operacao.quantidade
            operacoes_abertas.append(operacao)
            if soma == abs(posicao):
                return operacoes_abertas

    def preco_medio(self):
        operacoes = self.obter_operacoes_abertas()
        if operacoes is None:
            return 0
        quantidade = sum([operacao.quantidade for operacao in operacoes])
        valor_financeiro = sum([operacao.valor_financeiro for operacao in operacoes])
        return round(abs(valor_financeiro / quantidade), 10)

    def obter_resultado_por_unidade_em_aberto(self, preco_atual: float):
        posicao = self.obter_posicao()
        if posicao > 0:
            return preco_atual - self.preco_medio()
        if posicao < 0:
            return self.preco_medio() - preco_atual
        return 0

    def obter_valor_de_entrada_da_posicao(self):
        return self.preco_medio() * abs(self.obter_posicao())

    def obter_resultado_em_aberto(self, preco_atual: float):
        return round(self.obter_resultado_por_unidade_em_aberto(preco_atual) * abs(self.obter_posicao()), 10)

    def obter_resultado_em_aberto_pct(self, preco_atual: float):
        if self.obter_valor_de_entrada_da_posicao() == 0:
            return 0
        return self.obter_resultado_em_aberto(preco_atual=preco_atual) / self.obter_valor_de_entrada_da_posicao()

    def obter_patrimonio_liquido(self, preco_atual: float):
        posicao = self.obter_posicao()
        if posicao > 0:
            return self.saldo + self.obter_valor_de_entrada_da_posicao() + self.obter_resultado_em_aberto(preco_atual)
        elif posicao < 0:
            return self.saldo - self.obter_valor_de_entrada_da_posicao() + self.obter_resultado_em_aberto(preco_atual)
        return self.saldo

    def lucro_acumulado(self, preco_atual: float):
        return self.obter_patrimonio_liquido(preco_atual=preco_atual) - self.principal

    def lucro_acumulado_pct(self, preco_atual: float):
        return round(self.obter_patrimonio_liquido(preco_atual=preco_atual) / self.principal - 1, 10)
