import sqlite3
from dataclasses import dataclass
from enum import Enum


def criar_base_de_dados(nome: str) -> sqlite3.Connection:
    return sqlite3.connect(f'{nome}.db')


def criar_um_cursor(base_de_dados: sqlite3.Connection) -> sqlite3.Cursor:
    return base_de_dados.cursor()


@dataclass()
class TiposDados(Enum):
    NULL = 'NULL'
    INTEGER = 'INTEGER'
    REAL = 'REAL'
    TEXT = 'TEXT'
    BLOB = 'BLOB'


@dataclass()
class Coluna:

    nome: str
    tipo: TiposDados

    @property
    def obter_comando(self):
        return f'{self.nome.replace(" ", "_").lower()} {self.tipo.value}'


def criar_texto_colunas(colunas: list[Coluna]):
    texto = ''
    for coluna in colunas:
        texto = f'{texto + coluna.obter_comando},\n'
    return texto[:-2]


def criar_uma_tabela(cursor: sqlite3.Connection, nome_tabela: str, colunas: list[Coluna]):
    return cursor.execute(f"""CREATE TABLE {nome_tabela} ({criar_texto_colunas(colunas)}) """)


def inserir_valor(cursor: sqlite3.Connection, nome_tabela: str, linha: dict):
    return cursor.execute(f"""INSERT INTO {nome_tabela} VALUES ({linha}) """)


x = criar_texto_colunas([Coluna('eae mano', tipo=TiposDados.TEXT), Coluna('eae vei', tipo=TiposDados.TEXT)])

print(x)
