from django.db import models
from brokers.models import Broker, Currency
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset, CurrencyHolding
from django.utils import timezone

# Create your models here.


class CurrencyTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=2)
    transaction_type = models.CharField(max_length=50, choices=(('deposit', 'Deposit'), ('withdraw', 'Withdraw')), default='deposit')
    transaction_amount = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)

    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Verifica se o objeto é novo

        # Encontra ou cria um PortfolioInvestment com o Portfolio, Broker e Asset adequados
        asset = CurrencyHolding.objects.get(currency=self.broker.main_currency)
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=asset
        )

        # Recalcular share_average_price_brl e share_average_price_usd
        portfolio_average_price, _ = CurrencyAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

        # Salvar o objeto
        super(CurrencyTransaction, self).save(*args, **kwargs)

        # Recalcular share_average_price_brl e share_average_price_usd
        portfolio_average_price, _ = CurrencyAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

    def delete(self, *args, **kwargs):
        # Antes de deletar o objeto, precisamos ajustar a quantidade de ações em portfolio_investment
        if self.transaction_type == 'deposit':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'withdraw':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

        # Em seguida, recalcule as médias
        portfolio_average_price = CurrencyAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)

        # Agora, podemos deletar o objeto
        super(CurrencyTransaction, self).delete(*args, **kwargs)



class CurrencyAveragePrice(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)

    def recalculate_average(self, start_date, is_new=False, transaction_id=None):
        # Obter todas as transações do portfolio_investment, ordenadas por data
        transactions = CurrencyTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

        # Iniciar total_brl, total_usd, e total_shares com 0
        total_brl = 0
        total_usd = 0
        total_shares = 0

        # Percorrer as transações e recalcular a quantidade total de ações e os totais brl e usd
        for transaction in transactions:
            if transaction.transaction_type == 'deposit':
                total_brl += transaction.transaction_amount * transaction.broker.main_currency.price_brl
                total_usd += transaction.transaction_amount * transaction.broker.main_currency.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'withdraw':
                total_brl -= transaction.transaction_amount * transaction.broker.main_currency.price_brl
                total_usd -= transaction.transaction_amount * transaction.broker.main_currency.price_usd
                total_shares -= transaction.transaction_amount

        # Atualizar os preços médios
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0

        # Atualizar o portfolio_investment correspondente
        portfolio_investment = self.portfolio_investment
        portfolio_investment.share_average_price_brl = self.share_average_price_brl
        portfolio_investment.share_average_price_usd = self.share_average_price_usd
        portfolio_investment.total_cost_brl = total_brl
        portfolio_investment.total_cost_usd = total_usd
        portfolio_investment.shares_amount = total_shares
        portfolio_investment.total_today_brl = total_shares * portfolio_investment.asset.price_brl
        portfolio_investment.total_today_usd = total_shares * portfolio_investment.asset.price_usd
        portfolio_investment.save()

class Income(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} | {self.amount} | {self.broker.main_currency}"

class Expense(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class InternationalCurrencyTransfer(models.Model):
    from_portfolio_investment = models.ForeignKey(PortfolioInvestment, related_name='international_transfer_from', on_delete=models.CASCADE)
    to_portfolio_investment = models.ForeignKey(PortfolioInvestment, related_name='international_transfer_to', on_delete=models.CASCADE)
    transfer_amount_in_source_currency = models.FloatField()  # Valor transferido na moeda de origem
    transfer_date = models.DateField(auto_now_add=True)
    transfer_fee = models.FloatField()
    exchange_rate = models.FloatField()  # Taxa de câmbio usada na transferência

    def save(self, *args, **kwargs):
        if self.pk is not None:  # Verifica se o objeto já existe (ou seja, é uma edição e não uma criação)
            old_transfer = InternationalCurrencyTransfer.objects.get(pk=self.pk)  # Obtém o objeto antigo antes da edição

            # Atualiza o balanço dos portfolio_investments de origem e destino de acordo com a diferença entre os valores antigos e novos
            old_transfer.undo_transfer()
            self.make_transfer()

        else:  # O objeto é novo
            self.make_transfer()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.undo_transfer()
        super().delete(*args, **kwargs)

    def make_transfer(self):
        # Atualiza os balanços dos portfolio_investments de origem e destino
        self.from_portfolio_investment.shares_amount -= self.transfer_amount_in_source_currency
        self.to_portfolio_investment.shares_amount += self.transfer_amount_in_source_currency * self.exchange_rate
        self.from_portfolio_investment.save()
        self.to_portfolio_investment.save()

    def undo_transfer(self):
        # Desfaz a atualização dos balanços dos portfolio_investments de origem e destino
        self.from_portfolio_investment.shares_amount += self.transfer_amount_in_source_currency
        self.to_portfolio_investment.shares_amount -= self.transfer_amount_in_source_currency * self.exchange_rate
        self.from_portfolio_investment.save()
        self.to_portfolio_investment.save()
    
class CurrencyTransfer(models.Model):
    from_portfolio_investment = models.ForeignKey(PortfolioInvestment, related_name='transfer_from', on_delete=models.CASCADE)
    to_portfolio_investment = models.ForeignKey(PortfolioInvestment, related_name='transfer_to', on_delete=models.CASCADE)
    transfer_amount = models.FloatField()
    transfer_date = models.DateField(auto_now_add=True)
    transfer_fee = models.FloatField()

    def save(self, *args, **kwargs):
        if self.pk is not None:  # Verifica se o objeto já existe (ou seja, é uma edição e não uma criação)
            old_transfer = CurrencyTransfer.objects.get(pk=self.pk)  # Obtém o objeto antigo antes da edição

            # Atualiza o balanço dos portfolio_investments de origem e destino de acordo com a diferença entre os valores antigos e novos
            old_transfer.undo_transfer()
            self.make_transfer()

        else:  # O objeto é novo
            self.make_transfer()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.undo_transfer()
        super().delete(*args, **kwargs)

    def make_transfer(self):
        # Atualiza os balanços dos portfolio_investments de origem e destino
        self.from_portfolio_investment.shares_amount -= self.transfer_amount
        self.to_portfolio_investment.shares_amount += self.transfer_amount
        self.from_portfolio_investment.save()
        self.to_portfolio_investment.save()

    def undo_transfer(self):
        # Desfaz a atualização dos balanços dos portfolio_investments de origem e destino
        self.from_portfolio_investment.shares_amount += self.transfer_amount
        self.to_portfolio_investment.shares_amount -= self.transfer_amount
        self.from_portfolio_investment.save()
        self.to_portfolio_investment.save()

class AssetTransaction(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, related_name='asset_transactions')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE) 
    transaction_amount = models.FloatField()
    transaction_type = models.CharField(max_length=50, choices=(('buy', 'Buy'), ('sell', 'Sell')))
    transaction_date = models.DateField(auto_now_add=True)
    asset_price_brl = models.FloatField()  
    asset_price_usd = models.FloatField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Verifica se o objeto é novo

        if self.transaction_type == 'buy':
            # Criar uma transação de moeda correspondente para diminuir o saldo da moeda
            currency_transaction = self.update_currency_balance_on_asset_buy()
            currency_transaction.save()
            
            self.portfolio_investment.shares_amount += self.transaction_amount if is_new else self.transaction_amount - AssetTransaction.objects.get(pk=self.pk).transaction_amount
        elif self.transaction_type == 'sell':
            # Criar uma transação de moeda correspondente para aumentar o saldo da moeda
            currency_transaction = self.update_currency_balance_on_asset_sell()
            currency_transaction.save()

            self.portfolio_investment.shares_amount -= self.transaction_amount if is_new else AssetTransaction.objects.get(pk=self.pk).transaction_amount - self.transaction_amount

        self.portfolio_investment.save()

        super(AssetTransaction, self).save(*args, **kwargs)

        # Recalcular share_average_price_brl e share_average_price_usd
        portfolio_average_price, _ = AssetAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

    def delete(self, *args, **kwargs):
        # Antes de deletar o objeto, precisamos recalcular as médias
        portfolio_average_price = AssetAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date)

        # Atualiza shares_amount no PortfolioInvestment
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount

        self.portfolio_investment.save()

        # Deletar o objeto
        super(AssetTransaction, self).delete(*args, **kwargs)

class AssetAveragePrice(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)

    def calculate_average(self, start_date, is_new=False):
        # Obter todas as transações desde a data de início, ordenadas por data
        transactions = AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment, transaction_date__gte=start_date).order_by('transaction_date')

        # Se a transação não é nova, remova a primeira transação da lista (que é a que estamos editando)
        if not is_new:
            transactions = transactions[1:]

        # Se não há transações, não há nada para recalcular
        if not transactions:
            return

        # Obter a transação imediatamente anterior à data de início
        previous_transaction = AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment, transaction_date__lt=start_date).order_by('transaction_date').last()

        # Começar com a quantidade total de ações e os totais brl e usd da transação anterior
        total_brl = previous_transaction.transaction_amount * previous_transaction.asset_price_brl if previous_transaction else 0
        total_usd = previous_transaction.transaction_amount * previous_transaction.asset_price_usd if previous_transaction else 0
        total_shares = previous_transaction.transaction_amount if previous_transaction else 0

        # Percorrer as transações e recalcular a quantidade total de ações e os totais brl e usd
        for transaction in transactions:
            if transaction.transaction_type == 'buy':
                total_brl += transaction.transaction_amount * transaction.asset_price_brl
                total_usd += transaction.transaction_amount * transaction.asset_price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'sell':
                total_brl -= transaction.transaction_amount * transaction.asset_price_brl
                total_usd -= transaction.transaction_amount * transaction.asset_price_usd
                total_shares -= transaction.transaction_amount

        # Atualizar os preços médios
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0

