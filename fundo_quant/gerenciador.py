from dataclasses import dataclass
from enum import Enum, auto
import pandas as pd
from datetime import datetime


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

    historico: pd.DataFrame = pd.DataFrame(columns=['Preço', 'Quantidade'])

    def __str__(self):
        return str(self.historico)

    def _transacoes_desde_ultima_troca_pos(self):
        # Identificando último posição zerada
        qtde_cum = self.quantidade_acumulada().copy()

        prev_value = 0
        mudanca_pos = []

        for index, value in enumerate(qtde_cum, 0):  # starting index of 0
            if prev_value > 0 >= value:
                mudanca_pos.append(index)
            if prev_value < 0 <= value:
                mudanca_pos.append(index)
            if prev_value == 0 and value != 0:
                mudanca_pos.append(index)
            prev_value = value

        ult_mudanca_pos = mudanca_pos[-1]
        # Filtrando df para todas as transações desde a última troca de posição.
        return self.historico.iloc[ult_mudanca_pos:].copy()

    def adicionar(self, preco, quantidade, data: datetime = None):
        if data is None:
            data = datetime.now()
        nova_linha = {'Preço': preco, 'Quantidade': quantidade}
        nova_linha = pd.DataFrame(nova_linha, index=[data])
        self.historico = pd.concat([self.historico, nova_linha])

    def qtde_pos(self):
        return self.historico['Quantidade'].sum()

    def quantidade_acumulada(self):
        return self.historico['Quantidade'].cumsum()

    def pmedio(self):
        """ Identifica a última vez que ficou zerado, e a partir daí faz o cálculo do preço médio. """

        if self.qtde_pos() == 0:
            return 0

        df = self._transacoes_desde_ultima_troca_pos()

        compras = df[df['Quantidade'] > 0]
        vendas = df[df['Quantidade'] < 0]

        if self.qtde_pos() > 0:
            return (compras['Preço'] * compras['Quantidade']).sum() / compras['Quantidade'].sum()

        if self.qtde_pos() < 0:
            return (vendas['Preço'] * vendas['Quantidade']).sum() / vendas['Quantidade'].sum()

    def compras(self):
        return self.historico[self.historico['Quantidade'] > 0].copy()

    def vendas(self):
        return self.historico[self.historico['Quantidade'] < 0].copy()

    def serie_pmedio(self):
        precos = []
        df_a_iterar = self.historico.copy()
        for linha_n in range(len(df_a_iterar)):
            # Adaptação
            linha = df_a_iterar.iloc[:linha_n+1]
            self.historico = pd.DataFrame(linha)

            precos.append(self.pmedio())

        self.historico = df_a_iterar

        return pd.Series(precos, index=df_a_iterar.index, name='Preco Médio')

    def resultado_fechado(self):

        dfs = [self.serie_pmedio(), self.historico[['Preço', 'Quantidade']], self.quantidade_acumulada()]
        transacoes = pd.concat(dfs, axis=1)
        transacoes.columns = ['Preço Médio', 'Preço', 'Quantidade', 'Quantidade Acumulada']

        resultado = 0

        for index in range(1, len(transacoes)):

            # Invertou de comprado para vendido
            if transacoes['Quantidade Acumulada'].iloc[index - 1] > 0 >\
                    transacoes['Quantidade Acumulada'].iloc[index]:
                qntde_cum_anterior = transacoes['Quantidade Acumulada'].iloc[index - 1]
                financeiro_venda = qntde_cum_anterior * transacoes['Preço'].iloc[index]
                financeiro_compra = qntde_cum_anterior * transacoes['Preço Médio'].iloc[
                    index - 1]
                resultado += financeiro_venda - financeiro_compra

            # Invertou de vendido para comprado
            elif transacoes['Quantidade Acumulada'].iloc[index - 1] < 0 <\
                    transacoes['Quantidade Acumulada'].iloc[index]:
                qntde_cum_anterior = transacoes['Quantidade Acumulada'].iloc[index - 1]
                financeiro_venda = - qntde_cum_anterior * transacoes['Preço Médio'].iloc[index]
                financeiro_compra = - qntde_cum_anterior * transacoes['Preço'].iloc[
                    index - 1]
                resultado += financeiro_venda - financeiro_compra

            # Comprado anteriormente
            elif transacoes['Quantidade Acumulada'].iloc[index-1] > 0:

                # Vendeu.
                if transacoes['Quantidade'].iloc[index] < 0:
                    financeiro_venda = - transacoes['Quantidade'].iloc[index] * transacoes['Preço'].iloc[index]
                    financeiro_compra = - transacoes['Quantidade'].iloc[index] * transacoes['Preço Médio'].iloc[
                        index - 1]
                    resultado += financeiro_venda - financeiro_compra

            # Vendido anteriormente
            elif transacoes['Quantidade Acumulada'].iloc[index-1] < 0:

                # Comprou.
                if transacoes['Quantidade'].iloc[index] > 0:
                    financeiro_venda = transacoes['Quantidade'].iloc[index] * transacoes['Preço'].iloc[index]
                    financeiro_compra = transacoes['Quantidade'].iloc[index] * transacoes['Preço Médio'].iloc[
                        index - 1]
                    resultado += financeiro_venda - financeiro_compra

        return resultado

    def resultado_em_aberto(self, preco_mercado):
        if self.qtde_pos() == 0:
            return 0

        valor_posicao = self.qtde_pos() * self.pmedio()
        valor_mercado = self.qtde_pos() * preco_mercado
        return valor_mercado - valor_posicao

    def eh_long_only(self):
        return self.quantidade_acumulada().min() >= 0


@dataclass
class Gerenciador:

    transacoes: Transacoes = Transacoes()
    proibir_aumentar_pos: bool = False

    def posicao(self) -> Posicao:
        """ Retorna a posição da estratégia. """
        if self.transacoes.qtde_pos() > 0:
            return Posicao.comprado
        if self.transacoes.qtde_pos() == 0:
            return Posicao.zerado
        return Posicao.vendido

    def comprar(self, preco: float, quantidade=1):

        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if self.proibir_aumentar_pos and self.transacoes.qtde_pos() > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de compra "
                                      "e não é permitido pelo gerenciador.")

        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou comprar 0 quantidades')

        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou comprar {quantidade} quantidades.")

        self.transacoes.adicionar(preco=preco, quantidade=quantidade)

    def vender(self, preco: float, quantidade=1):
        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if self.proibir_aumentar_pos and self.transacoes.qtde_pos() > 0:
            raise AumentarPosicaoErro("Você tentou aumentar o tamanho da posição de venda "
                                      "e não é permitido pelo gerenciador.")
        if quantidade == 0:
            raise QuantidadeNulaParaCompraErro('Você tentou vender 0 quantidades')
        if quantidade < 0:
            raise QuantidadeNegativaParaCompraErro(f"Você tentou vender {quantidade} quantidades.")
        self.transacoes.adicionar(preco=preco, quantidade=-quantidade)

    def zerar(self, preco: float):
        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if len(self.transacoes.historico) == 0:
            raise SemPosicaoEmAbertoErro("Não tem como zerar porque não tem posição em aberto.")

        qtde = self.transacoes.qtde_pos()
        self.transacoes.adicionar(preco=preco, quantidade=-qtde)

    def inverter(self, preco: float, quantidade: float = None):
        if preco < 0:
            raise PrecoNegativoErro(f"Você inseriu um preço negativo: {preco}")

        if len(self.transacoes.historico) == 0:
            raise SemTransacoesErro("Não tem como inverter porque não tem transações no histórico.")

        self.zerar(preco)

        if quantidade is None:
            quantidade = self.transacoes.qtde_pos()

        self.transacoes.adicionar(preco=preco, quantidade=-quantidade)

    def obter_transacoes(self):
        return self.transacoes.historico


if __name__ == '__main__':
    ger = Gerenciador(proibir_aumentar_pos=False)
    ger.comprar(preco=2, quantidade=5)
    ger.inverter(preco=3)
    historico = ger.obter_transacoes()
