from portfolios.models import PortfolioInvestment

# set_portfolio_investment for future update on process_transaction
def set_portfolio_investment(self):
    self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
        portfolio=self.portfolio,
        broker=self.broker,
        asset=self.asset
    )

# Adjust the portfolio investment by updating the number of shares when the asset transaction is deleted
def adjust_portfolio_investment(self):
    if self.trade_type == 'buy':
        self.portfolio_investment.shares_amount -= self.trade_amount
    elif self.trade_type == 'sell':
        self.portfolio_investment.shares_amount += self.trade_amount
    self.portfolio_investment.save()


def update_portfolio_investment(trade_calculation, total_brl, total_usd, total_shares):
    portfolio_investment = trade_calculation.portfolio_investment
    portfolio_investment.share_average_price_brl = trade_calculation.share_average_price_brl
    portfolio_investment.share_average_price_usd = trade_calculation.share_average_price_usd
    portfolio_investment.total_cost_brl = total_brl
    portfolio_investment.total_cost_usd = total_usd
    portfolio_investment.shares_amount = total_shares
    portfolio_investment.trade_profit_brl = trade_calculation.trade_profit_brl
    portfolio_investment.trade_profit_usd = trade_calculation.trade_profit_usd
    portfolio_investment.total_today_brl = total_shares * portfolio_investment.asset.price_brl
    portfolio_investment.total_today_usd = total_shares * portfolio_investment.asset.price_usd
    portfolio_investment.save()
