from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union, List

import pandas as pd
import datetime


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
    def deve_comprar(self) -> Union[Sinalizacao.MANTER, Sinalizacao.COMPRAR]:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class EstrategiaVenda(ABC):

    @abstractmethod
    def deve_vender(self) -> Union[Sinalizacao.MANTER, Sinalizacao.VENDER]:
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class StopLoss(ABC):

    @abstractmethod
    def deve_stopar_perda(self) -> Union[Sinalizacao.STOP_COMPRA, Sinalizacao.STOP_VENDA, Sinalizacao.MANTER]:
        pass


class StopGain(ABC):
    @abstractmethod
    def deve_stopar_ganho(self) -> Union[Sinalizacao.STOP_COMPRA, Sinalizacao.STOP_VENDA, Sinalizacao.MANTER]:
        pass


class Sinal(ABC):

    @abstractmethod
    def __init__(self):
        pass


class TiposOperacao(Enum):
    COMPRA = 'C'
    VENDA = 'V'


@dataclass
class Operacao:
    horario: datetime.datetime
    quantidade: int
    preco: float
    tipo: TiposOperacao

    def retorno_nominal(self, preco_atual: float):
        return preco_atual - self.preco

    def retorno_percentual(self, preco_atual: float):
        return preco_atual / self.preco - 1
    

@dataclass
class Operacoes:
    """ Responsabilidade de separar/organizar as operações de um mesmo ativo. Como se fosse uma espécie de histórico. 
        Esse histórico terá vários métodos. """
    
    ativo: str
    operacoes: List[Operacao]
    
    def preco_medio(self):
        pass

   
class Executor(ABC):

    @abstractmethod
    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int) -> Operacao:
        pass


class ExecutorTF(Executor):

    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int = 1) -> Operacao:
        if sinal == Sinalizacao.VENDER or sinal.STOP_VENDA:
            return Operacao(horario=horario, quantidade=qtde, preco=preco, tipo=TiposOperacao.VENDA)
        elif sinal == Sinalizacao.COMPRAR or sinal == Sinalizacao.STOP_COMPRA:
            return Operacao(horario=horario, quantidade=qtde, preco=preco, tipo=TiposOperacao.COMPRA)


@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    executor: ExecutorTF

    def track_um_ativo(self, timeseries: pd.Series):

        operacoes = []

        # Iterando a quantidade de dias
        for dia in range(len(timeseries)):

            # Acionando estratégia
            deve_comprar = self.estrategia_compra.deve_comprar()
            deve_vender = self.estrategia_venda.deve_vender()

            # Executando Sinais
            if deve_comprar != Sinalizacao.MANTER:
                op = self.executor.executar(deve_comprar,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=1)
                operacoes.append(op)

            elif self.estrategia_venda.deve_vender() != Sinalizacao.MANTER:
                op = self.executor.executar(deve_vender,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=1)
                operacoes.append(op)

            # Avançando simulação de dados interna.
            self.estrategia_compra.avancar_dia()
            self.estrategia_compra.avancar_dia()

# Todo: Colocar separar de ordens fechadas e abertas e também pegar a posição.
