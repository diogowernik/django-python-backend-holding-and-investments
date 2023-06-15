import pandas as pd
import requests
import yfinance as yf

# data fetcher
def fetch_data(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    }
    r = requests.get(url, headers=header)
    return pd.read_html(r.text, decimal=',')[0]

def get_app_df(AppModel): # Ex AppModel = Fii
    queryset = AppModel.objects.values_list("id", "ticker")
    app_df = pd.DataFrame(list(queryset), columns=["id", "ticker"])
    return app_df.set_index('ticker')

def get_yahoo_prices(ticker_list):
    ticker_list = [ticker + '.SA' for ticker in ticker_list]
    df = yf.download(ticker_list, period="1min")["Adj Close"]
    df = df.T.reset_index()
    df['ticker'] = df['ticker'].map(lambda x: x.rstrip('.SA'))
    if df.shape[1] == 3:
        df.columns = ["ticker",  "price_brl", "price_brl2"]
        df["price_brl"] = df["price_brl"].fillna(df["price_brl2"]).round(2)
    else:
        df.columns = ["ticker",  "price_brl"]
        df["price_brl"] = df["price_brl"].round(2)
    return df.set_index('ticker')

def get_usd_today():
    economia_df = pd.read_json('https://economia.awesomeapi.com.br/json/last/USD-BRL').T.reset_index()
    return economia_df['bid'].astype(float)[0]

# data processor

def preprocess_dataframe(df, transformations):
    for column, operation in transformations.items():
        if operation == 'remove_percent':
            df[column] = df[column].str.replace(',', '.')
            df[column] = df[column].str.replace('%', '')
        elif operation == 'divide_by_100':
            # string to float
            df[column] = df[column].astype(float)
            df[column] = df[column] / 100
    return df

def rename_set_index(df, column_map, index_column):
    df = df[list(column_map.keys())]
    df.columns = list(column_map.values())
    return df.set_index(index_column)

def merge_dataframes(df1, df2, on_column):
    return df1.merge(df2, left_on=on_column, right_on=on_column, how='inner')

def update_investment(AppModel, df, fields):
    def update_row(row):
        try:
            investment = AppModel.objects.get(id=row['id'])
            for field in fields:
                setattr(investment, field, row[field])
            investment.save()
        except AppModel.DoesNotExist:
            print(f'{AppModel.__name__} not found')

    df.apply(update_row, axis=1)

def update_ranking(AppModel, field_high_to_low, field_low_to_high):
    """
    This function updates the ranking of an AppModel based on two fields: one that should be ranked from high to low 
    and the other one from low to high.

    Parameters:
    - AppModel: The Django model to be updated. For example: Fii, BrazilianStock, AmericanStock.
    - field_high_to_low: The name of the field that should be ranked from high to low.
    - field_low_to_high: The name of the field that should be ranked from low to high.

    Examples:
    update_ranking(Fii, "twelve_m_yield", "p_vpa") # For Fiis we want high yield and low price/book value.
    update_ranking(BrazilianStock, "roe", "preco_lucro") # For Brazilian Stocks we want high ROE and low P/E.
    update_ranking(AmericanStock, "roic", "earning_yield") # For American Stocks we want high ROIC and high earning yield.

    """
    queryset = AppModel.objects.values_list("id", "ticker", field_high_to_low, field_low_to_high)
    ranking_df = pd.DataFrame(list(queryset), columns=["id", "ticker", field_high_to_low, field_low_to_high])
    ranking_df = ranking_df.set_index('ticker')

    # The field_high_to_low is ranked from high to low.
    ranking_df[field_high_to_low] = pd.to_numeric(ranking_df[field_high_to_low])
    ranking_df[f'ranking_{field_high_to_low}'] = ranking_df[field_high_to_low].rank(ascending=False, method='first')

    # The field_low_to_high is ranked from low to high.
    ranking_df[field_low_to_high] = pd.to_numeric(ranking_df[field_low_to_high])
    ranking_df[f'ranking_{field_low_to_high}'] = ranking_df[field_low_to_high].rank(ascending=True, method='first')

    # We create a new column 'ranking' that is the sum of the ranks of field_high_to_low and field_low_to_high.
    ranking_df['ranking'] = ranking_df[f'ranking_{field_high_to_low}'] + ranking_df[f'ranking_{field_low_to_high}']
    ranking_df = ranking_df.sort_values(by=['ranking'])

    for index, row in ranking_df.iterrows():
        try:
            investment = AppModel.objects.get(id=row['id'])
            investment.ranking = row['ranking']
            investment.save()
        except AppModel.DoesNotExist:
            print(f'{AppModel.__name__} not found')

    # print(f"{AppModel.__name__}'s ranking updated!")

def update_investment_price(AppModel, df, usd_brl_price):
    df['price_usd'] = df['price_brl'] / usd_brl_price
    df['price_usd'] = df['price_usd'].round(2)
    update_investment(AppModel, df, ['price_brl', 'price_usd'])

def update_prices_from_yahoo(AppModel):
    print(f"Updating {AppModel.__name__} price_brl and price_usd from yahoo finance")
    app_df = get_app_df(AppModel)
    ticker_list = app_df.index.tolist()
    yahoo_df = get_yahoo_prices(ticker_list)
    merged_df = merge_dataframes(app_df, yahoo_df, on_column="ticker")
    usd_brl_price = get_usd_today()
    update_investment_price(AppModel, merged_df, usd_brl_price)
    print(f"{AppModel.__name__} price_brl and price_usd updated")
