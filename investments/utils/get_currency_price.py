import requests
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv('API_KEY_ALPHA_VANTAGE')

def get_exchange_rate(from_currency, to_currency, date):
    API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"

    base_url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey={API_KEY}"

    response = requests.get(base_url)
    response_json = response.json()

    # Se a resposta não contiver 'Time Series FX (Daily)', retornar 0
    if 'Time Series FX (Daily)' not in response_json:
        return 0

    # Procurar pela data específica na resposta
    if date not in response_json['Time Series FX (Daily)']:
        return 0

    # Retornar a taxa de câmbio
    exchange_rate = response_json['Time Series FX (Daily)'][date]['4. close']
    return float(exchange_rate)

# Para usar a função
# exchange_rate = get_exchange_rate('USD', 'BRL', '2023-06-01')
# print(exchange_rate)
