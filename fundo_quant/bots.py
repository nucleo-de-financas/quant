from dataclasses import dataclass
import pandas as pd
from typing import Tuple

from fundo_quant.operacional import Posicao, Sinalizacao, Historico
from fundo_quant.estrategia import EstrategiaCompra, EstrategiaVenda
from fundo_quant.gerenciamento_risco import StopGain, StopLoss
from fundo_quant.executor import Executor, ExecutorTF


class FormatoError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


@dataclass
class TrendFollowingBot:

    # Acessíveis
    estrategia_compra: EstrategiaCompra
    estrategia_venda: EstrategiaVenda
    stop_loss: StopLoss = None
    stop_gain: StopGain = None
    executor: Executor = ExecutorTF()

    @staticmethod
    def _verificar_timeseries(timeseries: pd.Series) -> None:

        if not (timeseries.index.name == 'data' or timeseries.index.name == 'Data'):
            raise FormatoError('O formato da série temporal não corresponde à:\n'
                               'index.name = data'
                               'index.dtype: [datetime64[ns]]'
                               'values: float64 | int64')

        if not (timeseries.dtype == 'float64' or timeseries.dtype == 'int64'):

            raise FormatoError('O formato da série temporal não corresponde à:\n'
                               'index.name = data'
                               'index.dtype: [datetime64[ns]]'
                               'values: float64 | int64')

    def track_um_ativo(self, timeseries: pd.Series, pl_inicial) -> Tuple[Historico, pd.Series]:

        self._verificar_timeseries(timeseries)

        operacoes = Historico(ativo=str(timeseries.name), pl_inicial=pl_inicial)
        rentabilidade = {'data': [], 'valor': []}
        pos: Posicao = Posicao.ZERADO

        # Iterando a quantidade de dias
        for dia in range(len(timeseries)):

            # Acionando estratégia
            deve_comprar = self.estrategia_compra.deve_comprar(pos)
            deve_vender = self.estrategia_venda.deve_vender(pos)

            # Executando Sinais
            if deve_comprar != Sinalizacao.MANTER:
                op = self.executor.executar(sinal=deve_comprar,
                                            horario=timeseries.index[dia], preco=timeseries.iloc[dia], qtde=1)
                operacoes.registrar(op)

            elif deve_vender != Sinalizacao.MANTER:
                op = self.executor.executar(sinal=deve_vender,
                                            horario=timeseries.index[dia], preco=timeseries.iloc[dia], qtde=-1)
                operacoes.registrar(op)

            if self.stop_loss is not None and deve_comprar == Sinalizacao.MANTER and deve_vender == Sinalizacao.MANTER:
                deve_stopar_perda = self.stop_loss.deve_stopar_perda(
                                    preco_atual=timeseries[dia],
                                    posicao=operacoes.pos_atual,
                                    preco_medio=operacoes.preco_medio())

                if deve_stopar_perda != Sinalizacao.MANTER:
                    op = self.executor.executar(sinal=deve_stopar_perda,
                                                horario=timeseries.index[dia], preco=timeseries.iloc[dia], qtde=-1)
                    operacoes.registrar(op)

            if self.stop_gain is not None and deve_comprar == Sinalizacao.MANTER and deve_vender == Sinalizacao.MANTER:
                deve_stopar_ganho = self.stop_gain.deve_stopar_ganho(
                                    preco_atual=timeseries[dia],
                                    posicao=operacoes.pos_atual,
                                    preco_medio=operacoes.preco_medio())

                if deve_stopar_ganho != Sinalizacao.MANTER:
                    op = self.executor.executar(sinal=deve_stopar_ganho,
                                                horario=timeseries.index[dia], preco=timeseries.iloc[dia], qtde=-1)
                    operacoes.registrar(op)

            pos = operacoes.pos_atual

            rentabilidade['data'].append(timeseries.index[dia])
            rentabilidade['valor'].append(operacoes.pl_atual(timeseries[dia]))

            # Avançando simulação de dados interna.
            self.estrategia_compra.avancar_dia()
            self.estrategia_venda.avancar_dia()

        return operacoes, pd.Series(rentabilidade['valor'], index=rentabilidade['data'], dtype='float64')
