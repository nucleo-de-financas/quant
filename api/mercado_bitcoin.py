from enum import Enum
import requests
from datetime import date, datetime


class Moedas(Enum):
    BITCOIN = 'BTC'


class ApiDados:
    url_base = fr'https://www.mercadobitcoin.net/api'

    @staticmethod
    def obter(url: str):
        response = requests.request("GET", url, verify=False)
        if response.status_code == 200:
            return response.text

    def obter_ult_24_horas(self, moeda: Moedas):
        return self.obter(f'{self.url_base}/{moeda.value}/ticker')

    def obter_book(self, moeda: Moedas):
        return self.obter(f'{self.url_base}/{moeda.value}/orderbook')

    def obter_historico(self, moeda: Moedas,
                        desde: datetime | date | None = None,
                        ate: datetime | date | None = None):
        url = f'{self.url_base}/{moeda.value}/trades'
        print(url)
        if desde is not None:
            url = f'{url}/{desde.timestamp():.0f}'
            if ate is not None:
                url = f'{url}/{ate.timestamp():.0f}'
        return self.obter(url)

    def obter_resumo_dia_especifico(self, moeda: Moedas, data: date | datetime):
        url = f'{self.url_base}/{moeda.value}/day-summary/{data.year}/{data.month}/{data.day}'
        return self.obter(url)

