import requests
from dotenv import load_dotenv
import os
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


def fetch_asset_price_from_yahoo(asset, currency, date):
    # Adicionar '.SA' se a moeda for BRL
    asset = f"{asset}.SA" if currency.upper() == 'BRL' else asset

    # Formatar o símbolo da criptomoeda corretamente, se necessário
    known_cryptos = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH']  # Adicione qualquer outra criptomoeda que você quer rastrear aqui
    asset = f"{asset}-{currency}" if asset in known_cryptos else asset

    # Baixar o histórico de preços do ativo para o intervalo de datas especificado
    data = yf.download(asset, start=date, end=date)

    # Verificar se os dados foram retornados
    if data.empty:
        raise Exception(f"No price data found for asset {asset} on date {date}.")

    # Retornar o preço de fechamento no último dia de negociação anterior à data especificada
    return data['Close'][-1]

def fetch_asset_price_from_yahoo_currency(asset, currency, date):
    # Fetch asset price
    asset_price = fetch_asset_price_from_yahoo(asset, currency, date)

    # Fetch currency price
    currency_price = fetch_currency_price_from_api('USD', currency, date) if currency.upper() != 'USD' else 1.0

    # Convert asset price to desired currency
    converted_asset_price = asset_price * currency_price

    return converted_asset_price


def fetch_currency_exchange_rate(from_currency, to_currency, date):
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


def fetch_raw_asset_price(asset, currency, date):
    # Adicionar '.SA' se a moeda for BRL
    asset = f"{asset}.SA" if currency.upper() == 'BRL' else asset

    # Formatar o símbolo da criptomoeda corretamente, se necessário
    known_cryptos = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH']  # Adicione qualquer outra criptomoeda que você quer rastrear aqui
    asset = f"{asset}-{currency}" if asset in known_cryptos else asset

    # Baixar o histórico de preços do ativo para o intervalo de datas especificado
    data = yf.download(asset, start=date, end=date)

    # Verificar se os dados foram retornados
    if data.empty:
        raise Exception(f"No price data found for asset {asset} on date {date}.")

    # Retornar o preço de fechamento no último dia de negociação anterior à data especificada
    return data['Close'][-1]


def fetch_asset_price_adjusted_by_currency(asset, currency, date):
    # Fetch asset price
    raw_asset_price = fetch_raw_asset_price(asset, currency, date)

    # Fetch currency price
    exchange_rate = fetch_currency_exchange_rate('USD', currency, date) if currency.upper() != 'USD' else 1.0

    # Convert asset price to desired currency
    adjusted_asset_price = raw_asset_price * exchange_rate

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


