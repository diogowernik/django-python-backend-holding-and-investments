from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset, CurrencyHolding
from django.utils import timezone
from investments.utils.get_currency_price import get_exchange_rate

# Deposito e Saque de dinheiro (Mesma moeda do broker)
class CurrencyTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=2)
    transaction_type = models.CharField(max_length=50, choices=(('deposit', 'Deposit'), ('withdraw', 'Withdraw')), default='deposit')
    transaction_amount = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    price_brl = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)

    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Verifica se o objeto é novo

        # Criar a função get_exchange_rate
        if not self.price_brl:
            if self.broker.main_currency.ticker == 'BRL':
                self.price_brl = 1
            else:
                self.price_brl = get_exchange_rate(self.broker.main_currency.ticker, 'BRL', self.transaction_date.strftime('%Y-%m-%d'))

        if not self.price_usd:
            if self.broker.main_currency.ticker == 'USD':
                self.price_usd = 1
            else:
                self.price_usd = get_exchange_rate(self.broker.main_currency.ticker, 'USD', self.transaction_date.strftime('%Y-%m-%d'))

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

# Preço Médio, Total Investido, Total Atual (Mesma moeda do broker, calculado em BRL e USD)
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
                total_brl += transaction.transaction_amount * transaction.price_brl
                total_usd += transaction.transaction_amount * transaction.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'withdraw':
                total_brl -= transaction.transaction_amount * transaction.price_brl
                total_usd -= transaction.transaction_amount * transaction.price_usd
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

class AssetTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    transaction_type = models.CharField(max_length=50, choices=(('buy', 'Buy'), ('sell', 'Sell')), default='buy')
    transaction_amount = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    price_brl = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)

    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the object is new

        # Get the price of the asset
        # vou criar uma get_asset_price (asset.ticker, date), por enquanto vou trabalhar oferecendo o preço

        # Find or create a PortfolioInvestment with the correct Portfolio, Broker and Asset
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=self.asset
        )

        # Recalculate share_average_price_brl and share_average_price_usd
        portfolio_average_price, _ = AssetAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

        # Save the object
        super().save(*args, **kwargs)

        # Create a CurrencyTransaction
        if is_new:
            # Determine the transaction_type for the CurrencyTransaction
            if self.transaction_type == 'buy':
                currency_transaction_type = 'withdraw'

            else:  # self.transaction_type == 'sell'
                currency_transaction_type = 'deposit'

            # Determine the transaction_amount for the CurrencyTransaction
            if self.broker.main_currency.ticker == 'BRL':
                currency_transaction_amount = self.transaction_amount * self.price_brl
            elif self.broker.main_currency.ticker == 'USD':
                currency_transaction_amount = self.transaction_amount * self.price_usd

            # Create the CurrencyTransaction
            CurrencyTransaction.objects.create(
                portfolio=self.portfolio,
                broker=self.broker,
                transaction_type=currency_transaction_type,
                transaction_amount=currency_transaction_amount,
                transaction_date=self.transaction_date, 
                price_brl=self.price_brl,  
                price_usd=self.price_usd,  
            )

        # Recalculate share_average_price_brl and share_average_price_usd
        portfolio_average_price, _ = AssetAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()
    
    def delete(self, *args, **kwargs):
        # Antes de deletar o objeto, precisamos ajustar a quantidade de ações em portfolio_investment
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

        # Em seguida, recalcule as médias
        portfolio_average_price = AssetAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)

        # Depois deletar a CurrencyTransaction correspondente
        currency_transaction = CurrencyTransaction.objects.get(
            portfolio=self.portfolio, 
            broker=self.broker, 
            transaction_date=self.transaction_date
            )
        currency_transaction.delete()

        # Agora, podemos deletar o objeto
        super(AssetTransaction, self).delete(*args, **kwargs)

        

class AssetAveragePrice(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)

    def recalculate_average(self, start_date, is_new=False, transaction_id=None):
        # Get all transactions for this portfolio_investment, ordered by date
        transactions = AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

        # Initialize total_brl, total_usd, and total_shares with 0
        total_brl = 0
        total_usd = 0
        total_shares = 0

        # Go through the transactions and recalculate the total shares and total brl and usd
        for transaction in transactions:
            if transaction.transaction_type == 'buy':
                total_brl += transaction.transaction_amount * transaction.price_brl
                total_usd += transaction.transaction_amount * transaction.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'sell':
                total_brl -= transaction.transaction_amount * transaction.price_brl
                total_usd -= transaction.transaction_amount * transaction.price_usd
                total_shares -= transaction.transaction_amount

        # Update average prices
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0

        # Update the corresponding portfolio_investment
        portfolio_investment = self.portfolio_investment
        portfolio_investment.share_average_price_brl = self.share_average_price_brl
        portfolio_investment.share_average_price_usd = self.share_average_price_usd
        portfolio_investment.total_cost_brl = total_brl
        portfolio_investment.total_cost_usd = total_usd
        portfolio_investment.shares_amount = total_shares
        portfolio_investment.total_today_brl = total_shares * portfolio_investment.asset.price_brl
        portfolio_investment.total_today_usd = total_shares * portfolio_investment.asset.price_usd
        portfolio_investment.save()


    def delete(self, *args, **kwargs):
        # Before deleting the object, we need to adjust the amount of shares in portfolio_investment
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

        # Then recalculate averages
        portfolio_average_price = AssetAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)

        # Now we can delete the object
        super().delete(*args, **kwargs)



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

# entrada de dinheiro na carteira, como aporte ou dividendos, criará uma transação de moeda (CurrencyTransaction) Deposit
class Income(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} | {self.amount} | {self.broker.main_currency}"

# saída de dinheiro da carteira, como retirada ou taxa, criará uma transação de moeda (CurrencyTransaction) Withdraw
class Expense(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} - {self.amount}"
