import requests
from django.core.management.base import BaseCommand
import pandas as pd
from investments.utils.common import get_app_df, merge_dataframes, get_usd_to_brl_today, update_investment, update_ranking, create_df_from_api
from investments.models import Stocks, Reit
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.

api_key = os.getenv('API_KEY_FINANCIAL_MODELING_PREP')

def get_financial_data(tickers, api_key, app_df):
    
    usd_to_brl = get_usd_to_brl_today()
    print(usd_to_brl)


    balance_df = create_df_from_api('https://financialmodelingprep.com/api/v3/balance-sheet-statement',
                ['ticker', 'total_equity', 'total_assets', 'total_liabil', 'net_debt', 'total_debt', 'cash_and_cash_equivalents'],
                {
                    'net_debt': lambda data: float(data['netDebt']),
                    'total_liabil': lambda data: float(data['totalCurrentLiabilities']),
                    'total_assets': lambda data: float(data['totalAssets']),
                    'total_equity': lambda data: float(data['totalStockholdersEquity']),
                    'total_debt': lambda data: float(data['totalDebt']),
                    'cash_and_cash_equivalents': lambda data: float(data['cashAndCashEquivalents']),
                    }, api_key, tickers)
    print('balance')
    print(balance_df)

    income_df = create_df_from_api('https://financialmodelingprep.com/api/v3/income-statement',
                        ['ticker', 'avg_shares_out', 'ebitda', 'operating_income', 'net_income'],
                        {
                            'net_income': lambda data: float(data['netIncome']),
                            'operating_income': lambda data: float(data['operatingIncome']),
                            'ebitda': lambda data: float(data['ebitda']),
                            'avg_shares_out': lambda data: float(data['weightedAverageShsOut'])
                        
                        }, api_key, tickers)
    print('income')
    print(income_df)

    ratios_df = create_df_from_api('https://financialmodelingprep.com/api/v3/ratios-ttm',
                        ['ticker', 'twelve_m_dividend', 'der', 'ffo'],
                        {'twelve_m_dividend': lambda data: float(data['dividendYielPercentageTTM'])*0.70,
                        'der': lambda data: float(data['debtEquityRatioTTM']),
                        'ffo': lambda data: float(data['operatingCashFlowPerShareTTM'])}, api_key, tickers)
    print('ratios')
    print(ratios_df)

    profile_df = create_df_from_api('https://financialmodelingprep.com/api/v3/profile',
                        ['ticker', 'price', 'bottom_52w', 'top_52w', 'market_cap'],
                        {'price': lambda data: float(data['price']),
                            'bottom_52w': lambda data: float(data['range'].split('-')[0]),
                            'top_52w': lambda data: float(data['range'].split('-')[1]),
                            'market_cap': lambda data: float(data['mktCap'])}, api_key, tickers)
    print('profile')
    print(profile_df)

    temp_df = profile_df[['ticker', 'price']].merge(ratios_df[['ticker', 'ffo']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'total_equity']], on='ticker', how='inner') \
        .merge(income_df[['ticker', 'avg_shares_out']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'total_assets']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'net_debt']], on='ticker', how='inner') \
        .merge(income_df[['ticker', 'ebitda']], on='ticker', how='inner') \
        .merge(profile_df[['ticker', 'market_cap']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'total_debt']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'cash_and_cash_equivalents']], on='ticker', how='inner') \
        .merge(balance_df[['ticker', 'total_liabil']], on='ticker', how='inner') \
        .merge(income_df[['ticker', 'operating_income']], on='ticker', how='inner')

    temp_df['roic'] = temp_df['operating_income'] / (temp_df['total_debt'] + temp_df['total_equity'])
    temp_df['earnings_yield'] = temp_df['operating_income'] / (temp_df['market_cap'] + temp_df['total_debt'] - temp_df['cash_and_cash_equivalents'])
    temp_df['vpa'] = temp_df['total_equity'] / temp_df['avg_shares_out']
    temp_df['p_ffo'] = temp_df['price'] / temp_df['ffo']
    temp_df['p_vpa'] = temp_df['price'] / temp_df['vpa']
    temp_df['ffo_yield'] = (1 / temp_df['p_ffo']) * 100
    temp_df['price_brl'] = temp_df['price'] * usd_to_brl
    temp_df['price_usd'] = temp_df['price']

    # Create the final DataFrame with only necessary columns
    metrics_df = temp_df[['ticker', 'p_ffo', 'p_vpa', 'roic', 'earnings_yield', 'ffo_yield', 'price_brl', 'price_usd']]
    print('metrics')
    print(metrics_df)

    final_df = balance_df.merge(income_df, on='ticker', how='outer') \
                .merge(ratios_df, on='ticker', how='outer') \
                .merge(profile_df, on='ticker', how='outer') \
                .merge(metrics_df, on='ticker', how='outer')
    # final only necessary columns
    final_df = final_df[['ticker', 'ebitda', 'twelve_m_dividend', 'der', 'ffo',
                        'bottom_52w', 'top_52w', 'p_ffo', 'p_vpa', 'roic', 
                        'earnings_yield', 'ffo_yield', 'price_brl', 'price_usd' ]]
    print('final')
    print(final_df)

    # merge final with the original app_df to get the final result
    merged_df = merge_dataframes(app_df, final_df, 'ticker')
    # print('merged')
    # print(merged_df)

    return merged_df







# Exemples of data

# api/v3/profile/O
# {'symbol': 'O', 'price': 61.39, 'beta': 0.80176, 'volAvg': 3654866, 'mktCap': 41329099562, 'lastDiv': 3.07, 'range': '55.5-75.11', 'changes': 0.16, 'companyName': 'Realty Income Corporation', 'currency': 'USD', 'cik': '0000726728', 'isin': 'US7561091049', 'cusip': '756109104', 'exchange': 'New York Stock Exchange', 'exchangeShortName': 'NYSE', 'industry': 'REIT—Retail', 'website': 'https://www.realtyincome.com', 'description': "Realty Income, The Monthly Dividend Company, is an S&P 500 company dedicated to providing stockholders with dependable monthly income. The company is structured as a REIT, and its monthly dividends are supported by the cash flow from over 6,500 real estate properties owned under long-term lease agreements with our commercial clients. To date, the company has declared 608 consecutive common stock monthly dividends throughout its 52-year operating history and increased the dividend 109 times since Realty Income's public listing in 1994 (NYSE: O). The company is a member of the S&P 500 Dividend Aristocrats index. Additional information about the company can be obtained from the corporate website at www.realtyincome.com.", 'ceo': 'Mr. Sumit  Roy', 'sector': 'Real Estate', 'country': 'US', 'fullTimeEmployees': '391', 'phone': '858-284-5000', 'address': '11995 El Camino Real', 'city': 'San Diego', 'state': 'CA', 'zip': '92130', 'dcfDiff': 2.25464, 'dcf': 66.0454, 'image': 'https://financialmodelingprep.com/image-stock/O.png', 'ipoDate': '2012-02-10', 'defaultImage': False, 'isEtf': False, 'isActivelyTrading': True, 'isAdr': False, 'isFund': False}

# api/v3/income-statement/O
# {'date': '2022-12-31', 'symbol': 'O', 'reportedCurrency': 'USD', 'cik': '0000726728', 'fillingDate': '2023-02-22', 'acceptedDate': '2023-02-22 16:07:07', 'calendarYear': '2022', 'period': 'FY', 'revenue': 3343681000, 'costOfRevenue': 226330000, 'grossProfit': 3117351000, 'grossProfitRatio': 0.9323111266, 'researchAndDevelopmentExpenses': 0, 'generalAndAdministrativeExpenses': 138459000, 'sellingAndMarketingExpenses': 0, 'sellingGeneralAndAdministrativeExpenses': 138459000, 'otherExpenses': 1670389000, 'operatingExpenses': 1808848000, 'costAndExpenses': 2035178000, 'interestIncome': 0, 'interestExpense': 445448000, 'depreciationAndAmortization': 1670389000, 'ebitda': 2928636000, 'ebitdaratio': 0.8758718311, 'operatingIncome': 1258247000, 'operatingIncomeRatio': 0.3763059335, 'totalOtherIncomeExpensesNet': -340648000, 'incomeBeforeTax': 917599000, 'incomeBeforeTaxRatio': 0.2744277938, 'incomeTaxExpense': 45183000, 'netIncome': 869408000, 'netIncomeRatio': 0.2600152347, 'eps': 1.42, 'epsdiluted': 1.42, 'weightedAverageShsOut': 611765815, 'weightedAverageShsOutDil': 612180519, 'link': 'https://www.sec.gov/Archives/edgar/data/726728/000072672823000044/0000726728-23-000044-index.htm', 'finalLink': 'https://www.sec.gov/Archives/edgar/data/726728/000072672823000044/o-20221231.htm'}

# api/v3/balance-sheet-statement/O
# {'date': '2022-12-31', 'symbol': 'O', 'reportedCurrency': 'USD', 'cik': '0000726728', 'fillingDate': '2023-02-22', 'acceptedDate': '2023-02-22 16:07:07', 'calendarYear': '2022', 'period': 'FY', 'cashAndCashEquivalents': 171102000, 'shortTermInvestments': 0, 'cashAndShortTermInvestments': 171102000, 'netReceivables': 567963000, 'inventory': 29535000, 'otherCurrentAssets': 71422000, 'totalCurrentAssets': 768600000, 'propertyPlantEquipmentNet': 1071017000, 'goodwill': 3731478000, 'intangibleAssets': 5168366000, 'goodwillAndIntangibleAssets': 8899844000, 'longTermInvestments': 5951000, 'taxAssets': 0, 'otherNonCurrentAssets': 38927680000, 'totalNonCurrentAssets': 48904492000, 'otherAssets': 0, 'totalAssets': 49673092000, 'accountPayables': 399137000, 'shortTermDebt': 2729040000, 'taxPayables': 91573000, 'deferredRevenue': 269645000, 'otherCurrentLiabilities': -103935000, 'totalCurrentLiabilities': 3293887000, 'longTermDebt': 16761129000, 'deferredRevenueNonCurrent': 0, 'deferredTaxLiabilitiesNonCurrent': 0, 'otherNonCurrentLiabilities': 774787000, 'totalNonCurrentLiabilities': 17535916000, 'otherLiabilities': 0, 'capitalLeaseObligations': 1379436000, 'totalLiabilities': 20829803000, 'preferredStock': 0, 'commonStock': 34159509000, 'retainedEarnings': -5493193000, 'accumulatedOtherComprehensiveIncomeLoss': 46833000, 'othertotalStockholdersEquity': 0, 'totalStockholdersEquity': 28713149000, 'totalEquity': 28713149000, 'totalLiabilitiesAndStockholdersEquity': 49673092000, 'minorityInterest': 130140000, 'totalLiabilitiesAndTotalEquity': 49673092000, 'totalInvestments': 5951000, 'totalDebt': 19490169000, 'netDebt': 19319067000, 'link': 'https://www.sec.gov/Archives/edgar/data/726728/000072672823000044/0000726728-23-000044-index.htm', 'finalLink': 'https://www.sec.gov/Archives/edgar/data/726728/000072672823000044/o-20221231.htm'}

# api/v3/ratios/O
#{'dividendYielTTM': 0.048965629581365036, 'dividendYielPercentageTTM': 4.896562958136504, 'peRatioTTM': 45.29977115887851, 'pegRatioTTM': 0.7165600165131693, 'payoutRatioTTM': 2.0919340152281145, 'currentRatioTTM': 0.4243109249092055, 'quickRatioTTM': 0.4114481548015571, 'cashRatioTTM': 0.08659861948195319, 'daysOfSalesOutstandingTTM': 64.73802387253045, 'daysOfInventoryOutstandingTTM': 36.65971608768001, 'operatingCycleTTM': 52.62251649460533, 'daysOfPayablesOutstandingTTM': 633.4130081968897, 'cashConversionCycleTTM': -559.6356022753422, 'grossProfitMarginTTM': 0.9300765901014642, 'operatingProfitMarginTTM': 0.3912223187215811, 'pretaxProfitMarginTTM': 0.27141349662442177, 'netProfitMarginTTM': 0.2571452540079874, 'effectiveTaxRateTTM': 0.04885262178489053, 'returnOnAssetsTTM': 0.01751526052945907, 'returnOnEquityTTM': 0.032243780858576786, 'returnOnCapitalEmployedTTM': 0.02767712488398608, 'netIncomePerEBTTTM': 0.9474298706811232, 'ebtPerEbitTTM': 0.693757701532302, 'ebitPerRevenueTTM': 0.3912223187215811, 'debtRatioTTM': 0.3978089422845596, 'debtEquityRatioTTM': 0.6947788835380001, 'longTermDebtToCapitalizationTTM': 0.39400632402510893, 'totalDebtToCapitalizationTTM': 0.4099525255398439, 'interestCoverageTTM': 2.930525636197342, 'cashFlowToDebtRatioTTM': 0.13683233319111995, 'companyEquityMultiplierTTM': 1.7465139912340453, 'receivablesTurnoverTTM': 5.638108458773583, 'payablesTurnoverTTM': 0.5762432966746771, 'inventoryTurnoverTTM': 9.956432808345264, 'fixedAssetTurnoverTTM': 3.0859704075544165, 'assetTurnoverTTM': 0.06811426715623932, 'operatingCashFlowPerShareTTM': 4.211611447088602, 'freeCashFlowPerShareTTM': 4.211611447088602, 'cashPerShareTTM': 0.2491829970172155, 'operatingCashFlowSalesRatioTTM': 0.7991442616894066, 'freeCashFlowOperatingCashFlowRatioTTM': 1, 'cashFlowCoverageRatiosTTM': 0.13683233319111995, 'shortTermCoverageRatiosTTM': 2.1317346408574727, 'capitalExpenditureCoverageRatioTTM': 0, 'dividendPaidAndCapexCoverageRatioTTM': 1.4855890527431164, 'priceBookValueRatioTTM': 1.3857493347407814, 'priceToBookRatioTTM': 1.3857493347407814, 'priceToSalesRatioTTM': 11.873663411513137, 'priceEarningsRatioTTM': 45.29977115887851, 'priceToFreeCashFlowsRatioTTM': 14.85797243467904, 'priceToOperatingCashFlowsRatioTTM': 14.576368397525751, 'priceCashFlowRatioTTM': 14.576368397525751, 'priceEarningsToGrowthRatioTTM': 1.2864940380673981, 'priceSalesRatioTTM': 11.873663411513137, 'dividendYieldTTM': 0.048965629581365036, 'enterpriseValueMultipleTTM': 19.966301094924876, 'priceFairValueTTM': 1.3857493347407814, 'dividendPerShareTTM': 3.006}
