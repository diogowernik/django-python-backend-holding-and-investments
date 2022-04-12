from sqlite3.dbapi2 import Error
import pandas as pd
import yfinance as yf
import datetime as dt
import requests

yf.pdr_override()

def get_yahoo_price(conn, table):
    cursor = conn.cursor()

    app_list = pd.read_sql_query(f"SELECT investments_asset.ticker FROM investments_asset INNER JOIN investments_fii ON investments_asset.id=investments_fii.asset_ptr_id", conn)
    app_list['ticker'] = app_list['ticker'].astype(str) + '.SA' 
    app_list = app_list["ticker"].astype(str).tolist()
    # print(app_list)

    yahoo_df = yf.download(app_list, period="1min")["Adj Close"]
    yahoo_df = yahoo_df.T.reset_index()
    try:
        yahoo_df.columns = ["ticker",  "price"] # , "valor_duplicado" (As vezes 2 as vezes 3)
        yahoo_df['ticker'] = yahoo_df['ticker'].map(lambda x: x.rstrip('.SA'))
        yahoo_df = yahoo_df.set_index('ticker')
        print(yahoo_df)
    except Exception as e:
        print(f' Key Exception - {e}')
        pass
    app_df = pd.read_sql_query(f"SELECT investments_asset.ticker, investments_asset.price FROM investments_asset INNER JOIN investments_fii ON investments_asset.id=investments_fii.asset_ptr_id", conn, index_col="ticker")
    print(app_df)

    for index, row in app_df.iterrows():
        app_df.loc[index]['price'] = yahoo_df.loc[index]['price']
    print(app_df)

    # for index, row in app_df.iterrows():
    #     query = f"Update {table} set price = ? where ticker = ?"
    #     params = (row['price'], index,)
    #     cursor.execute(query, params)    
    # conn.commit()
        
    # # cursor.close()
    # # conn.close()

    # print(f'updated {table} with success')

# def get_derivatives_price(conn, table):
#     cursor = conn.cursor()

#     app_derivatives = pd.read_sql_query(f"SELECT ticker, price FROM {table} ORDER BY ticker", conn, index_col="ticker")
#     # print(app_derivatives)

#     url = 'https://www.tradergrafico.com.br/opcoes/'
#     header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
#     r = requests.get(url, headers=header)
#     tradergrafico_derivatives = pd.read_html(r.text,  decimal=',', thousands='.')[0]
#     tradergrafico_derivatives = tradergrafico_derivatives.drop([0, 2, 3, 5, 6], axis=1).drop([0,1])
#     tradergrafico_derivatives.columns = ["ticker", "price"]
#     tradergrafico_derivatives = tradergrafico_derivatives.set_index('ticker')
#     tradergrafico_derivatives['price'] = tradergrafico_derivatives['price'].str[3:]
#     tradergrafico_derivatives['price'] = tradergrafico_derivatives['price'].str.replace(',', '.')
#     # print(tradergrafico_derivatives.head())


#     for index, row in app_derivatives.iterrows():
#         try:
#             app_derivatives.loc[index]['price'] = tradergrafico_derivatives.loc[index]['price']
#         except Exception as e:
#             # print(f' Key Exception - {e}')
#             pass

#     # print(app_derivatives)

#     for index, row in app_derivatives.iterrows():
#         query = f"Update {table} set price = ? where ticker = ?"
#         params = (row['price'], index,)
#         cursor.execute(query, params)
#     conn.commit()

#     print(f'updated {table} with success')

# def get_criptos_price(conn, table):
#     cursor = conn.cursor()

#     app_criptos_list = pd.read_sql_query(f"SELECT slug FROM {table} ORDER BY slug", conn)
#     app_criptos_list = app_criptos_list["slug"].tolist()
#     app_criptos_list = ','.join(app_criptos_list)
#     # print(app_criptos_list)

#     criptos_price = pd.read_json(f'https://api.coingecko.com/api/v3/simple/price?ids={app_criptos_list}&vs_currencies=brl').T.reset_index()
#     criptos_price.columns = ["slug", "price"]
#     criptos_price = criptos_price.set_index('slug')
#     # print(criptos_price)

#     app_criptos = pd.read_sql_query(f"SELECT slug, price FROM {table} ORDER BY slug", conn, index_col="slug")
#     # print(app_criptos)

#     for index, row in app_criptos.iterrows():
#         try:
#             app_criptos.loc[index]['price'] = criptos_price.loc[index]['price']
#         except Exception as e:
#             # print(f' Key Exception - {e}')
#             pass
        
#     # print(app_criptos)

#     for index, row in app_criptos.iterrows():
#         query = f"Update {table} set price = ? where slug = ?"
#         params = (row['price'], index,)
#         cursor.execute(query, params)
#     conn.commit()

#     print(f'updated {table} with success')

# def update_total_today(conn, asset_table, portfolio_table, asset_id):
#     cursor = conn.cursor()

#     portfolio_assets = pd.read_sql_query(f"SELECT {portfolio_table}.id, {asset_table}.ticker, {portfolio_table}.shares_amount, {asset_table}.price, {portfolio_table}.total_today FROM {asset_table} INNER JOIN {portfolio_table} ON {asset_table}.id={portfolio_table}.{asset_id};", conn , index_col="id")

#     update_total_today = portfolio_assets["price"] * portfolio_assets["shares_amount"]
#     portfolio_assets["total_today"] = update_total_today

#     for index, row in portfolio_assets.iterrows():
#         portfolio_assets.loc[index]['total_today'] = portfolio_assets.loc[index]['total_today']
#         query = f"Update {portfolio_table} set total_today = ? where id = ?"
#         params = (row['total_today'], index,)
#         cursor.execute(query, params)
#     conn.commit()

#     print(f'updated total_today from {portfolio_table} with success')

# def update_fiis_table(conn, field):
#     cursor = conn.cursor()

#     url = 'https://www.fundsexplorer.com.br/ranking'
#     header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
#     r = requests.get(url, headers=header)

#     fiis = pd.read_html(r.text,  decimal=',')[0]
#     fiis= fiis[['Códigodo fundo', 'Setor', 'Dividendo', 'DividendYield', 'DY (6M)Acumulado', 'DY (12M)Acumulado', 'P/VPA', 'QuantidadeAtivos']]
#     fiis.columns = ['ticker', 'setor', 'last_dividend', 'last_yield','six_m_yield', 'twelve_m_yield', 'p_vpa', 'assets']
#     fiis['last_dividend'] = fiis['last_dividend'].str[3:]
#     fiis['last_dividend'] = fiis['last_dividend'].str.replace(',', '.')
#     fiis['last_yield'] = fiis['last_yield'].str.replace(',', '.')
#     fiis['last_yield'] = fiis['last_yield'].str.replace('%', '')
#     fiis['six_m_yield'] = fiis['six_m_yield'].str.replace(',', '.')
#     fiis['six_m_yield'] = fiis['six_m_yield'].str.replace('%', '')
#     fiis['twelve_m_yield'] = fiis['twelve_m_yield'].str.replace(',', '.')
#     fiis['twelve_m_yield'] = fiis['twelve_m_yield'].str.replace('%', '')
#     fiis['p_vpa'] = fiis['p_vpa'] / 100
#     fiis['setor'] = fiis['setor'].str.replace('Títulos e Val. Mob.', 'TVM')
#     fiis['setor'] = fiis['setor'].str.replace('Lajes Corporativas', 'Lajes')
#     fiis = fiis.set_index('ticker')

#     # print(fiis)


#     app_fiis = pd.read_sql_query(f"SELECT ticker, {field} FROM Fiis ORDER BY ticker", conn, index_col="ticker")
#     # print(app_fiis)

#     for index, row in app_fiis.iterrows():
#         try:
#             app_fiis.loc[index][f'{field}'] = fiis.loc[index][f'{field}']
#         except Exception as e:
#             print(f' Key Exception - {e}')
#             pass 

#     for index, row in app_fiis.iterrows():
#         query = f"Update Fiis set {field} = ? where ticker = ?"
#         params = (row[f'{field}'], index,)
#         cursor.execute(query, params)
#     conn.commit()

#     print(f'updated {field} with success')