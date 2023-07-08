import requests
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv('API_KEY_ALPHA_VANTAGE')

def get_exchange_rate_api(from_currency, to_currency, date):
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

# Para adicionar no futuro, maior controle sobre a taxa de câmbio
# def get_exchange_rate(self, target_currency):
#     if getattr(self.broker.main_currency, 'ticker') == target_currency:
#         return 1
#     try:
#         # Busca na API
#         return get_exchange_rate_api(self.broker.main_currency.ticker, target_currency, self.transaction_date.strftime('%Y-%m-%d'))
#     except Exception as api_exception:
#         # Aqui você pode adicionar uma lógica para registrar os detalhes da exceção em algum lugar, se desejar.
#         # Neste caso, estamos apenas registrando o erro no log
#         logging.error(f'Failed to get exchange rate from API: {api_exception}')

#         try:
#             # Busca no banco de dados e não considera a data
#             return getattr(self.broker.main_currency, f'price_{target_currency.lower()}')
#         except AttributeError as db_exception:
#             # Se algo deu errado ao tentar obter o valor do banco de dados, você pode lidar com isso aqui.
#             # Neste caso, estamos apenas registrando o erro no log
#             logging.error(f'Failed to get exchange rate from DB: {db_exception}')
#             return None