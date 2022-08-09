from fundo_quant.operacional import AtivoComSaldo, Compra, Venda
from datetime import datetime


def testar_compra():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_posicao() == 5


def testar_venda():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_posicao() == -5


def testar_quantidade_comprada():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_quantidade_comprada() == 5


def testar_quantidade_vendida():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.comprar(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    ativo.vender(preco=10, quantidade=3, horario=datetime.now())
    assert ativo.obter_quantidade_vendida() == 6


def testar_fechar_posicao():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.fechar_posicao(preco=10, horario=datetime.now())
    assert ativo.obter_posicao() == 0


def testar_inverter_posicao():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime.now())
    ativo.inverter_posicao(preco=10, horario=datetime.now())
    assert ativo.obter_posicao() == -2


def testar_operacoes_abertas_v1():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 2))
    assert ativo.obter_operacoes_abertas() == [Compra(preco=10, quantidade=5, horario=datetime(2022, 1, 2))]


def testar_operacoes_abertas_v_2():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 2))
    assert ativo.obter_operacoes_abertas() == [Venda(preco=10, quantidade=5, horario=datetime(2022, 1, 2))]


def testar_operacoes_abertas_v_3():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.inverter_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    assert ativo.obter_operacoes_abertas() == [Compra(preco=10, quantidade=1, horario=datetime(2022, 1, 1))]


def testar_preco_medio_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=20, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 15


def testar_preco_medio_inverter_posicao():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.inverter_posicao(preco=20, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 20


def testar_preco_medio_fechar_posicao():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=20, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 0


def testar_preco_medio_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.vender(preco=20, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.preco_medio() == 15


def testar_saldo_compra():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 80


def testar_saldo_venda():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 120


def testar_saldo_2_compras():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=15, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 50


def testar_saldo_2_vendas():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.vender(preco=15, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 150


def testar_saldo_1_compra_1_venda():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.vender(preco=15, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 110


def testar_saldo_1_venda_1_compra():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=15, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 90


def testar_saldo_fechar_posicao_comprada():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=15, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 110


def testar_saldo_fechar_posicao_vendida():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=15, horario=datetime(2022, 1, 1))
    assert ativo.saldo == 90


def teste_obter_resultado_por_unidade_aberto_compra_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(15) == 5


def teste_obter_resultado_por_unidade_aberto_compra_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(8) == -2


def teste_obter_resultado_por_unidade_aberto_venda_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(15) == -5


def teste_obter_resultado_por_unidade_aberto_venda_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(8) == 2


def teste_obter_resultado_por_unidade_aberto_operacao_comprada_fechada():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.vender(preco=14, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(15) == 0


def teste_obter_resultado_por_unidade_aberto_operacao_vendida_fechada():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=14, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_por_unidade_em_aberto(15) == 0


def teste_obter_valor_de_entrada_da_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_valor_de_entrada_da_posicao() == 20


def teste_obter_valor_de_entrada_da_posicao_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=2, horario=datetime(2022, 1, 1))
    assert ativo.obter_valor_de_entrada_da_posicao() == 20


def teste_obter_resultado_em_aberto_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto(preco_atual=15) == 25


def teste_obter_resultado_em_aberto_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto(preco_atual=8) == 10


def teste_obter_resultado_em_aberto_operacao_comprada():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto(preco_atual=15) == 0


def teste_obter_resultado_em_aberto_operacao_vendida():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto(preco_atual=8) == 0


def teste_obter_patrimonio_liquido_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 90


def teste_obter_patrimonio_liquido_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 110


def teste_obter_patrimonio_operacao_comprada_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.vender(preco=12, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 110


def teste_obter_patrimonio_operacao_comprada_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.vender(preco=8, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 90


def teste_obter_patrimonio_operacao_vendida_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=12, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 90


def teste_obter_patrimonio_operacao_vendida_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.comprar(preco=8, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_patrimonio_liquido(preco_atual=8) == 110


def teste_lucro_acumulado_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=13) == 9


def teste_lucro_acumulado_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=7) == 9


def teste_lucro_acumulado_operacao_comprada_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=12, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=10) == 6


def teste_lucro_acumulado_operacao_comprada_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=8, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=10) == -6


def teste_lucro_acumulado_operacao_vendida_vencedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=8, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=10) == 6


def teste_lucro_acumulado_operacao_vendida_perdedora():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=3, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=12, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado(preco_atual=10) == -6


def teste_lucro_acumulado_percentual_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado_pct(preco_atual=8) == -0.1


def teste_lucro_acumulado_percentual_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.lucro_acumulado_pct(preco_atual=8) == 0.1


def teste_retirar_principal_sem_lucro():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.retirar_capital(10)
    assert ativo.principal == 90 and ativo.saldo == 90


def teste_retirar_principal_com_lucro():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=1, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=12, horario=datetime(2022, 1, 1))
    ativo.retirar_capital(10)
    assert ativo.principal == 90 and ativo.saldo == 92


def teste_retirar_principal_com_prejuizo():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=1, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=8, horario=datetime(2022, 1, 1))
    ativo.retirar_capital(10)
    assert ativo.principal == 90 and ativo.saldo == 88


def teste_adicionar_principal_sem_lucro():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=10, horario=datetime(2022, 1, 1))
    ativo.adicionar_capital(10)
    assert ativo.principal == 110 and ativo.saldo == 110


def teste_adicionar_principal_com_lucro():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=12, horario=datetime(2022, 1, 1))
    ativo.adicionar_capital(10)
    assert ativo.principal == 110 and ativo.saldo == 120


def teste_adicionar_principal_com_prejuizo():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    ativo.fechar_posicao(preco=8, horario=datetime(2022, 1, 1))
    ativo.adicionar_capital(10)
    assert ativo.principal == 110 and ativo.saldo == 100


def teste_obter_resultado_em_aberto_pct_comprado():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.comprar(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto_pct(preco_atual=12) == 0.2


def teste_obter_resultado_em_aberto_pct_vendido():
    ativo = AtivoComSaldo(saldo_inicial=100)
    ativo.vender(preco=10, quantidade=5, horario=datetime(2022, 1, 1))
    assert ativo.obter_resultado_em_aberto_pct(preco_atual=12) == -0.2
