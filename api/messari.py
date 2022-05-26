import pandas as pd
import requests
import json
from typing import Any


class BitCoin:

    def __init__(self):
        self.link = r'https://data.messari.io/api/v1/assets/bitcoin/metrics'

    def _requisitar(self) -> Any:
        resposta = requests.get(self.link)
        if resposta.status_code == 200:
            return json.loads(resposta.text)
        return None

    def obter(self):
        df = pd.DataFrame(self._requisitar()['data']['market_data'])
        return df


if __name__ == "__main__":
    prices = BitCoin().obter()
    print(prices)
