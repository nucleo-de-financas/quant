import pandas as pd
from fundo_quant.estrategia import Estrategia
from fundo_quant.executores import ExecutorLongOnly


class WalkForward:

    def __init__(self, estrategia: Estrategia,
                 ex: ExecutorLongOnly,
                 precos: pd.Series,
                 atraso: int = 0):
        self.estrategia = estrategia
        self.ex = ex
        self.precos = precos.sort_index().shift(atraso)

    def obter_serie_retorno(self):
        dia = 0
        pls = []
        for horario in self.precos.index:
            preco = self.precos.loc[horario]
            self.ex.executar_ordem(ordem=self.estrategia.obter_ordem(), preco=preco, horario=horario)
            self.estrategia.setar_dia(dia)
            pls.append(self.ex.ativo.lucro_acumulado_pct(preco_atual=preco))
            dia += 1
        return pd.Series(pls, index=self.precos.index)
