import logger
from market import market
from binance.client import Client


class BinanceTrader (market):

    def __init__(self, apiKey, apiKeySecret,realMoney,name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(BinanceTrader, self).__init__(apiKey, apiKeySecret,realMoney,name)
        self.connect()

    def marketOrder(self, type, asset, currency):
        pass

    def resetToEquilibrium_Market(self, currentAmount, asset, currency):
        pass

    def getMaxAmountToUse(self, asset, currency):
        pass

    def marketBuy(self, orderSize, asset, currency, note):
        if self.real_money == True:
            result = self.market.order_market_buy(
                symbol=asset + currency,
                quantity=orderSize)
            logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                            orderSize,
                            note=note)
            return result
        else:
            result = self.market.create_test_order(
                symbol=asset + currency,
                side='BUY',
                type='MARKET',
                timeInForce='GTC',
                quantity=orderSize)

    def marketSell(self, orderSize, asset, currency, note):
            if self.real_money == True:
                result = self.market.order_market_sell(
        symbol=asset+currency,
        quantity=-orderSize)
                logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                                orderSize,
                                note=note)
                return result

            else:
                 result = self.market.create_test_order(
                symbol=asset + currency,
                side='SELL',
                type='MARKET',
                timeInForce='GTC',
                quantity=orderSize)

    def connect(self):
        self.market = Client(self.apiKey, self.apiKeySecret)
        pass


    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        pass

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        pass

    def limitShortEnd(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        pass

    def getCurrentPrice(self, asset, currency):
        prices = self.market.get_all_tickers()

    def closeLimitOrders(self, asset, currency):
        pass

    def getAmountOfItem(self, coin):
        balance = self.market.get_asset_balance(asset=coin)
        return balance
