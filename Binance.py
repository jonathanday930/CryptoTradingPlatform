import logger
from market import market
from binance.client import Client

class Binance (market):
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
                            orderQuantity,
                            note=note)
            return result
        else:
            result = self.market.create_test_order(
                symbol=asset + currency,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=orderQuantity,

    def marketSell(self, orderSize, asset, currency, note):
            if self.real_money == True:
                result self.market.order_market_sell(
        symbol=asset+currency,
        quantity=-orderSize)
                logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                                orderQuantity,
                                note=note)
                return result

            else:
                 result = self.market.create_test_order(
                symbol=asset + currency,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=orderQuantity,

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
        pass

    def closeLimitOrders(self, asset, currency):
        pass

    def getAmountOfItem(self, coin):
        pass