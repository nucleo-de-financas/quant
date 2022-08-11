from fundo_quant.fundos import fundo_cripto_v1
from api.coinmarketcap import Moeda


def main():
    fundo_cripto_v1(Moeda.BITCOIN)


main()
