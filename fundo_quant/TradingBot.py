import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import pandas as pd
import datetime
from typing import List


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


@dataclass
class Operacao:
    horario: datetime.datetime
    quantidade: int
    preco: float
    tipo: TipoOperacao

    def validar_consistencia_quantidades(self):
        if self.tipo == TipoOperacao.VENDA and self.quantidade < 0:
            return True
        if self.tipo == TipoOperacao.COMPRA and self.quantidade > 0:
            return True
        if self.tipo == TipoOperacao.VENDA and self.quantidade > 0:
            return False
        if self.tipo == TipoOperacao.COMPRA and self.quantidade < 0:
            return False

    def __post_init__(self):
        if not self.validar_consistencia_quantidades():
            raise InconsistenciaNaOperacaoError(f'A quantidade {self.quantidade} não é consistente como o tipo de '
                                                f'operação de {self.tipo.name}')

    def retorno_nominal(self, preco_atual: float):
        return preco_atual - self.preco

    def retorno_percentual(self, preco_atual: float):
        return preco_atual / self.preco - 1


@dataclass
class Operacoes:
    """ Responsabilidade de separar/organizar as operações de um mesmo ativo. Como se fosse uma espécie de histórico.
        Esse histórico terá vários métodos. """

    ativo: str
    _operacoes = []
    _fechadas = []
    _abertas = []

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

    def registrar(self, operacao: Operacao):
        self._operacoes.append(operacao)

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
        toques_no_eixo = pd.concat([comprado_to_vendido, vendido_to_comprado, zerados])
        return toques_no_eixo.index

    @staticmethod
    def calcular_quantidade_cumulativa(quantidade: pd.Series):
        return quantidade.cumsum()

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


class Executor(ABC):

    @abstractmethod
    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int) -> Operacao:
        pass


class ExecutorTF(Executor):

    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int = 1) -> Operacao:
        if sinal == Sinalizacao.VENDER or sinal.STOP_VENDA:
            return Operacao(horario=horario, quantidade=-qtde, preco=preco, tipo=TipoOperacao.VENDA)
        elif sinal == Sinalizacao.COMPRAR or sinal == Sinalizacao.STOP_COMPRA:
            return Operacao(horario=horario, quantidade=qtde, preco=preco, tipo=TipoOperacao.COMPRA)


@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    executor: ExecutorTF

    def track_um_ativo(self, timeseries: pd.Series):

        operacoes = Operacoes(ativo=str(timeseries.name))

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

            elif self.estrategia_venda.deve_vender() != Sinalizacao.MANTER:
                op = self.executor.executar(deve_vender,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=1)
                operacoes.registrar(op)

            # Avançando simulação de dados interna.
            self.estrategia_compra.avancar_dia()
            self.estrategia_venda.avancar_dia()

        return operacoes

# Todo: Colocar valor inicial de trade no histórico e no bot.


if __name__ == '__main__':
    petr = Operacoes('PETR4')
    print(petr)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=10, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=50, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=3, preco=50, tipo=TipoOperacao.COMPRA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=50, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=50, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=100, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=100, tipo=TipoOperacao.VENDA))
    x = petr.preco_medio()
    print('ok')
