from enum import Enum
import requests
from datetime import date, datetime
import hashlib
import hmac
import json
from http import client
from urllib.parse import urlencode


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


# Constantes
MB_TAPI_ID = '<user_tapi_id>'
MB_TAPI_SECRET = '15b79f9520dfb321492fd34b1005947c0fa74a3982b25c97ad5e310a8208c0e2'
REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/tapi/v3/'

# Nonce
# Para obter variação de forma simples
# timestamp pode ser utilizado:
#     import time
#     tapi_nonce = str(int(time.time()))
tapi_nonce = 1

# Parâmetros
params = {
    'tapi_method': 'list_orders',
    'tapi_nonce': tapi_nonce,
    'coin_pair': 'BRLBTC'
}
params = urlencode(params)

# Gerar MAC
params_string = REQUEST_PATH + '?' + params
H = hmac.new(bytes(MB_TAPI_SECRET, encoding='utf8'), digestmod=hashlib.sha512)
H.update(params_string.encode('utf-8'))
tapi_mac = H.hexdigest()

# Gerar cabeçalho da requisição
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'TAPI-ID': MB_TAPI_ID,
    'TAPI-MAC': tapi_mac
}

# Realizar requisição POST
try:
    conn = client.HTTPSConnection(REQUEST_HOST)
    conn.request("POST", REQUEST_PATH, params, headers)

    # Print response data to console
    response = conn.getresponse()
    response = response.read()

    response_json = json.loads(response)
    print('status: {}'.format(response_json['status_code']))
    print(json.dumps(response_json, indent=4))
finally:
    if conn:
        conn.close()
class ApiNegociacao:

    url_base = 'https://www.mercadobitcoin.net/tapi/v3/'
    chave =

    @staticmethod
    def enviar(url: str):
        response = requests.request("POST", url, verify=False)
        if response.status_code == 200:
            return response.text

    def _gerar_header(self):
        return {'Content-Type': 'application/x-www-form-urlencoded',
                'TAPI-ID': MB_TAPI_ID,
                'TAPI-MAC': tapi_mac}
