import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

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


@dataclass
class Operacao:
    horario: datetime.datetime
    quantidade: int
    preco: float
    tipo: TipoOperacao

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

    def preco_medio(self):
        pass

    def registrar(self, operacao: Operacao):
        self._operacoes.append(operacao)

    def _ops_to_df(self):
        """ Transforma a lista de operações em dataframe. """
        dicts = []
        for op in self._operacoes:
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
    def calcular_posicao(quantidade_cumulativa: pd.Series):
        # Definindo a série de posição.
        posicao = quantidade_cumulativa.mask(quantidade_cumulativa > 0, Posicao.COMPRADO)
        posicao = posicao.mask(posicao < 0, Posicao.VENDIDO)
        return posicao.mask(posicao == 0, Posicao.ZERADO)

    def segregar_ops(self):
        """ Segrega as operações em: (1) operações passadas e (2) operações atuais. """
        df = self._ops_to_df()

        x = self.identifica_posicoes_zeros(df['quantidade'])
        print(x)
        print('s')


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


# Todo: Colocar separar de ordens fechadas e abertas e também pegar a posição.

if __name__ == '__main__':
    petr = Operacoes('PETR4')
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=10, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=50, tipo=TipoOperacao.VENDA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=3, preco=50, tipo=TipoOperacao.COMPRA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=-1, preco=50, tipo=TipoOperacao.COMPRA))
    time.sleep(0.1)
    petr.registrar(Operacao(horario=datetime.datetime.now(), quantidade=1, preco=50, tipo=TipoOperacao.COMPRA))
    x = petr.segregar_ops()
    print('ok')
