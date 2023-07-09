# import requests
from dotenv import load_dotenv
# import os
load_dotenv()  # take environment variables from .env.
import yfinance as yf
from datetime import datetime

def fetch_currency_price_from_api(from_currency, to_currency, date):
    # Date should be in 'YYYY-MM-DD' format
    if isinstance(date, datetime):
        date = date.strftime('%Y-%m-%d')

    pair = f"{from_currency}{to_currency}=X"
    ticker = yf.Ticker(pair)

    try:
        # Get historical market data
        hist = ticker.history(start=date, end=date)
    except ValueError as ve:
        raise Exception(f"Failed to fetch data for date {date}. Exception: {ve}")

    if hist.empty:
        raise Exception(f"No exchange rate data available for {pair} on date {date}.")

    # Get the close price
    close_price = hist['Close'].values[0]

    return float(close_price)

def fetch_raw_asset_price(asset, asset_currency, target_currency, date):
    # Adicionar '.SA' se a moeda do ativo for BRL
    if asset_currency.upper() == 'BRL':
        asset += ".SA"
        original_currency = 'BRL'  # preço originalmente em BRL
    else:
        original_currency = 'USD'  # preço originalmente em USD
        known_cryptos = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH']
        asset = f"{asset}-{target_currency}" if asset in known_cryptos else asset

    data = yf.download(asset, start=date, end=date)

    if data.empty:
        raise Exception(f"No price data found for asset {asset} on date {date}.")

    return data['Close'][-1], original_currency

def fetch_asset_price_from_api(asset, asset_currency, target_currency, date):
    # Fetch the raw asset price in its original currency
    raw_asset_price, original_currency = fetch_raw_asset_price(asset, asset_currency, target_currency, date)

    # If the original currency is already the target currency, return the original price
    if original_currency.upper() == target_currency.upper():
        return raw_asset_price

    # If the original and target currencies are different, convert the price to the target currency
    else:
        # Fetch the exchange rate for the specified date
        exchange_rate = fetch_currency_price_from_api(original_currency, target_currency, date)
        
        # Convert the asset price to the target currency by dividing the original price by the exchange rate.
        # This is the change - we no longer make a distinction between BRL to USD conversion and all other conversions.
        # The exchange rate should always be used to divide the original price, no matter which currencies are involved.
        adjusted_asset_price = raw_asset_price * exchange_rate if exchange_rate else None

        return adjusted_asset_price












# Parei de usar devido a limitações de uso gratuito
# API_KEY = os.getenv('API_KEY_ALPHA_VANTAGE')

# def fetch_currency_price_from_api(from_currency, to_currency, date):
#     # Obs: Essa API tem limitações de uso gratuito, por exemplo, 5 chamadas de API por minuto e 500 chamadas por dia.
#     # pensar outra solução para o futuro
#     API_KEY = "API_KEY_ALPHA_VANTAGE"
#     # API_KEY = "WRONG_API_KEY" # Para testar a exceção

#     base_url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey={API_KEY}"

#     response = requests.get(base_url)
    
#     try:
#         response_json = response.json()
#     except ValueError:
#         raise Exception("API response is not valid JSON.")

#     # Se a resposta não contiver 'Time Series FX (Daily)', lançar uma exceção
#     if 'Time Series FX (Daily)' not in response_json:
#         raise Exception("API response does not contain 'Time Series FX (Daily)'.")

#     # Procurar pela data específica na resposta
#     if date not in response_json['Time Series FX (Daily)']:
#         raise Exception(f"No exchange rate found for date {date}.")

#     # Verificar se '4. close' está presente nos dados da taxa de câmbio
#     if '4. close' not in response_json['Time Series FX (Daily)'][date]:
#         raise Exception("API response does not contain '4. close' in exchange rate data.")

#     # Retornar a taxa de câmbio
#     exchange_rate = response_json['Time Series FX (Daily)'][date]['4. close']
#     return float(exchange_rate)


