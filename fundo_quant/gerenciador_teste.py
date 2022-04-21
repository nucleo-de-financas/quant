from fundo_quant.gerenciador import *
from unittest import TestCase, main


class TestesGerenciador(TestCase):
    def setUp(self) -> None:
        self.ger = Gerenciador()

    def testar_comprar_padrao(self):
        qntde_inicial = self.ger.quantidade
        self.ger.comprar()
        self.assertEqual(self.ger.quantidade, qntde_inicial + 1, 'A compra não está aumentando a quantidade')

    def testar_comprar_quantidade_especifica(self):
        self.ger.comprar(quantidade=3)
        self.assertEqual(self.ger.quantidade, 3, f"A compra de quantidade específica 3 deveria dar "
                                                 f"3 e deu {self.ger.quantidade}")

    def testar_comprar_quantidade_negativa(self):
        with self.assertRaises(QuantidadeNegativaParaCompraErro):
            self.ger.comprar(quantidade=-3)

    def testar_comprar_quantidade_zero(self):
        with self.assertRaises(QuantidadeNulaParaCompraErro):
            self.ger.comprar(quantidade=0)

    def testar_comprar_depois_comprar_proibido(self):
        with self.assertRaises(AumentarPosicaoErro):
            self.ger.vender()
            self.ger.vender()

    def testar_vender_depois_vender_proibido(self):
        with self.assertRaises(AumentarPosicaoErro):
            self.ger.comprar()
            self.ger.comprar()

if __name__ == "__main__":
    main()
