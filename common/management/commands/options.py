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
from investments.models import Asset
from options.models import Call, Put, Expiration

class Command(BaseCommand):
    help = 'Extrai e atualiza os detalhes das opções do site Opções.net.br'

    expiration_date = "2024-07-19"
    asset_tickers = [
        # Bancos
        "BBDC4", 
        "ITSA4",
        "ITUB4",
        "SANB11",
        # Energia
        'EGIE3',
        'TAEE11',
        'CSAN3',
        # Indústria
        "WEGE3",
        # UNIP6 não tem liquidez
        ]

    def handle(self, *args, **options):
        print("Fetching options details from Opções.net.br")

        for asset_ticker in self.asset_tickers:
            try:
                # Obter e imprimir os detalhes das opções
                options_df = self.get_options_details(asset_ticker)  # Usar self aqui
                self.update_options_in_db(asset_ticker, self.expiration_date, options_df)
                print(options_df)
            except Exception as e:
                print(f"Failed to fetch options for {asset_ticker}: {str(e)}")

    def get_options_details(self, asset_ticker):
        url = f"https://opcoes.net.br/opcoes/bovespa/{asset_ticker}"
        
        # Configuração do ChromeDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(executable_path='/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Carregar a página
        driver.get(url)
        
        # Esperar explicitamente que a página carregue completamente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

        # Pausa adicional para garantir o carregamento completo
        time.sleep(3)

        # Extrair e imprimir o HTML da página
        page_source = driver.page_source

        # Fechar o navegador
        driver.quit()
        
        # Usar BeautifulSoup para parsear o HTML
        soup = BeautifulSoup(page_source, 'html.parser')

        # Encontrar a tabela no HTML
        table = soup.find('table', {'id': 'tblListaOpc'})

        # Extrair os dados da tabela
        data = []
        headers = ['Ticker', 'Tipo', 'F.M.', 'Strike', 'Último', 'Var (%)']
        rows = table.find_all('tr')[1:]  # Ignorar a linha de cabeçalho
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                ticker = cols[0].text.strip()
                tipo = cols[1].text.strip()
                fm = cols[2].text.strip() == '✔'
                try:
                    strike = float(cols[4].text.strip().replace(',', '.')) if cols[4].text.strip() else None
                    ultimo = float(cols[7].text.strip().replace(',', '.')) if cols[7].text.strip() else None
                except ValueError:
                    strike = None
                    ultimo = None
                var_percent = cols[8].text.strip()
                if strike is not None and ultimo is not None:
                    data.append([ticker, tipo, fm, strike, ultimo, var_percent])

        # Criar um DataFrame do pandas
        df = pd.DataFrame(data, columns=headers)
        return df

    def update_options_in_db(self, asset_ticker, expiration_date, options_df):
        asset, created = Asset.objects.get_or_create(ticker=asset_ticker)
        expiration, created = Expiration.objects.get_or_create(date=expiration_date)

        for index, row in options_df.iterrows():
            option_data = {
                'option_ticker': row['Ticker'],
                'has_market_maker': row['F.M.'],
                'asset': asset,
                'expiration': expiration,
                'price_brl': row['Último'],
                'strike_price': row['Strike']
            }

            if row['Tipo'] == 'CALL':
                option, created = Call.objects.update_or_create(
                    option_ticker=row['Ticker'],
                    defaults=option_data
                )
            else:
                option, created = Put.objects.update_or_create(
                    option_ticker=row['Ticker'],
                    defaults=option_data
                )

            if created:
                print(f"Created new option: {option}")
            else:
                print(f"Updated existing option: {option}")

