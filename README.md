# Quant
Biblioteca Python produzida pelos membros da área Quantitativa do Núcleo de Finanças Insper.

# Contribuintes
- Felipe Lima
- Fernando Camillo

# Guia do Usuário

Para usar é necessário requisitar os dados na internet através das API's predefinidas
na pasta 'coletar_dados'. Com isso, é possível usar os métodos
definidos na calculadora localizada na pasta 'analise_tecnica'.

# Calculadora

## Média Móvel

Todas as médias móveis têm como argumento o tamanho da 'janela', passada já
na criação da classe da Calculadora. Além disso, é necessário utilizar as opções
predefinidas pela 'class' SeletoresMediaMovel. 

###SeletoresMediaMovel

    ARNAUD_LEGOUX
    DUPLA_EXPONENCIAL
    EXPONENCIAL
    FIBONACCI_PONDERADA 
    GAIN_HIGH_LOW
    HIGH_LOW
    HIGH_LOW_CLOSE
    HULL
    HOLT_WINTER
    ICHIMOKU
    JURIK
    KAUFMAN_ADAPTIVE
    LINEAR_REGRESSION
    MC_GINLEY_DYNAMIC
    MIDPOINT
    MIDPRICE
    OPEN_HIGH_CLOSE_LOW_AVERAGE
    PASCAL_PONDERADA
    WILDER
    SENO_MM
    SIMPLES
    EHLER_SMOOTH_FILTER
    SUPERTREND
    SIMETRICAMENTE_PONDERADA
    T3
    TRIPLO_EXPONENCIAL
    MOVIMENTO_TRIANGULAR
    VARIABLE_INDEX_DYNAMIC
    VWAP
    FECHAMENTO_PONDERADA
    PONDERADA
    ZERO_LAG

Depois, chama-se o método calcular(). O retorno são pd.Series individuais.

## Exemplo

Coletando dados de um em um dia (YahooIntervalo), durante o total de um ano (YahooPeriodo) da Petrobras (YahoooTicker), por meio da API da yahoo, chamando-se o histórico.

Depois, foi salvo na variável PETR4.

    PETR4 = YahooAPI(YahooIntervalo.DIA_1, YahooPeriodo.ANO_1, YahooTickers.PETR4).historico()

Depois, são calculadas todas as médias móveis usando a Class CalculadoraMediaMovel e o método calcular.

    print(CalculadoraMediaMovel(ativo=PETR4,
                                media_movel=[seletor for seletor in SeletorMediaMovel], janela=10).calcular())
