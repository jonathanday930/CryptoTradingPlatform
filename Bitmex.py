import datetime
from math import floor
from time import sleep

import bitmexApi.bitmex
import logger
from market import market

marketName = 'Bitmex'


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(market):

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        # TODO: figure out quantity params
        orderQuantity = orderQuantity * -1
        self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, price=limitPrice,
                                    ordType="Limit").result()

    def limitBuy(self, price, asset, currency, orderQuantity, orderId=None):
        if orderId == None:
            result = self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Limit",
                                                 price=price).result()
            tradeInfo = result[0]
            for key, value in tradeInfo.items():
                if key == "orderID":
                    newOrderId = (key + ": {0}".format(value))
            return newOrderId
        else:
            result = self.market.Order.Order_amend(orderID=orderId, price=price)
            return result
        return None

    def resetToEquilibrium_Market(self, amount, asset, currency):
        before = self.getAmountOfItem('xbt')

        if amount < 0:
            self.marketBuy(-amount, asset, currency, note='Buying for equilibrium')
        else:
            if amount > 0:
                self.marketSell(amount, asset, currency, note='Selling for equilibrium')
        after = self.getAmountOfItem('xbt')
        return after - before

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
            self.attemptsLeft = self.attemptsTotal= False
            return result

        except Exception as e:
            logger.logError(e)
            if self.attemptsLeft == 0:
                return None
            sleep(1)
            self.connect()
            self.attemptsLeft = self.attemptsLeft - 1
            self.marketOrder(type, asset, currency)

    def marketBuy(self, orderQuantity, asset, currency, note=None):
        result = self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Market").result()
        logger.logOrder('Bitmex', 'market', self.getCurrentPrice(asset, currency), asset, currency, orderQuantity,
                        note=note)
        return result

    def marketSell(self, orderQuantity, asset, currency, note=None):
        return self.marketBuy(-orderQuantity, asset, currency, note=note)

    def closeLimitOrders(self, asset, currency):
        # client.Order.Order_cancel(orderID='').result()
        self.market.Order.Order_cancelAll().result()

    def __init__(self, apiKey, apiKeySecret,realMoney,name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(Bitmex, self).__init__(apiKey, apiKeySecret,realMoney,name)
        self.connect()
        pass

    def connect(self):
        self.market = bitmexApi.bitmex.bitmex(test=not self.real_money, config=None, api_key=self.apiKey, api_secret=self.apiKeySecret)

    def getAmountToUse(self, asset, currency, orderType):
        if orderType == self.buyText:
            return self.getAmountOfItem('XBt')
        return self.getAmountOfItem(asset)

    def getMaxAmountToUse(self, asset, currency, curr=None):
        percentLower = 0.01
        if curr is None:
            curr = self.getAmountOfItem('XBt') * (1 - percentLower)

        price = self.getCurrentPrice(asset, currency)
        if currency == 'USD' or (currency == 'U18' and asset == 'XBT'):
            result = floor(curr * price)
        else:
            result = floor((curr / price))
        return result

    def getAmountOfItem(self, coin):
        if coin.lower() == 'xbt':
            return self.market.User.User_getMargin().result()[0]['availableMargin'] / self.btcToSatoshi
        else:
            symbol = '{"symbol": "' + coin + '"}'
            result = self.market.Position.Position_get(filter=symbol).result()
            if len(result[0]) > 0:
                return result[0][0]['currentQty']
            else:
                return 0

    def getCurrentPrice(self, asset, currency):
        startTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
        trades = self.market.Trade.Trade_get(symbol=asset + currency, startTime=startTime).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        return sum / volume

    def get_orders(self, asset, currency):
        orders = self.market.Order.Order_getOrders(symbol=asset + currency, reverse=True).result()
        orderList = orders[0]
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)
        return orderList

    def getWallet(self):
        return self.market.User.User_getWallet().result()

    def getNumberOfTradingPairs(self):
        pass

    # def logOrder(self, orderQuantity, asset, currency):
    #     print("Available Balance: %s \n" % (self.getAvailableBalanceInUsd()))
    #     print("Ordering %d contracts of %s%s \n" % (orderQuantity, asset, currency))
    #     pass
#
#
#
#
#         amount = self.getAmountOfItem(asset + currency)
#         print("current amount of %s%s: %f \n" % (asset, currency, amount))
#
#         # if we are currently in a Long
#         if amount > 0:
#             amountToBuy = amount * -1
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#         else:
#             # numberOfCoins = self.getNumberOfTradingPairs()
#             numberOfCoins = 2
#             allowedAmount = (self.getAvailableBalanceInUsd() / numberOfCoins)
#             extraToSell = (allowedAmount - abs(amount)) * -1
#             self.logOrder(extraToSell, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=extraToSell, ordType="Market").result()
#         pass

#
# def figureOutShare(self):
#        numberOfCoins = 2
#        availableBalance = self.getAvailableBalanceInUsd()
#        allowedAmount = availableBalance / numberOfCoins
#        extraToBuy = allowedAmount - amount
#        self.logOrder(extraToBuy, asset, currency)


# def getAvailableBalanceInUsd(self):
#     availableBalance = self.market.User.User_getMargin(currency="XBt").result()
#     user = availableBalance[0]
#     balanceInBtc = user['withdrawableMargin'] / 100000000
#     balanceInUsd = floor((balanceInBtc * self.getCurrentPrice('XBT', 'USD'))) - 1
#     return balanceInUsd
