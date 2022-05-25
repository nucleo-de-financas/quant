import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import pandas as pd
import datetime
from typing import List
from copy import deepcopy


class Posicao(Enum):
    COMPRADO = auto()
    VENDIDO = auto()
    ZERADO = auto()


class Sinalizacao(Enum):
    COMPRAR = auto()
    VENDER = auto()
    STOP_COMPRA = auto()
    STOP_VENDA = auto()
    MANTER = auto()


class EstrategiaCompra(ABC):

    @abstractmethod
    def deve_comprar(self) -> Sinalizacao:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class EstrategiaVenda(ABC):

    @abstractmethod
    def deve_vender(self) -> Sinalizacao:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class StopLoss(ABC):

    @abstractmethod
    def deve_stopar_perda(self) -> Sinalizacao:
        pass


class StopGain(ABC):
    @abstractmethod
    def deve_stopar_ganho(self) -> Sinalizacao:
        pass


class TipoOperacao(Enum):
    COMPRA = 'C'
    VENDA = 'V'


class InconsistenciaNaOperacaoError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class SaldoError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


@dataclass
class Operacao:
    horario: datetime.datetime
    quantidade: int
    preco: float
    _tipo: TipoOperacao | None = None

    def _inferir_tipo_operacao(self):
        if self.quantidade > 0:
            self._tipo = TipoOperacao.COMPRA
        elif self.quantidade < 0:
            self._tipo = TipoOperacao.VENDA
        else:
            raise InconsistenciaNaOperacaoError("Quantidade a ser operada não pode ser zero.")

    def __post_init__(self):
        # Infere o tipo de operação pela quantidade a ser executada.
        self._inferir_tipo_operacao()

    @property
    def tipo(self):
        return self._tipo

    def valor_financeiro(self):
        return self.quantidade * self.preco

    def retorno_nominal(self, preco_atual: float):
        return preco_atual - self.preco

    def retorno_percentual(self, preco_atual: float):
        return preco_atual / self.preco - 1


@dataclass
class Operacoes:
    """ Responsabilidade de separar/organizar as operações de um mesmo ativo. Como se fosse uma espécie de histórico.
        Esse histórico terá vários métodos. """

    ativo: str
    pl_inicial: float

    _operacoes = []
    _fechadas = []
    _abertas = []

    def __post_init__(self):
        self._caixa = [self.pl_inicial]

    @property
    def caixa_atual(self):
        return self._caixa[-1]

    def _verificar_operacao(self, operacao: Operacao):

        def verificar_saldo_compra() -> bool:
            """ Retorna se é possível comprar. """
            if self.caixa_atual >= operacao.valor_financeiro():
                return True
            else:
                return False

        if operacao.tipo == TipoOperacao.COMPRA:
            return verificar_saldo_compra()
        else:
            return True

    def _calcular_novo_saldo(self, operacao: Operacao):
        self._caixa.append(self.caixa_atual - operacao.valor_financeiro())

    def registrar(self, operacao: Operacao):
        # Toda a vez que for registrar, temos que verificar se é um registro possível. Isto é, se a operação
        # pode ser realizada.
        if not self._verificar_operacao(operacao):
            raise SaldoError(f"Saldo insuficiente para a compra."
                             f"\nSaldo: {round(self.caixa_atual, 2)}"
                             f"\nValor Financeiro: {round(operacao.valor_financeiro(), 2)}")

        # Adiciona as transações
        self._operacoes.append(operacao)

        # Recalcula o saldo
        self._calcular_novo_saldo(operacao)

        # Separa as operações em abertas ou fechadas.
        self._ajustar_operacoes()

    @staticmethod
    def _ops_to_df(operacoes: List[Operacao]):
        """ Transforma a lista de operações em dataframe. """
        dicts = []
        for op in operacoes:
            dicts.append(op.__dict__)
        return pd.DataFrame(dicts).set_index('horario')

    def identifica_posicoes_zeros(self, quantidades: pd.Series):
        """ Identifica os toques da quantidade cumulativa no valor de zero. Ou seja, ultrapassando de cima para baixo
        ou de baixo para cima ou somente tocou e continuou no zero, esse algoritmo identifica os horários. """

        qtde_cum = self.calcular_quantidade_cumulativa(quantidades)
        qtde_cum_anterior = qtde_cum - quantidades

        comprado_to_vendido = quantidades[(qtde_cum > 0) & (qtde_cum_anterior < 0)]
        vendido_to_comprado = quantidades[(qtde_cum < 0) & (qtde_cum_anterior > 0)]
        zerados = quantidades[qtde_cum == 0]
        toques_no_eixo = pd.concat([comprado_to_vendido, vendido_to_comprado, zerados]).sort_index()
        return toques_no_eixo.index

    @staticmethod
    def calcular_quantidade_cumulativa(quantidade: pd.Series):
        qtde_cum = quantidade.cumsum()
        qtde_cum.name = 'quantidade_cumulativa'
        return qtde_cum

    @staticmethod
    def calcular_posicao(qtde_cum: pd.Series):
        # Definindo a série de posição.
        pos = qtde_cum.copy()
        pos.name = 'posicao'
        comprado = pos.loc[pos > 0]
        vendido = pos.loc[pos < 0]
        zerado = pos.loc[pos < 0]
        comprado.loc[:] = Posicao.COMPRADO
        vendido.loc[:] = Posicao.VENDIDO
        zerado.loc[:] = Posicao.VENDIDO
        return pd.concat([comprado, vendido, zerado]).sort_index()

    def _ajustar_operacoes(self):
        operacoes_ajustadas = []
        quantidade_cum0 = 0
        quantidade_cum1 = 0
        for operacao in self._operacoes:
            quantidade_cum1 += operacao.quantidade
            if quantidade_cum1 > 0 > quantidade_cum0 or quantidade_cum1 < 0 < quantidade_cum0:
                operacao1 = deepcopy(operacao)
                operacao2 = deepcopy(operacao)
                operacao1.quantidade = operacao.quantidade - quantidade_cum1
                operacao2.quantidade = quantidade_cum1
                operacoes_ajustadas.append(operacao1)
                operacoes_ajustadas.append(operacao2)
            else:
                operacoes_ajustadas.append(operacao)
            quantidade_cum0 += operacao.quantidade

        self._operacoes = operacoes_ajustadas

    def _segregar_ops(self):
        """ Segrega as operações em: (1) operações passadas e (2) operações atuais. """
        df = self._ops_to_df(self._operacoes)

        inversoes = self.identifica_posicoes_zeros(df['quantidade'])

        # Filtra as operações abertas, porém inclui a última operação fechada.
        op_abertas = df.loc[inversoes[-1]:]

        # Exclui a última operação fechada
        self._abertas = op_abertas[1:]

        # Operações Fechadas
        op_fechadas = df.loc[:self._abertas.index[-1]]

        # Porém, inclui a primeira operação em aberto, portanto, exclui-se.
        self._fechadas = op_fechadas[:-1]

    def preco_medio(self) -> float:
        self._segregar_ops()

        # Se tiver zerado, não vai ter operações abertas.
        if len(self._abertas) <= 0:
            return np.NAN

        # Só se utiliza operações em aberto.
        df = self._abertas.copy()
        qtde_cum = self.calcular_quantidade_cumulativa(df['quantidade'])
        ultima_pos = self.calcular_posicao(qtde_cum).iloc[-1]

        qtde_posicionada = 0
        pmedio = 0
        if ultima_pos == Posicao.COMPRADO:
            for preco, quantidade in zip(df.preco, df.quantidade):
                if quantidade > 0:
                    pmedio = (qtde_posicionada * pmedio + quantidade * preco) / (qtde_posicionada + quantidade)
                qtde_posicionada = qtde_posicionada + quantidade

        elif ultima_pos == Posicao.VENDIDO:
            for preco, quantidade in zip(df.preco, df.quantidade):
                if quantidade < 0:
                    pmedio = (qtde_posicionada * pmedio + quantidade * preco) / (qtde_posicionada + quantidade)
                qtde_posicionada = qtde_posicionada + quantidade

        return pmedio


class Executor(ABC):

    @abstractmethod
    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int) -> Operacao:
        pass


class ExecutorTF(Executor):

    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int = 1) -> Operacao:
        if sinal == Sinalizacao.VENDER or sinal.STOP_VENDA:
            return Operacao(horario=horario, quantidade=-qtde, preco=preco)
        elif sinal == Sinalizacao.COMPRAR or sinal == Sinalizacao.STOP_COMPRA:
            return Operacao(horario=horario, quantidade=qtde, preco=preco)


@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    executor: ExecutorTF

    def track_um_ativo(self, timeseries: pd.Series, pl_inicial):

        operacoes = Operacoes(ativo=str(timeseries.name), pl_inicial=pl_inicial)

        # Iterando a quantidade de dias
        for dia in range(len(timeseries)):

            # Acionando estratégia
            deve_comprar = self.estrategia_compra.deve_comprar()
            deve_vender = self.estrategia_venda.deve_vender()

            # Executando Sinais
            if deve_comprar != Sinalizacao.MANTER:
                op = self.executor.executar(deve_comprar,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=1)
                operacoes.registrar(op)

            elif deve_vender != Sinalizacao.MANTER:
                op = self.executor.executar(deve_vender,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=-1)
                operacoes.registrar(op)

            # Avançando simulação de dados interna.
            self.estrategia_compra.avancar_dia()
            self.estrategia_venda.avancar_dia()

        return operacoes


if __name__ == '__main__':
    petr = Operacoes('PETR4', 100)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=2, preco=49.98))
    time.sleep(0.1)
    print(f'O caixa final é: {petr.caixa_atual}')
