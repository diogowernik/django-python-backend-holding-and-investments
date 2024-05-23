from django.core.paginator import Paginator
from django.db import transaction
from equity.models import QuotaHistory, PortfolioTotalHistory

class QuotaHistoryService:
    
    @staticmethod
    def create_portfolio_history(portfolio, date):
        return PortfolioTotalHistory.objects.create(portfolio=portfolio, date=date)

    @staticmethod
    def calculate_quota_amounts(quota_history_instance, last_quota_history):
        if quota_history_instance.event_type in ['deposit', 'withdraw']:
            return last_quota_history.quota_amount + (quota_history_instance.value_brl / last_quota_history.quota_price_brl if last_quota_history.quota_price_brl != 0 else 0)
        return last_quota_history.quota_amount

    @staticmethod
    def calculate_prices(quota_amount, total_brl, total_usd):
        if quota_amount and quota_amount != 0:
            quota_price_brl = total_brl / quota_amount
            quota_price_usd = total_usd / quota_amount
        else:
            quota_price_brl = 0
            quota_price_usd = 0
        return quota_price_brl, quota_price_usd

    @staticmethod
    def calculate_percentage_change(last_quota_price_brl, new_quota_price_brl):
        if last_quota_price_brl and last_quota_price_brl != 0:
            return (new_quota_price_brl / last_quota_price_brl) - 1
        return 0

    @staticmethod
    def handle_first_entry(quota_history_instance):
        quota_history_instance.total_brl = quota_history_instance.value_brl
        quota_history_instance.total_usd = quota_history_instance.value_usd
        quota_history_instance.quota_amount = quota_history_instance.value_brl
        quota_history_instance.quota_price_brl = 1
        quota_history_instance.quota_price_usd = quota_history_instance.value_usd / quota_history_instance.value_brl if quota_history_instance.value_brl != 0 else 0
        quota_history_instance.percentage_change = 0

    @staticmethod
    def create_quota_history(quota_history_instance, portfolio_history):
        quota_history_instance.total_brl = portfolio_history.total_brl  
        quota_history_instance.total_usd = portfolio_history.total_usd  
        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=quota_history_instance.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=quota_history_instance.date).first()

        if last_quota_history:
            quota_history_instance.quota_amount = calculate_quota_amounts(quota_history_instance, last_quota_history)
            quota_history_instance.quota_price_brl, quota_history_instance.quota_price_usd = calculate_prices(quota_history_instance.quota_amount, quota_history_instance.total_brl, quota_history_instance.total_usd)
            quota_history_instance.percentage_change = calculate_percentage_change(last_quota_history.quota_price_brl, quota_history_instance.quota_price_brl)
        else:
            if quota_history_instance.event_type == 'deposit':
                handle_first_entry(quota_history_instance)
            else:
                raise Exception(f'Não há histórico de cotas para este portfolio, por isso você não pode realizar a operação: {quota_history_instance.event_type}.')

    @staticmethod
    def reprocess_subsequent_entries(portfolio, from_date):
        affected_entries = QuotaHistory.objects.filter(portfolio=portfolio, date__gte=from_date).order_by('date')
        PortfolioTotalHistory.objects.filter(portfolio=portfolio, date__gte=from_date).delete()

        paginator = Paginator(affected_entries, 100)  # Processa 100 registros por vez para eficiência
        for page_number in range(1, paginator.num_pages + 1):
            with transaction.atomic():
                for entry in paginator.page(page_number).object_list:
                    portfolio_history = create_portfolio_history(entry.portfolio, entry.date)
                    update_quota_history(entry, portfolio_history)
                    entry.save()  # Salva as mudanças após atualizações

    @staticmethod
    def update_quota_history(entry, portfolio_history):
        """
        Atualiza uma entrada de QuotaHistory com base nos dados recalculados de PortfolioTotalHistory.
        Esta função assume que 'entry' é uma instância existente de QuotaHistory que já está salva no banco de dados.

        Args:
        entry (QuotaHistory): A instância de QuotaHistory a ser atualizada.
        portfolio_history (PortfolioTotalHistory): Os dados atualizados do portfolio que impactam esta entrada.
        """
        entry.total_brl = portfolio_history.total_brl
        entry.total_usd = portfolio_history.total_usd

        # Rebuscar a última entrada histórica válida anterior à entrada atual
        last_quota_history = QuotaHistory.objects.filter(portfolio=entry.portfolio, date__lt=entry.date).order_by('-date').first()

        if last_quota_history:
            entry.quota_amount = calculate_quota_amounts(entry, last_quota_history)
            entry.quota_price_brl, entry.quota_price_usd = calculate_prices(entry.quota_amount, entry.total_brl, entry.total_usd)
            entry.percentage_change = calculate_percentage_change(last_quota_history.quota_price_brl, entry.quota_price_brl)
        else:
            # Se não houver nenhuma entrada anterior, trata como primeira entrada
            handle_first_entry(entry)


## para atualizar os models no futuro.

# from django.db import models, transaction
# from services.quota_history_service import QuotaHistoryService

# class QuotaHistory(models.Model):
#     # Definição dos campos conforme já definido

#     def save(self, *args, **kwargs):
#         with transaction.atomic():  # Garante que as operações sejam atômicas
#             if not self.pk:  # Verifica se é uma nova instância
#                 last_entry = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date').first()
#                 if last_entry and last_entry.date > self.date:  # Novo registro é fora de ordem
#                     QuotaHistoryService.reprocess_subsequent_entries(self.portfolio, self.date)
#             super().save(*args, **kwargs)
