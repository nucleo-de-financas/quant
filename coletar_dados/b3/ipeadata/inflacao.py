import ipeadatapy as ipea


class Inflacao:
    ipca_mes = 'PAN12_IPCAG12'
    ipca_trimestre = 'PAN4_IPCAG4'
    ipca_ano = 'PAN_IPCAG'


def ipca_mensal():
    """
    Coleta a série temporal do IPCA mensal.
    >>ipeadatapy.timeseries(Inflacao.ipca_mes)
                   YEAR  DAY  ...                   RAW DATE VALUE ((% a.a.))
    DATE                   ...
    2022-01-01  2022    1  ...  2022-01-01T00:00:00-03:00         6.676334
    2022-02-01  2022    1  ...  2022-02-01T00:00:00-03:00        12.817282
    2022-03-01  2022    1  ...  2022-03-01T00:00:00-03:00        21.269854"""
    return ipea.timeseries(Inflacao.ipca_mes)


def ipca_trimestral():
    """>>>ipeadatapy.timeseries(Inflacao.ipca_mes)
                   YEAR  DAY  ...                   RAW DATE VALUE ((% a.a.))
    DATE                   ...
    2022-01-01  2022    1  ...  2022-01-01T00:00:00-03:00         6.676334
    2022-02-01  2022    1  ...  2022-02-01T00:00:00-03:00        12.817282
    2022-03-01  2022    1  ...  2022-03-01T00:00:00-03:00        21.269854"""
    return ipea.timeseries(Inflacao.ipca_trimestre)


def ipca_anual():
    """>>>ipeadatapy.timeseries(Inflacao.ipca_mes)
                   YEAR  DAY  ...                   RAW DATE VALUE ((% a.a.))
    DATE                   ...
    2022-01-01  2022    1  ...  2022-01-01T00:00:00-03:00         6.676334
    2022-02-01  2022    1  ...  2022-02-01T00:00:00-03:00        12.817282
    2022-03-01  2022    1  ...  2022-03-01T00:00:00-03:00        21.269854"""
    return ipea.timeseries(Inflacao.ipca_ano)
