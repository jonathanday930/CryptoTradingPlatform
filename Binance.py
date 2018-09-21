import logger
from market import market
from binance.client import Client

class Binance (market):
    def connect(self):
        self.market = Client(self.apiKey, self.apiKeySecret)
        pass

    def marketOrder(self, type, asset, currency):
        try:

            currentAmount = self.getAmountOfItem(asset + currency)
            print("current amount of %s%s: %f \n" % (asset, currency, currentAmount))

            change = self.resetToEquilibrium_Market(currentAmount, asset, currency)
            # orderSize = self.bank.update(change)
            orderSize = self.getMaxAmountToUse(asset, currency) * 0.4
            if type == 'buy':
                result = self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
            else:
                if type == 'sell':
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
            self.secondAttempt = False
            return result

        except Exception as e:
            logger.logError(e)
            if self.secondAttempt:
                return None
            sleep(1)
            self.connect()
            self.secondAttempt = True
            self.marketOrder(type, asset, currency)


        def marketBuy(self, orderQuantity, asset, currency, note=None):
            if self.real_money==True:
                result = self.market.order_market_buy(
        symbol=asset+currency,
        quantity=orderQuantity)
                logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                                orderQuantity,
                                note=note)
                return result
            else:
                result = self.market.create_test_order(
                    symbol=asset+currency,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=orderQuantity,

        def marketSell(self, orderQuantity, asset, currency, note=None):
            if self.real_money == True:
                result self.market.order_market_sell(
        symbol=asset+currency,
        quantity=-orderQuantity)
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