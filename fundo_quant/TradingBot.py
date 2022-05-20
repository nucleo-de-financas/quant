from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

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


class EstrategiaVenda(ABC):

    @abstractmethod
    def deve_vender(self) -> Union[Sinalizacao.MANTER, Sinalizacao.VENDER]:
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


class Execucao(ABC):

    @abstractmethod
    def executar(self, *args) -> Posicao:
        pass


@dataclass
class ExecucaoTF(Execucao):
    _transacoes = pd.DataFrame(columns=['posicao_anterior', 'posicao_atual', 'quantidade', 'preco', 'data', 'sinal'])

    def _registrar_transacao(self, pos_anterior: Posicao, pos_atual: Posicao,
                             quantidade: float, preco: float, data: datetime, sinal: Sinalizacao):
        nova_linha = {'posicao_anterior': pos_anterior,
                      'posicao_atual': pos_atual,
                      'quantidade': quantidade,
                      'preco': preco,
                      'data': data,
                      'sinal': sinal}
        nova_linha = pd.DataFrame(nova_linha)
        self._transacoes = pd.concat([self._transacoes, nova_linha])

    def executar(self, pos_anterior: Posicao, sinal: Sinalizacao, preco: float, quantidade: float, data: datetime)\
            -> Posicao:

        pos_atual = None
        if Sinalizacao.COMPRAR or Sinalizacao.STOP_COMPRA:
            if pos_anterior.VENDIDO:
                pos_atual = Posicao.ZERADO
            elif pos_anterior.COMPRADO or pos_anterior.ZERADO:
                pos_atual = Posicao.COMPRADO

        if Sinalizacao.VENDER or Sinalizacao.STOP_VENDA:
            if pos_anterior.COMPRADO:
                pos_atual = Posicao.ZERADO
            elif pos_anterior.VENDIDO or pos_anterior.ZERADO:
                pos_atual = Posicao.VENDIDO

        if pos_atual is not None:
            self._registrar_transacao(pos_anterior, pos_atual, quantidade, preco, data, sinal)
        # Caso não tenha nenhuma atualização
        return pos_atual

    def obter_transacoes(self):
        return self._transacoes

@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    Executor: Execucao
    stop_loss: StopLoss | None = None
    stop_gain: StopGain | None = None
    valor_inicial: float = 100

    # Não acessíveis
    _posicao: Posicao = Posicao.ZERADO
    _sinal: Sinalizacao = Sinalizacao.MANTER

    def track_um_ativo(self, timeseries: pd.Series):

        for qtde_dias in range(len(timeseries)):
            dias_simulados = timeseries.iloc[:qtde_dias + 1]

            # Acionando os stops, tanto de 'loss' quanto de 'gain'.
            if self._posicao != Posicao.ZERADO:
                if self.stop_loss is not None :
                    self._sinal = self.stop_loss.deve_stopar_perda()
                if self.stop_gain is not None:
                    self._sinal = self.stop_gain.deve_stopar_ganho()

            # Acionando estratégia
            self._sinal.estrategia_compra = self.estrategia_compra.deve_comprar()
            self._sinal.estrategia_venda = self.estrategia_venda.deve_vender()


# Colocar executor de sinais para ordens.