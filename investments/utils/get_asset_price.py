import requests
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv('API_KEY_ALPHA_VANTAGE')

def fetch_asset_price_from_api(from_currency, to_currency, date):
    # ToDo: Implement this function
    raise NotImplementedError("fetch_asset_price_from_api not yet implemented")

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