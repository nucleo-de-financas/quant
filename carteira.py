from dataclasses import dataclass


def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])


@dataclass
class Ativo:
    nome: str
    peso: float
    preco_inicial: float
    qtde_inicial: int
    qtde_comprada: int = 0
    preco_compra: float = 0

    def qtde_teorica(self, montante_total: float,  preco_atual: float) -> float:
        return proper_round(montante_total * self.peso / preco_atual, 2)

    def ajuste(self, montante_total: float, preco_atual: float) -> float:
        return self.qtde_teorica(montante_total, preco_atual) - self.qtde_final

    @property
    def qtde_final(self):
        return self.qtde_inicial + self.qtde_comprada

    @property
    def preco_medio(self):
        return (self.qtde_inicial * self.preco_inicial + self.qtde_comprada * self.preco_compra) / self.qtde_final


@dataclass()
class Carteira:

    ativos: list[Ativo]
    aporte: float

    def _verificar_pesos(self):
        soma_peso = round(sum([ativo.peso for ativo in self.ativos]), 4)
        if not soma_peso == 1:
            raise ValueError(f"A soma dos pesos dos ativos da carteira não é igual a 100%. Peso Total: "
                             f"{soma_peso*100}%")

    def __post_init__(self):
        self._verificar_pesos()

    @property
    def montante_investido(self):
        return sum([ativo.preco_medio * ativo.qtde_final for ativo in self.ativos])

    @property
    def aporte_restante(self):
        return self.aporte - sum([ativo.qtde_comprada * ativo.preco_compra for ativo in self.ativos])

    @property
    def montante_total(self):
        return self.montante_investido + self.aporte_restante

    def obter_ajuste(self, precos: list[float]):
        for ativo, preco in zip(self.ativos, precos):
            ajuste = ativo.ajuste(preco_atual=preco, montante_total=self.montante_total)
            if ajuste > 0:
                print(f'Comprar {ajuste} de {ativo.nome}.')
            if ajuste == 0:
                print(f'Manter a quantidade de {ativo.nome}.')
            if ajuste < 0:
                print(f'Vender {ajuste} de {ativo.nome}.')


rbrr11 = Ativo(nome='RBRR11', peso=0.15, preco_inicial=89.43, qtde_inicial=3)
hgru11 = Ativo(nome='HGRU11', peso=0.15, preco_inicial=124, qtde_inicial=2)
vilg11 = Ativo(nome='VILG11', peso=0.15, preco_inicial=107.05, qtde_inicial=2, qtde_comprada=1, preco_compra=107.05)
brco11 = Ativo(nome='BRCO11', peso=0.175, preco_inicial=108.90, qtde_inicial=2, qtde_comprada=1, preco_compra=108.90)
kncr11 = Ativo(nome='KNCR11', peso=0.20, preco_inicial=100.60, qtde_inicial=3)
hgre11 = Ativo(nome='HGRE11', peso=0.175, preco_inicial=138.05, qtde_inicial=2)

p = Carteira(ativos=[rbrr11, hgru11, vilg11, brco11, kncr11, hgre11], aporte=576.79)

precos = [87.15, 123.44, 104.61, 107.95, 99.95, 131.25]
p.obter_ajuste(precos=precos)
