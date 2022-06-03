from dataclasses import dataclass
import datetime
from enum import Enum, auto
from typing import List
import pandas as pd
from copy import deepcopy
import numpy as np


class Posicao(Enum):
    COMPRADO = auto()
    VENDIDO = auto()
    ZERADO = auto()


class Sinalizacao(Enum):
    COMPRAR = auto()
    VENDER = auto()
    STOP_COMPRAR = auto()
    STOP_VENDER = auto()
    MANTER = auto()


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

    def verificar_restricoes(self):
        if self.quantidade == 0:
            raise InconsistenciaNaOperacaoError("Quantidade a ser operada não pode ser zero.")
        if self.preco < 0:
            raise InconsistenciaNaOperacaoError(f"Não existe preço negativo. \n Preço: {self.preco}")

    def _verificar_tipo_atts(self) -> bool:
        """ Retorna True se as atributos estão preenchidos conforme o typing. """
        horario_bool = isinstance(self.horario, datetime.datetime)
        quantidade_bool = isinstance(self.quantidade, int)
        preco_bool = isinstance(self.preco, float) or isinstance(self.preco, int)

        return bool(horario_bool*quantidade_bool*preco_bool)

    def __post_init__(self):

        # Verificando os tipos das variáveis.
        if not self._verificar_tipo_atts():
            raise InconsistenciaNaOperacaoError("Os tipos das variáveis não estão corretos.")

        # Verificar números plausíveis para uma operação.
        self.verificar_restricoes()

        # Infere a operação pela quantidade a ser executada.
        self._inferir_tipo_operacao()

    @property
    def tipo(self):
        return self._tipo

    def valor_financeiro(self):
        return self.quantidade * self.preco


@dataclass
class Operacoes:
    """ Responsabilidade de separar/organizar as operações de um mesmo ativo. """

    ativo: str
    pl_inicial: float

    _operacoes: List = None
    _fechadas = pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])
    _abertas = pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])

    def __post_init__(self):
        self._caixa = [self.pl_inicial]
        if self._operacoes is None:
            self._operacoes = []

    @property
    def caixa_atual(self):
        return round(self._caixa[-1], 2)

    def obter_pos_atual(self):
        df = self._ops_to_df(self._operacoes)
        if df is not None:
            return df.quantidade.sum()
        return 0

    def _calcular_valor_pos(self, preco_atual: float):
        return self.obter_pos_atual() * preco_atual

    def _calcular_pl_atual(self, preco_atual: float):
        return self.caixa_atual + self._calcular_valor_pos(preco_atual=preco_atual)

    def pl_atual(self, preco_atual: float):
        return round(self._calcular_pl_atual(preco_atual=preco_atual), 2)

    def retorno_acumulado(self, preco_atual):
        return (self._calcular_pl_atual(preco_atual=preco_atual) / self.pl_inicial) - 1

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
        if df is None:
            return
        inversoes = self._identifica_posicoes_zeros(df['quantidade'])

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

        def _ajustar_operacoes(_operacoes: List[Operacao]):
            operacoes_ajustadas = []
            quantidade_cum0 = 0
            quantidade_cum1 = 0
            for op in _operacoes:
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

            return operacoes_ajustadas

        if not self._verificar_operacao(operacao):
            raise SaldoError(f"Saldo insuficiente para a compra."
                             f"\nSaldo: {round(self.caixa_atual, 2)}"
                             f"\nValor Financeiro: {round(operacao.valor_financeiro(), 2)}")

        # Adiciona as transações
        self._operacoes.append(operacao)

        # Recalcula o saldo
        self._calcular_novo_saldo(operacao)

        # Ajusta operações para nunca inverter diretamente.
        self._operacoes = _ajustar_operacoes(self._operacoes)

        # Toda a vez que registrar, ele já segrega as operações.
        self._segregar_ops()

    @staticmethod
    def _ops_to_df(operacoes: List[Operacao]) -> pd.DataFrame | None:
        """ Transforma a lista de operações em dataframe. """
        dicts = []
        for op in operacoes:
            dicts.append(op.__dict__)
        if len(dicts) > 0:
            return pd.DataFrame(dicts).set_index('horario')

    def _identifica_posicoes_zeros(self, quantidades: pd.Series):
        """ Identifica os toques da quantidade cumulativa no valor de zero. Ou seja, ultrapassando de cima para baixo
        ou de baixo para cima ou somente tocou e continuou no zero, esse algoritmo identifica os horários. """

        qtde_cum = self._calcular_quantidade_cumulativa(quantidades)
        qtde_cum_anterior = qtde_cum - quantidades

        # Momento que inverteu de comprado para vendido.
        comprado_to_vendido = quantidades[(qtde_cum > 0) & (qtde_cum_anterior < 0)]
        # Momentos que inverteram de vendido para comprado.
        vendido_to_comprado = quantidades[(qtde_cum < 0) & (qtde_cum_anterior > 0)]
        zerados = quantidades[qtde_cum == 0]
        toques_no_eixo = pd.concat([comprado_to_vendido, vendido_to_comprado, zerados]).sort_index()
        return toques_no_eixo.index

    @staticmethod
    def _calcular_quantidade_cumulativa(quantidade: pd.Series):
        qtde_cum = quantidade.cumsum()
        qtde_cum.name = 'quantidade_cumulativa'
        return qtde_cum

    @staticmethod
    def _calcular_posicao(qtde_cum: pd.Series):
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

        qtde_cum = self._calcular_quantidade_cumulativa(operacoes['quantidade'])
        ultima_pos = self._calcular_posicao(qtde_cum).iloc[-1]

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
        df['qtde_cum'] = self._calcular_quantidade_cumulativa(df['quantidade'])
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

                df['pos'] = self._calcular_posicao(self._calcular_quantidade_cumulativa(df['quantidade']))
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
        df = self._ops_to_df(self._operacoes)
        if df is None:
            return pd.DataFrame(columns=['quantidade', 'preco', '_tipo'])
        return df

    @property
    def pos_atual(self):
        pos_atual_qtde = self.obter_pos_atual()
        if pos_atual_qtde == 0:
            return Posicao.ZERADO
        elif pos_atual_qtde > 0:
            return Posicao.COMPRADO
        elif pos_atual_qtde < 0:
            return Posicao.VENDIDO
