from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import pandas as pd
import datetime
from typing import List, Tuple
from copy import deepcopy


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


class SaldoError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


@dataclass
class Operacao:
    """
    horario: Horario da transação (datetime)
    quantidade: Quantidade transacionada. (int)
    preco: preço do mercado naquele momento. (float)
     """
    horario: datetime.datetime
    quantidade: int
    preco: float
    _tipo: TipoOperacao | None = None

    def _inferir_tipo_operacao(self):
        if self.quantidade > 0:
            self._tipo = TipoOperacao.COMPRA
        elif self.quantidade < 0:
            self._tipo = TipoOperacao.VENDA
        else:
            raise InconsistenciaNaOperacaoError("Quantidade a ser operada não pode ser zero.")

    def __post_init__(self):
        # Infere o tipo de operação pela quantidade a ser executada.
        self._inferir_tipo_operacao()

    @property
    def tipo(self):
        return self._tipo

    def valor_financeiro(self):
        return self.quantidade * self.preco

    def retorno_nominal(self, preco_atual: float):
        return preco_atual - self.preco

    def retorno_percentual(self, preco_atual: float):
        return preco_atual / self.preco - 1


@dataclass
class Operacoes:
    """ Responsabilidade de separar/organizar as operações de um mesmo ativo. """

    ativo: str
    pl_inicial: float

    _operacoes = []
    _fechadas = pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])
    _abertas = pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])

    def __post_init__(self):
        self._caixa = [self.pl_inicial]

    @property
    def caixa_atual(self):
        return round(self._caixa[-1], 2)

    def obter_pos_atual(self):
        return self._ops_to_df(self._operacoes).quantidade.sum()

    def calcular_valor_pos(self, preco_atual: float):
        return round(self.obter_pos_atual() * preco_atual, 2)

    def calcular_pl_atual(self, preco_atual: float):
        return round(self.caixa_atual + self.calcular_valor_pos(preco_atual=preco_atual), 2)

    def retorno_acumulado(self, preco_atual):
        return (self.calcular_pl_atual(preco_atual=preco_atual) / self.pl_inicial) - 1

    def _verificar_operacao(self, operacao: Operacao):

        def verificar_saldo_compra() -> bool:
            """ Retorna se é possível comprar. """
            if self.caixa_atual >= operacao.valor_financeiro():
                return True
            else:
                return False

        if operacao.tipo == TipoOperacao.COMPRA:
            return verificar_saldo_compra()
        else:
            return True

    def _calcular_novo_saldo(self, operacao: Operacao):
        self._caixa.append(self.caixa_atual - operacao.valor_financeiro())

    def _segregar_ops(self):
        """ Segrega as operações em: (1) operações passadas e (2) operações atuais. """
        df = self._ops_to_df(self._operacoes)

        inversoes = self.identifica_posicoes_zeros(df['quantidade'])

        if len(inversoes) == 0:
            self._abertas = df
            self._fechadas = pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])
            return

        # Filtra as operações abertas, porém inclui a última operação fechada.
        op_abertas = df.loc[inversoes[-1]:]

        # Exclui a última operação fechada
        self._abertas = op_abertas[1:]

        # Operações Fechadas
        op_fechadas = df.loc[:inversoes[-1]]

        # Porém, inclui a primeira operação em aberto, portanto, exclui-se.
        self._fechadas = op_fechadas[:-1]

    def registrar(self, operacao: Operacao):
        # Toda a vez que for registrar, temos que verificar se é um registro possível. Isto é, se a operação
        # pode ser realizada.

        def _ajustar_operacoes():
            operacoes_ajustadas = []
            quantidade_cum0 = 0
            quantidade_cum1 = 0
            for op in self._operacoes:
                quantidade_cum1 += op.quantidade
                if quantidade_cum1 > 0 > quantidade_cum0 or quantidade_cum1 < 0 < quantidade_cum0:
                    operacao1 = deepcopy(op)
                    operacao2 = deepcopy(op)
                    operacao1.quantidade = op.quantidade - quantidade_cum1
                    operacao2.quantidade = quantidade_cum1
                    operacoes_ajustadas.append(operacao1)
                    operacoes_ajustadas.append(operacao2)
                else:
                    operacoes_ajustadas.append(op)
                quantidade_cum0 += op.quantidade

            self._operacoes = operacoes_ajustadas

        if not self._verificar_operacao(operacao):
            raise SaldoError(f"Saldo insuficiente para a compra."
                             f"\nSaldo: {round(self.caixa_atual, 2)}"
                             f"\nValor Financeiro: {round(operacao.valor_financeiro(), 2)}")

        # Adiciona as transações
        self._operacoes.append(operacao)

        # Recalcula o saldo
        self._calcular_novo_saldo(operacao)

        # Ajusta operações para nunca inverter diretamente.
        _ajustar_operacoes()

        # Toda a vez que registrar, ele já segrega as operações.
        self._segregar_ops()

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

        # Momento que inverteu de comprado para vendido.
        comprado_to_vendido = quantidades[(qtde_cum > 0) & (qtde_cum_anterior < 0)]
        # Momentos que inverteram de vendido para comprado.
        vendido_to_comprado = quantidades[(qtde_cum < 0) & (qtde_cum_anterior > 0)]
        zerados = quantidades[qtde_cum == 0]
        toques_no_eixo = pd.concat([comprado_to_vendido, vendido_to_comprado, zerados]).sort_index()
        return toques_no_eixo.index

    @staticmethod
    def calcular_quantidade_cumulativa(quantidade: pd.Series):
        qtde_cum = quantidade.cumsum()
        qtde_cum.name = 'quantidade_cumulativa'
        return qtde_cum

    @staticmethod
    def calcular_posicao(qtde_cum: pd.Series):
        # Definindo a série de posição.
        pos = qtde_cum.copy()
        pos.name = 'posicao'
        comprado = pos.loc[pos > 0]
        vendido = pos.loc[pos < 0]
        zerado = pos.loc[pos == 0]
        comprado.loc[:] = Posicao.COMPRADO
        vendido.loc[:] = Posicao.VENDIDO
        zerado.loc[:] = Posicao.ZERADO
        return pd.concat([comprado, vendido, zerado]).sort_index()

    def _preco_medio(self, operacoes: pd.DataFrame):

        if not len(operacoes) > 0:
            return np.NAN

        qtde_cum = self.calcular_quantidade_cumulativa(operacoes['quantidade'])
        ultima_pos = self.calcular_posicao(qtde_cum).iloc[-1]

        qtde_posicionada = 0
        pmedio = 0
        if ultima_pos == Posicao.COMPRADO:
            for preco, quantidade in zip(operacoes.preco, operacoes.quantidade):
                if quantidade > 0:
                    pmedio = (qtde_posicionada * pmedio + quantidade * preco) / (qtde_posicionada + quantidade)
                qtde_posicionada = qtde_posicionada + quantidade

        elif ultima_pos == Posicao.VENDIDO:
            for preco, quantidade in zip(operacoes.preco, operacoes.quantidade):
                if quantidade < 0:
                    pmedio = (qtde_posicionada * pmedio + quantidade * preco) / (qtde_posicionada + quantidade)
                qtde_posicionada = qtde_posicionada + quantidade

        return pmedio

    def preco_medio(self) -> float:

        # Só se utiliza operações em aberto.
        if self._abertas is None:
            return np.NAN
        df = self._abertas.copy()

        return self._preco_medio(df)

    def _dividir_operacoes(self) -> List[pd.DataFrame]:
        df = self.obter_df()
        df['qtde_cum'] = self.calcular_quantidade_cumulativa(df['quantidade'])
        id_ = 1
        ids = []
        for item in df['qtde_cum']:
            ids.append(id_)
            if item == 0:
                id_ += 1
        df['id'] = ids
        # Ainda falta retornar uma lista de df separados por id.
        return [i[1].drop(['id', 'qtde_cum'], axis=1) for i in df.groupby('id')]

    def win_rate(self):
        """ Calcula uma razão de ganhos. """
        dfs = self._dividir_operacoes()
        total_operacoes = 0
        wins = 0
        for df in dfs:
            # Se tiver fechado.
            if df['quantidade'].sum() == 0:
                total_operacoes += 1
                if (-df['quantidade'] * df['preco']).sum() > 0:
                    wins += 1

        # Falta desconsiderar operações em aberto.
        if total_operacoes > 0:
            return wins/total_operacoes
        return np.NAN

    def retornos_por_operacao(self):
        dfs = self._dividir_operacoes()

        # Se não tiver operações.
        if len(dfs) < 0:
            return np.NAN

        def obter_posicao(posicao: pd.Series) -> Posicao:
            return [x for x in posicao.unique().tolist() if x != Posicao.ZERADO][0]

        retornos = {'inicio_operacao': [], 'fim_operacao': [], 'rentabilidade': []}
        # Para cada operação.
        for df in dfs:
            # Se tiver fechado.
            rentabilidade = {'quantidades': [], 'porcentagem': []}
            if df['quantidade'].sum() == 0:

                df['pos'] = self.calcular_posicao(self.calcular_quantidade_cumulativa(df['quantidade']))
                pos = obter_posicao(df['pos'])
                for index in range(len(df)):

                    if pos == Posicao.COMPRADO and df['quantidade'].iloc[index] < 0:
                        quantidade = df['quantidade'].iloc[index]
                        rentabilidade['quantidades'].append(quantidade)
                        porcentagem = df['preco'].iloc[index] / self._preco_medio(df.iloc[:index]) - 1
                        rentabilidade['porcentagem'].append(porcentagem)

                    elif pos == Posicao.VENDIDO and df['quantidade'].iloc[index] > 0:
                        quantidade = df['quantidade'].iloc[index]
                        rentabilidade['quantidades'].append(quantidade)
                        porcentagem = self._preco_medio(df.iloc[:index]) / df['preco'].iloc[index] - 1
                        rentabilidade['porcentagem'].append(porcentagem)

                rent = pd.DataFrame(rentabilidade)
                rent = (rent['quantidades'] * rentabilidade['porcentagem']).sum() / rent['quantidades'].sum()

                retornos['inicio_operacao'].append(df.index[0])
                retornos['fim_operacao'].append(df.index[-1])
                retornos['rentabilidade'].append(rent)

        return pd.DataFrame(retornos)

    def obter_df(self):
        return self._ops_to_df(self._operacoes)

    @property
    def pos_atual(self):
        pos_atual_qtde = self.obter_pos_atual()
        if pos_atual_qtde == 0:
            return Posicao.ZERADO.name
        elif pos_atual_qtde > 0:
            return Posicao.COMPRADO.name
        elif pos_atual_qtde < 0:
            return Posicao.VENDIDO.name


class Executor(ABC):

    @abstractmethod
    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int) -> Operacao:
        pass


class ExecutorTF(Executor):

    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int = 1) -> Operacao:
        if sinal == Sinalizacao.VENDER or sinal.STOP_VENDA:
            return Operacao(horario=horario, quantidade=-qtde, preco=preco)
        elif sinal == Sinalizacao.COMPRAR or sinal == Sinalizacao.STOP_COMPRA:
            return Operacao(horario=horario, quantidade=qtde, preco=preco)


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
    executor: ExecutorTF

    @staticmethod
    def _verificar_timeseries(timeseries: pd.Series) -> bool:
        verificacoes = {'index': False, 'valores': False}

        if timeseries.index.name == 'data' and timeseries.index.dtype == '<M8[ns]':
            verificacoes['index'] = True
        if timeseries.index.dtype == 'float64' or timeseries.index.dtype == 'int64':
            verificacoes['valores'] = True

        return not(False in list(verificacoes.values()))

    def track_um_ativo(self, timeseries: pd.Series, pl_inicial) -> Tuple[Operacoes, pd.Series]:

        if not self._verificar_timeseries(timeseries):
            raise FormatoError('O formato da série temporal não corresponde à:\n'
                               'index.name = data'
                               'index.dtype: [datetime64[ns]]'
                               'values: float64 | int64')

        operacoes = Operacoes(ativo=str(timeseries.name), pl_inicial=pl_inicial)
        rentabilidade = {'data': [], 'valor': []}

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

            elif deve_vender != Sinalizacao.MANTER:
                op = self.executor.executar(deve_vender,
                                            horario=timeseries.iloc[dia], preco=timeseries.iloc[dia], qtde=-1)
                operacoes.registrar(op)

            rentabilidade['data'].append(timeseries.index[dia])
            rentabilidade['valor'].append(operacoes.calcular_pl_atual(timeseries[dia]))

            # Avançando simulação de dados interna.
            self.estrategia_compra.avancar_dia()
            self.estrategia_venda.avancar_dia()

        return operacoes, pd.Series(rentabilidade['valor'], index=rentabilidade['data'])
