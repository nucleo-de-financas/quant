from fundo_quant.operacional import Ativo, Ordem
from datetime import datetime
from math import floor


class ExecutorLongOnly:

    def __init__(self, ativo: Ativo,
                 stop_loss: float | None = None,
                 stop_gain: float | None = None):
        self.ativo = ativo
        self.stop_gain = stop_gain
        self.stop_loss = stop_loss

    def _stopar_loss(self, preco: float, horario: datetime):
        if self.ativo.obter_resultado_em_aberto_pct(preco_atual=preco) < -abs(self.stop_loss) \
                and self.ativo.obter_posicao() != 0:
            print(f"Stopando a perda no preco R${round(preco, 2)}.")
            self.ativo.fechar_posicao(preco=preco, horario=horario)

    def _stopar_gain(self, preco: float, horario: datetime):
        if self.ativo.obter_resultado_em_aberto_pct(preco_atual=preco) > abs(self.stop_gain) \
                and self.ativo.obter_posicao() != 0:
            print(f"Stopando o ganho no preco R${round(preco, 2)}.")
            self.ativo.fechar_posicao(preco=preco, horario=horario)

    def _comprar(self, preco: float, horario: datetime):
        """ Compra a quantidade inteira máxima possível. """
        quantidade = floor(self.ativo.saldo/preco)
        print(f"Comprando {quantidade} ao preco R${round(preco, 2)}.")
        self.ativo.comprar(preco=preco, quantidade=quantidade, horario=horario)

    def _vender(self, preco: float, horario: datetime):
        print(f"Fechando posicao a R${round(preco, 2)}.")
        self.ativo.fechar_posicao(preco=preco, horario=horario)

    def executar_ordem(self, ordem: Ordem | None, preco: float, horario: datetime):
        if self.stop_gain is not None:
            self._stopar_gain(preco=preco, horario=horario)
        if self.stop_loss is not None:
            self._stopar_loss(preco=preco, horario=horario)

        if ordem == Ordem.COMPRAR and self.ativo.obter_posicao() == 0:
            self._comprar(preco=preco, horario=horario)
        elif ordem == Ordem.VENDER and self.ativo.obter_posicao() > 0:
            self._vender(preco=preco, horario=horario)
