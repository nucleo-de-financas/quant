from enum import Enum
import ipeadatapy
import pandas as pd


class Codigos(Enum):
    EMBI_BRASIL = 'JPM366_EMBI366'
    IPCA_MENSAL = 'PAN12_IPCAG12'
    IPCA_ANO = 'PAN_IPCAG'
    IBOV = 'GM366_IBVSP366'
    SELIC_OVER = 'GM366_TJOVER366'


class Inflacao:
    ipca_mes = 'PAN12_IPCAG12'
    ipca_trimestre = 'PAN4_IPCAG4'
    ipca_ano = 'PAN_IPCAG'


class Api:

    @staticmethod
    def obter_serie(codigo: Codigos) -> pd.DataFrame:
        serie = ipeadatapy.timeseries(codigo.value)
        serie.dropna(inplace=True)
        return serie
