import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
from coletar_dados.b3.yahoo.api import YahooAPI
from coletar_dados.b3.yahoo.seletores import YahooTickers, YahooPeriodo, YahooIntervalo

# Coletando Dados # ----------------------------------------------------------------------------------------------------

data = YahooAPI(intervalo=YahooIntervalo.DIA_1, ticker=YahooTickers.PETR4, periodo=YahooPeriodo.ANO_10).historico()

data = data[['Close']]

# Cálculo da média móvel exponencial p/ curto e longo prazo # ----------------------------------------------------------

Periodo_curto = 15
Periodo_Longo = 30

""" Usar nossa library. """
data['MMEC'] = round(ta.ema(data.iloc[:, 0], Periodo_curto), 4)  # Média móvel exponencial de curto
data['MMEL'] = round(ta.ema(data.iloc[:, 0], Periodo_Longo), 4)  # Média móvel exponencial de longo

# Criando listas para plotar no gráfico
""" Usar método to_list."""
Lista_EMA_curto = list(data['MMEC'])
Lista_EMA_longo = list(data['MMEL'])
Lista_PRECO_fechamento = list(data['Close'])


# Sinal de Compra e Venda # --------------------------------------------------------------------------------------------

# Com o código atual se a MMEC > MMEL no momento em que importa os dados já vai comprar

Lista_preco_compras = []  # Lista que vai armazenar os preços de compra
Lista_preco_vendas = []  # Lista que vaio armazenar os preços de venda


class Posicao:

    def __init__(self):
        self.status: int = 0

    def comprar(self):
        self.status = 1

    def vender(self):
        self.status = 0

    def esta_comprado(self):
        return self.status == 1


posicao = Posicao()


for i in range(len(Lista_PRECO_fechamento)):
    media_curto_dia = data['MMEC'][i]  # Valor da média móvel de curto no dia i
    media_longo_dia = data['MMEL'][i]  # Valor da média móvel de longo no dia i

    if media_curto_dia >= media_longo_dia:  # Compro
        if not posicao.esta_comprado():
            Preco_compra = data['Close'][i]
            Lista_preco_compras.append(Preco_compra)
            posicao.comprar()
    else:  # Vendo
        if posicao.esta_comprado():
            Preco_venda = data['Close'][i]
            Lista_preco_vendas.append(Preco_venda)
            posicao.vender()

print('Preços de Compras', Lista_preco_compras)
print('Preços de Vendas', Lista_preco_vendas)


# Calculando os retornos # ---------------------------------------------------------------------------------------------

# Retorno Absoluto em cada Compra e Venda #
Lista_retornos_compravenda = []  # Armazena o retorno absoluto (número) em cada Compra e Venda

""" Existe a possibilidade de as listas terem tamanhos diferentes? Isso quebraria seu código. Talvez,
exista uma maneira melhor de agregar duas listas. Tuples? Dicionario? Classes? """
for i in range(len(Lista_preco_vendas)):
    Retornos_compravenda = Lista_preco_vendas[i] - Lista_preco_compras[i]
    Lista_retornos_compravenda.append(Retornos_compravenda)

print(Lista_retornos_compravenda)

# Retorno em % em cada operação de Compra e Venda #
Lista_retornos = []  # Armazena os retornos em porcentagem por operação de Compra e Venda

for i in range(len(Lista_preco_vendas)):
    Retorno_porcentagem = round(((Lista_preco_vendas[i] - Lista_preco_compras[i]) / Lista_preco_compras[i]), 4)
    Lista_retornos.append(Retorno_porcentagem)

print(Lista_retornos)

# Investindo 100 reais na estratégia #
Investimento_100 = np.zeros(len(Lista_retornos)+1)
Investimento_100[0] = 100

for i in range(len(Lista_retornos)):
    Investimento_100[i+1] = (1+Lista_retornos[i])*Investimento_100[i]

Lista_Investimento_100 = list(Investimento_100)
print('Retornos investindo R$100 na estratégia', Lista_Investimento_100)


# Calculo de outros indicadores # --------------------------------------------------------------------------------------

# Sharpe #
# Volatilidade #

# Retorno no período #
Retorno_no_periodo = Lista_Investimento_100[-1] - Investimento_100[0]
print('Retorno no período: ', round(Retorno_no_periodo, 3), '%')

# Quantidade de operações #
Quantidade_de_operacoes = len(Lista_preco_compras) + len(Lista_preco_vendas)
print('Quantidade de Operações', Quantidade_de_operacoes)


# Criando Gráficos # ---------------------------------------------------------------------------------------------------

# Gráfico do Ativo e das médias móveis # ##### Colocar os pontos de compra e venda #####
plt.plot(Lista_PRECO_fechamento, label='Ativo', color='black', lw=1.5)
plt.plot(Lista_EMA_curto, label='MM Curto', color='r', lw=1.0)
plt.plot(Lista_EMA_longo, label='MM Longo', color='b', lw=1.0)
plt.xlabel('Dias')
plt.ylabel('Preço Ativo')
plt.legend()
plt.show()

# Gráfico investindo 100 reais #
plt.plot(Lista_Investimento_100, color='orange', lw=1.8, marker='o')
plt.xlabel('Dinheiro')
plt.ylabel('Operações concluidas')  # Comprou e vendeu
plt.title('Retorno acumulado da estratégia')
# plt.annotate() # Anotar o valor em cada período no gráfico
plt.grid()
plt.show()
