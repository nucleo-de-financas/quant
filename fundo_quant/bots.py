from dataclasses import dataclass
from fundo_quant.operacional import Ativo
from fundo_quant.stops import StopGain, StopLoss
import pandas as pd
from abc import ABC, abstractmethod


class EstrategiaCompra(ABC):

    @abstractmethod
    def obter_sinal(self):
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class EstrategiaVenda(ABC):

    @abstractmethod
    def obter_sinal(self):
        pass

    @abstractmethod
    def avancar_dia(self):
        pass


class WalkForward:

    def __init__(self,  precos: pd.Series,
                 estrategia_compra: EstrategiaCompra,
                 estrategia_venda: EstrategiaVenda):
        self.precos = precos.sort_index(ascending=True)
        self.estrategia_compra = estrategia_compra
        self.estrategia_venda = estrategia_venda

    def rodar(self):
        for horario in self.precos.index:
            preco = self.precos.loc[horario]

            self.estrategia_compra.avancar_dia()
            self.estrategia_venda.avancar_dia()
