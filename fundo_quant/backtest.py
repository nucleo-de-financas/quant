from dataclasses import dataclass
from enum import Enum, auto
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
import numpy as np


class AumentarPosicaoErro(Exception):
    """ Erro retornado quando não é permitido aumentar posição. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuantidadeNegativaParaCompraErro(Exception):
    """ Erro retornado quando é pedido uma compra negativa. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuantidadeNulaParaCompraErro(Exception):
    """ Erro retornado quando é pedido uma compra nula, isto é, quantidade negativa. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PrecoNegativoErro(Exception):
    """ Erro retornado quando é inserido um preço negativo. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SemTransacoesErro(Exception):
    """ Erro retornado quando é inserido um preço negativo. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SemPosicaoEmAbertoErro(Exception):
    """ Erro retornado quando não há posições em aberto. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Posicao(Enum):
    comprado = auto()
    vendido = auto()
    zerado = auto()


@dataclass
class Transacoes:
    _historico: pd.DataFrame = pd.DataFrame(columns=['Preço', 'Quantidade'])

    def __str__(self):
        return str(self._historico)

    def __len__(self):
        return len(self._historico)

    @property
    def preco(self):
        return self._historico['Preço']

    @property
    def quantidade(self):
        return self._historico['Quantidade']

    @property
    def qtde_posicao(self):
        """ Retorna a posição atual, em quantidade. """
        return self._historico['Quantidade'].sum()

    def obter_dataframe(self):
        return self._historico

    def add(self, preco, quantidade, data: datetime):
        """ Adiciona novas transações ao histórico. """
        nova_linha = {'Preço': preco, 'Quantidade': quantidade}
        nova_linha = pd.DataFrame(nova_linha, index=[data])
        self._historico = pd.concat([self._historico, nova_linha])

    def filtrar_compras(self):
        """ Filtra somente as transações de compra. """
        return self._historico[self._historico['Quantidade'] > 0].copy()

    def fitrar_vendas(self):
        """ Filtra somente as transações de venda. """
        return self._historico[self._historico['Quantidade'] < 0].copy()


@dataclass
class GerenciadorBacktest:

    proibir_aumentar_pos: bool = True
    _transacoes: List[Transacoes] = None

    def _separar_transacao(self):
        if self._transacoes is None:
            self._transacoes = [Transacoes()]
        elif len(self._transacoes[-1]) > 0 and self._transacoes[-1].qtde_posicao == 0:
            # Se tiver com alguma transação e a posição acumulada for zerada, adicione mais uma transação.
            self._transacoes.append(Transacoes())

    def comprar(self, preco: float, horario: datetime, quantidade=1):

        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou comprar {quantidade} quantidades.")

        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou comprar 0 quantidades')

        self._separar_transacao()

        if self.proibir_aumentar_pos and self._transacoes[-1].qtde_posicao > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de compra "
                                      "e não é permitido pelo gerenciador.")

        self._transacoes[-1].add(preco=preco, quantidade=quantidade, data=horario)

    def vender(self, preco: float, horario: datetime, quantidade=1):

        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou vender 0 quantidades')

        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou vender {quantidade} quantidades.")

        self._separar_transacao()

        if self.proibir_aumentar_pos and self._transacoes[-1].qtde_posicao < 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de venda "
                                      "e não é permitido pelo gerenciador.")

        self._transacoes[-1].add(preco=preco, quantidade=-quantidade, data=horario)

    def zerar(self, preco: float, horario: datetime):

        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        self._separar_transacao()

        if len(self._transacoes[-1]) == 0:
            raise SemPosicaoEmAbertoErro("Não tem como zerar porque não tem posição em aberto.")

        qtde = self._transacoes[-1].qtde_posicao

        self._transacoes[-1].add(preco=preco, quantidade=-qtde, data=horario)

    def inverter(self, preco: float, horario: datetime, quantidade: float = None):

        # Zerando a posição
        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if quantidade is None:
            quantidade = self._transacoes[-1].qtde_posicao

        self.zerar(preco, horario=horario)

        self._separar_transacao()

        self._transacoes[-1].add(preco=preco, quantidade=-quantidade, data=horario)

    def posicao(self) -> Posicao:
        """ Retorna a posição atual da estratégia. """
        if self._transacoes is None:
            return Posicao.zerado
        if self._transacoes[-1].qtde_posicao > 0:
            return Posicao.comprado
        if self._transacoes[-1].qtde_posicao == 0:
            return Posicao.zerado
        return Posicao.vendido

    def obter_historico(self):
        return pd.concat([transacao.obter_dataframe() for transacao in self._transacoes])

    def obter_transacoes(self):
        return self._transacoes


@dataclass
class Estatisticas:

    @staticmethod
    def preco_medio(transacoes: List[Transacoes]):

        """ Identifica a última vez que ficou zerado e a partir daí faz o cálculo do preço médio. """

        transacoes = transacoes[-1]

        if transacoes.qtde_posicao == 0:
            return np.nan

        if transacoes.qtde_posicao > 0:
            compras = transacoes.filtrar_compras()
            return (compras['Preço'] * compras['Quantidade']).sum() / compras['Quantidade'].sum()

        if transacoes.qtde_posicao < 0:
            vendas = transacoes.fitrar_vendas()
            return (vendas['Preço'] * vendas['Quantidade']).sum() / vendas['Quantidade'].sum()

    @staticmethod
    def res_fechado(historico: pd.DataFrame):
        resultado = 0

        for index in range(1, len(historico)):
            qtde_0 = historico['Quantidade'].iloc[index - 1]
            qtde_1 = historico['Quantidade'].iloc[index]
            qtde_cum_0 = historico.iloc[:index - 1]['Quantidade'].cumsum().iloc[-1]
            qtde_cum_1 = historico.iloc[:index]['Quantidade'].cumsum().iloc[-1]
            preco_0 = historico['Preço'].iloc[index - 1]
            preco_1 = historico['Preço'].iloc[index]
            preco_medio_0 = historico['Preço Médio'].iloc[index - 1]
            preco_medio_1 = historico['Preço Médio'].iloc[index]

            # Invertou de comprado para vendido
            if qtde_cum_0 > 0 > qtde_cum_1:
                financeiro_venda = qtde_cum_0 * preco_1
                financeiro_compra = qtde_cum_0 * preco_medio_0
                resultado += financeiro_venda - financeiro_compra

            # Invertou de vendido para comprado
            elif qtde_cum_0 < 0 < qtde_cum_1:
                financeiro_venda = - qtde_cum_0 * preco_medio_1
                financeiro_compra = - qtde_cum_0 * preco_0
                resultado += financeiro_venda - financeiro_compra

            # Comprado anteriormente
            elif qtde_cum_0 > 0:

                # Vendeu.
                if qtde_1 < 0:
                    financeiro_venda = - qtde_1 * preco_1
                    financeiro_compra = - qtde_1 * preco_medio_0
                    resultado += financeiro_venda - financeiro_compra

            # Vendido anteriormente
            elif qtde_0 < 0:

                # Comprou.
                if qtde_1 > 0:
                    financeiro_venda = qtde_1 * preco_1
                    financeiro_compra = qtde_1 * preco_medio_0
                    resultado += financeiro_venda - financeiro_compra

        return resultado

    @staticmethod
    def long_only(historico: pd.DataFrame):
        return historico['Quantidade'].cumsum().min() >= 0


# @dataclass
# class Graficos:
#     _transacoes: pd.DataFrame
#     precos: pd.Series
#
#     def merge(self):
#         return pd.concat([self.transacoes, self.precos], axis=1)
#
#     def calcular_pos(self):
#         df = self.merge()
#         df['Posicao'] = df['Quantidade'].fillna(0).cumsum()
#         return df
#
#     @staticmethod
#     def df_por_index_continuo(df) -> List[pd.DataFrame]:
#         non_sequence = pd.Series(df.index).diff() != 1
#         grouper = non_sequence.cumsum().values
#         dfs = [dfx for _, dfx in df.groupby(grouper)]
#         return dfs
#
#     def separar_por_posicao(self) -> List[pd.DataFrame]:
#         df = self.calcular_pos()
#         df.reset_index(inplace=True)
#         agrupamentos = [agrup[1] for agrup in df.groupby('Posicao')]
#         lista = []
#
#         for agrupamento in agrupamentos:
#             lista += self.df_por_index_continuo(agrupamento)
#
#         res = []
#         for df in lista:
#             df.index = df['index']
#             df = df.drop('index', axis=1)
#             df.index.name = 'data'
#             res.append(df)
#
#         return res
#
#     def plotar_pos(self):
#         df = self.calcular_pos().reset_index()
#         dfs = self.separar_por_posicao()
#         # O ultímo dado da anterior, é o primeiro da posterior.
#         for index in range(len(dfs)):
#             data = dfs[index].iloc[-1].name
#             index_t1 = df[df['index'] == data].index + 1
#             if index_t1 > len(df) - 1:
#                 continue
#             ult_linha = df.iloc[index_t1].copy()
#             ult_linha.index = ult_linha['index']
#             ult_linha.drop('index', inplace=True, axis=1)
#             dfs[index] = pd.concat([dfs[index], ult_linha])
#
#         posicao = {0: 'black', 1: 'grey'}
#         for df in dfs:
#             color = posicao[df['Posicao'].iloc[0]]
#             sns.lineplot(data=df['PreçoMercado'], color=color)
#         plt.show()
#
#     def retorno_estrategia(self, index_inicial=100):
#         pass
#

if __name__ == '__main__':
    ger = GerenciadorBacktest(proibir_aumentar_pos=False)
    ger.comprar(preco=2, quantidade=5, horario=datetime(2022, 4, 1))
    ger.vender(preco=4, quantidade=5, horario=datetime(2022, 5, 1))
    ger.comprar(preco=2, quantidade=5, horario=datetime(2022, 6, 1))
    ger.comprar(preco=2, quantidade=5, horario=datetime(2022, 7, 1))
    ger.inverter(3, horario=datetime(2022, 8, 1), quantidade=6)
    _transacoes = ger.obter_historico()
    print(_transacoes)

# Melhorar o gerenciador para comportar infinitos ativos.
