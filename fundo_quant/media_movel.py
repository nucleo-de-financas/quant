from coletar_dados.b3.yahoo.api import YahooAPI
from coletar_dados.b3.yahoo.seletores import YahooTickers, YahooPeriodo, YahooIntervalo
from analise_tecnica.calculadoras import CalculadoraMediaMovel, SeletorMediaMovel
from gerenciador import Gerenciador, Posicao

# Coletando Dados # ----------------------------------------------------------------------------------------------------

ativo = YahooAPI(intervalo=YahooIntervalo.DIA_1, ticker=YahooTickers.PETR4, periodo=YahooPeriodo.ANO_10).historico()

# Cálculo da média móvel exponencial p/ curto e longo prazo # ----------------------------------------------------------

janela_curta = 15
janela_longa = 30

curta = CalculadoraMediaMovel(ativo=ativo, media_movel=SeletorMediaMovel.EXPONENCIAL, janela=janela_curta).calcular()
longa = CalculadoraMediaMovel(ativo=ativo, media_movel=SeletorMediaMovel.EXPONENCIAL, janela=janela_longa).calcular()

# Sinal de Compra e Venda # --------------------------------------------------------------------------------------------

# Com o código atual se a média curta > média longa no momento em que importa os dados já vai comprar

gerenciador = Gerenciador(proibir_aumentar_pos=True)

for i in range(len(ativo.fechamento)):

    posicao = gerenciador.posicao()

    # Compra
    if curta[i] > longa[i] and posicao == Posicao.zerado:
        gerenciador.comprar(ativo.fechamento[i])

    # Venda
    if curta[i] < longa[i] and posicao == Posicao.comprado:
        gerenciador.vender(ativo.fechamento[i])

transacoes = gerenciador.obter_transacoes()

# Calculando os retornos # ---------------------------------------------------------------------------------------------


print(f'A operação é Long-Only: {transacoes.eh_long_only()}')
print(f' O retorno total da estratégia foi de R$ {round(transacoes.resultado_fechado(), 2)}')
