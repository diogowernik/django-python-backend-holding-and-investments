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

class SmartfolioScraper:
    login_url = 'https://smartfolio.meusdividendos.com/login'
    target_url = 'https://smartfolio.meusdividendos.com/dashboard'  # vou acessar manualmente e depois clicar no link para a página desejada

    def __init__(self):
        chrome_options = Options()
        # Remova a linha abaixo para visualizar o navegador durante o login manual
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

    def login(self):
        self.driver.get(self.login_url)

        # Aguardar o usuário realizar o login manualmente
        print("Por favor, realize o login manualmente no navegador e clique no link para a página desejada.")
        input("Depois de concluir o login e navegar até a página alvo, pressione Enter para continuar...")

    def scrape_page(self):
        # Esperar a página carregar completamente
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover"))
        )

        # Pausa adicional para garantir o carregamento completo
        time.sleep(3)

        # Extrair e imprimir o HTML da página
        page_source = self.driver.page_source

        # Usar BeautifulSoup para parsear o HTML
        soup = BeautifulSoup(page_source, 'html.parser')

        # Encontrar a tabela no HTML
        table = soup.find('table', {'class': 'table table-sm table-hover text-body table-striped'})
        data = []

        # Extrair os cabeçalhos da tabela
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]

        # Definir as colunas que queremos manter
        columns_to_keep = ['Data', 'Ativo', 'C/V', 'Qtd', 'Saldo', 'PU', 'PM', 'Desp.', 'Total']

        # Extrair os dados das linhas da tabela
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])

        # Criar um DataFrame do pandas com todas as colunas
        df = pd.DataFrame(data, columns=headers)

        # Filtrar apenas as colunas desejadas
        df_filtered = df[columns_to_keep]
        
        return df_filtered

    def scrape_data(self):
        df_combined = pd.DataFrame()
        
        for page in range(1, 65):  # Total de 64 páginas
            print(f"Scraping page {page}...")
            if page > 1:
                next_page_button = self.driver.find_element(By.XPATH, f"//a[contains(@class, 'page-link') and text()='{page}']")
                self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                next_page_button.click()
                
                # Esperar a página carregar novamente
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover"))
                )
            
            df_page = self.scrape_page()
            df_combined = pd.concat([df_combined, df_page], ignore_index=True)
        
        return df_combined

    def close(self):
        self.driver.quit()

class Command(BaseCommand):
    help = 'Extrai e atualiza os detalhes das opções do site meusdividendos'

    def handle(self, *args, **options):
        scraper = SmartfolioScraper()
        scraper.login()
        data = scraper.scrape_data()
        scraper.close()

        # Salvar os dados em um arquivo CSV
        data.to_csv('meusdividendos_data.csv', index=False)
        print("Dados salvos em meusdividendos_data.csv")
