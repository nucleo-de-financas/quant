from abc import ABC, abstractmethod
import datetime

from fundo_quant.operacional import Sinalizacao, Operacao


class Executor(ABC):

    @abstractmethod
    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int) -> Operacao:
        pass


class ExecutorTF(Executor):

    def executar(self, sinal: Sinalizacao, horario: datetime.datetime, preco: float, qtde: int = 1) -> Operacao:
        if sinal == Sinalizacao.VENDER or sinal.STOP_VENDER or sinal == Sinalizacao.COMPRAR or\
                sinal == Sinalizacao.STOP_COMPRAR:
            return Operacao(horario=horario, quantidade=qtde, preco=preco)
