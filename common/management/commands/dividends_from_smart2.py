# scraper_dividends.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from django.core.management.base import BaseCommand
import requests
from datetime import datetime

class SmartfolioDividendScraper:
    login_url = 'https://smartfolio.meusdividendos.com/login'
    # You can adjust the target_url to directly navigate to the dividends page if possible
    target_url = 'https://smartfolio.meusdividendos.com/dashboard'  # Replace with the actual dividends page URL

    def __init__(self):
        chrome_options = Options()
        # Remove the line below to visualize the browser during manual login
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

    def login(self):
        self.driver.get(self.login_url)

        # Wait for the user to manually log in and navigate to the target page
        print("Please log in manually in the browser and navigate to the dividends page.")
        input("After completing the login and navigating to the target page, press Enter to continue...")

    def scrape_page(self):
        # Wait for the table to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover"))
        )

        # Additional pause to ensure complete loading
        time.sleep(3)

        # Get the page source
        page_source = self.driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the table in the HTML
        table = soup.find('table', {'class': 'table table-sm table-hover text-body table-striped'})
        data = []

        # Extract the table headers
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]

        # Define the columns we want to keep (adjust according to the actual headers)
        columns_to_keep = ['Data-com', 'Pagamento', 'Ativo', 'Tipo', 'Valor', 'PM', 'Yield', 'Saldo', 'Total']

        # Extract data from table rows
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])

        # Create a pandas DataFrame with all columns
        df = pd.DataFrame(data, columns=headers)

        # Filter only the desired columns
        df_filtered = df[columns_to_keep]

        return df_filtered

    def scrape_data(self):
        df_combined = pd.DataFrame()

        # Adjust the number of pages according to the actual pagination
        page = 1
        while True:
            print(f"Scraping page {page}...")
            if page > 1:
                # Click the next page button
                next_page_button = self.driver.find_element(By.XPATH, f"//a[contains(@class, 'page-link') and text()='{page}']")
                self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                next_page_button.click()

                # Wait for the page to reload
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover"))
                )

                time.sleep(3)  # Additional wait to ensure page load

            df_page = self.scrape_page()
            df_combined = pd.concat([df_combined, df_page], ignore_index=True)

            # Check if there's a next page
            try:
                self.driver.find_element(By.XPATH, f"//a[contains(@class, 'page-link') and text()='{page + 1}']")
                page += 1
            except:
                break  # No more pages

        return df_combined

    def close(self):
        self.driver.quit()

def get_usd_brl_exchange_rate(date_str):
    """
    Fetches the USD to BRL exchange rate for a given date.
    Date format: 'YYYY-MM-DD'
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
        url = f'https://economia.awesomeapi.com.br/json/daily/USD-BRL/?start_date={date}&end_date={date}'
        response = requests.get(url)
        data = response.json()
        if data:
            return float(data[0]['bid'])
        else:
            # Fallback to current exchange rate if historical data is not available
            current_rate = requests.get('https://economia.awesomeapi.com.br/json/last/USD-BRL').json()
            return float(current_rate['USDBRL']['bid'])
    except Exception as e:
        print(f"Error fetching exchange rate for {date_str}: {e}")
        return None

class Command(BaseCommand):
    help = 'Scrapes dividend data from meusdividendos and saves to CSV'

    def handle(self, *args, **options):
        scraper = SmartfolioDividendScraper()
        scraper.login()
        data = scraper.scrape_data()
        scraper.close()

        # Process the data to match the desired CSV format
        # Rename columns for clarity
        data.rename(columns={
            'Data-com': 'record_date',
            'Pagamento': 'pay_date',
            'Ativo': 'asset_ticker',
            'Tipo': 'category',
            'Valor': 'value_per_share',
            'PM': 'average_price',
            'Yield': 'yield',
            'Saldo': 'shares_amount',
            'Total': 'total_dividend'
        }, inplace=True)

        # Convert dates to 'YYYY-MM-DD' format
        data['record_date'] = pd.to_datetime(data['record_date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        data['pay_date'] = pd.to_datetime(data['pay_date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

        # Clean numeric columns
        numeric_columns = ['value_per_share', 'average_price', 'shares_amount', 'total_dividend']
        for col in numeric_columns:
            data[col] = data[col].str.replace('.', '').str.replace(',', '.').str.replace('usd', '').str.strip()
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # Identify if the dividend is in USD or BRL based on 'value_per_share' and 'total_dividend' columns
        data['currency'] = data.apply(lambda row: 'USD' if 'usd' in str(row['total_dividend']).lower() else 'BRL', axis=1)

        # Remove 'usd' from 'total_dividend' if present
        data['total_dividend'] = data['total_dividend'].astype(str).str.replace('usd', '').str.strip()
        data['total_dividend'] = pd.to_numeric(data['total_dividend'], errors='coerce')

        # Get USD-BRL exchange rate for each pay_date
        data['usd_on_pay_date'] = data['pay_date'].apply(get_usd_brl_exchange_rate)

        # Calculate USD and BRL values
        data['value_per_share_usd'] = data.apply(lambda row: row['value_per_share'] if row['currency'] == 'USD' else round(row['value_per_share'] / row['usd_on_pay_date'], 4), axis=1)
        data['value_per_share_brl'] = data.apply(lambda row: row['value_per_share'] if row['currency'] == 'BRL' else round(row['value_per_share'] * row['usd_on_pay_date'], 4), axis=1)
        data['total_dividend_usd'] = data.apply(lambda row: row['total_dividend'] if row['currency'] == 'USD' else round(row['total_dividend'] / row['usd_on_pay_date'], 4), axis=1)
        data['total_dividend_brl'] = data.apply(lambda row: row['total_dividend'] if row['currency'] == 'BRL' else round(row['total_dividend'] * row['usd_on_pay_date'], 4), axis=1)
        data['average_price_usd'] = data.apply(lambda row: row['average_price'] if row['currency'] == 'USD' else round(row['average_price'] / row['usd_on_pay_date'], 4), axis=1)
        data['average_price_brl'] = data.apply(lambda row: row['average_price'] if row['currency'] == 'BRL' else round(row['average_price'] * row['usd_on_pay_date'], 4), axis=1)

        # Select and reorder the columns as per the desired CSV format
        final_data = data[[
            'asset_ticker', 'category', 'record_date', 'pay_date', 'shares_amount',
            'value_per_share_brl', 'total_dividend_brl', 'average_price_brl',
            'usd_on_pay_date', 'value_per_share_usd', 'total_dividend_usd', 'average_price_usd'
        ]]

        # Save the data to a CSV file
        final_data.to_csv('dividends_2024.csv', index=False)
        print("Dividend data saved to dividends_2024.csv")
