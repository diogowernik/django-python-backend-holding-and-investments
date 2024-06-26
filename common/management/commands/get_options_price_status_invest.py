from django.core.management.base import BaseCommand
from options.models import Option
import requests
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Atualiza o preço em BRL das opções'

    def handle(self, *args, **options):
        print("Updating Options price_brl from Status Invest")

        # Obter todas as opções do banco de dados
        queryset = Option.objects.values_list("id", "option_ticker", "asset__ticker")
        print(queryset)
        
        for option_id, option_ticker, asset_ticker in queryset:
            try:
                # Obter preço atualizado e imprimir os detalhes da opção
                option_details = self.get_updated_price(asset_ticker, option_ticker)
                print(f"Option details for {option_ticker}: {option_details}")
                
                # Atualizar o preço no banco de dados
                Option.objects.filter(id=option_id).update(
                    price_brl=option_details['premium_current']
                )
            except Exception as e:
                print(f"Failed to update option {option_ticker}: {str(e)}")

    def get_updated_price(self, asset_ticker, option_ticker):
        url = f"https://statusinvest.com.br/opcoes/{asset_ticker}/{option_ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrair os detalhes da opção
        top_info = soup.find('div', class_='top-info')
        if not top_info:
            raise ValueError(f"Could not find top-info for option {option_ticker} at {url}")

        # Preço de execução
        strike_price = top_info.find('strong', class_='value').text.strip()

        # Data de vencimento
        expiry_date = top_info.find('span', class_='sub-value').text.strip()

        # Prêmio atual
        premium_current = top_info.find_all('strong', class_='value')[1].text.strip()

        # Prêmio máximo (1 mês)
        premium_max = top_info.find_all('strong', class_='value')[2].text.strip()

        # Prêmio mínimo (1 mês)
        premium_min = top_info.find_all('span', class_='sub-value')[1].text.strip()

        # Cotação atual do ativo
        current_quote = top_info.find_all('strong', class_='value')[3].text.strip()

        option_details = {
            'strike_price': strike_price,
            'expiry_date': expiry_date,
            'premium_current': premium_current,
            'premium_max': premium_max,
            'premium_min': premium_min,
            'current_quote': current_quote
        }

        return option_details
