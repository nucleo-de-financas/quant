from dataclasses import dataclass, field
from typing import List, Union
from datetime import date, datetime


@dataclass
class Pregao:
    """ Representa """
    horario: Union[datetime, date]
    fechamento_ajustado: float
    fechamento: float
    abertura: float
    maxima: float
    minima: float
    volume: float


@dataclass
class AtivoB3:
    """Dataclass padronizado para todos os ativos da Bolsa de Valores de SP."""
    horario: List[date | datetime] = field(default_factory=lambda: [])
    fechamento: List[float] = field(default_factory=lambda: [])
    abertura: List[float] = field(default_factory=lambda: [])
    minima: List[float] = field(default_factory=lambda: [])
    maxima: List[float] = field(default_factory=lambda: [])
    volume: List[float] = field(default_factory=lambda: [])

    def add_dia(self, dia: Pregao):
        self.horario.append(dia.horario)
        self.fechamento.append(dia.fechamento)
        self.abertura.append(dia.abertura)
        self.minima.append(dia.minima)
        self.maxima.append(dia.maxima)
        self.volume.append(dia.volume)
