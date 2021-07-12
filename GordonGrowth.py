from datetime import date
from datetime import timedelta


class GordonGrowthModel:
    def __init__(self):
        pass


    def value(self, edps, coe, dgr):
        #multiply by 4 to annualize dividends
        return edps * 4 * (dgr) / (coe - (dgr - 1))


    def dividend_growth_rate(self, symbol, dividend_content, split_content):

        if not dividend_content:
            return (f'Insufficient data available for {symbol}')

        payed_dividends = {}

        for item in dividend_content:
            payed_dividends[item['paymentDate']] = item['amount']
        
        # IF there has been a split within the last 2 yearrs 
        if split_content and split_content[0]['exDate'] > str(date.today() - timedelta(365 * 2)):
            last_split_date = split_content[0]['exDate']
            split_ratio = split_content[0]['ratio']

            # multiply each dividend amount after the split by the ratio
            # mean growth rate avg(Ending Price - Starting Price)/(Starting Price)] * 100) 
            
            for payed_date, amount in payed_dividends.items():
                if payed_date > last_split_date:
                    #payed_dividends[payed_date] = payed_dividends[payed_date] * multiplier
                    payed_dividends[payed_date] *= 1 / split_ratio

        # calculate mean grwoth rate for payed dividends
        # for each of these value
        sum = 0
        for _ in range(0, len(payed_dividends.values()) - 1):
            # (i - i_-1) / i
            sum += (list(payed_dividends.values())[_] - list(payed_dividends.values())[_ + 1]) / list(payed_dividends.values())[_]

        return ((sum / len(payed_dividends.values())) * 8) + 1


    def cost_of_capital_equity(self, beta, rf, rm):
        return rf + (beta * (rm - rf))


    def expected_dividends_per_share(self, dividend_growth_rate, dividend_amount):
        return dividend_growth_rate * dividend_amount
