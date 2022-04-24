from dataclasses import dataclass, field
from typing import List
from datetime import date, datetime
import pandas as pd


@dataclass
class Pregao:
    """ Representa """
    horario: datetime | date
    fechamento_ajustado: float
    fechamento: float
    abertura: float
    maxima: float
    minima: float
    volume: float


@dataclass
class AtivoB3:
    """Dataclass padronizado para todos os ativos da Bolsa de Valores de SP."""
    data: List[date | datetime] = field(default_factory=lambda: [])
    fechamento: List[float] = field(default_factory=lambda: [])
    abertura: List[float] = field(default_factory=lambda: [])
    minima: List[float] = field(default_factory=lambda: [])
    maxima: List[float] = field(default_factory=lambda: [])
    volume: List[float] = field(default_factory=lambda: [])

    def add_dia(self, dia: Pregao):
        self.data.append(dia.horario)
        self.fechamento.append(dia.fechamento)
        self.abertura.append(dia.abertura)
        self.minima.append(dia.minima)
        self.maxima.append(dia.maxima)
        self.volume.append(dia.volume)

    def para_df(self):
        dataframe = pd.DataFrame.from_dict(self.__dict__)
        dataframe.index = pd.DatetimeIndex(self.data)
        dataframe.index.name = 'data'
        dataframe.drop(['data'], inplace=True, axis=1)
        return dataframe


if __name__ == '__main__':
    x = Pregao(horario=date.today(), fechamento=20, fechamento_ajustado=20,abertura=20, maxima=20, minima=20, volume=20)
    y = AtivoB3()
    y.add_dia(x)
    y.add_dia(x)
    print(y.para_df())
