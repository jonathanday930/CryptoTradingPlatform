import collections
from decimal import Decimal

from abc import ABC, abstractmethod
from time import sleep

import logger


class market(ABC):
    buyText = 'BUY'
    sellText = 'SELL'
    connectorName = None
    market = None
    btcToSatoshi = 100000000
    marginFromPrice = None
    maximumDeviationFromPrice = None
    bank = None
    marketName = ' DEFAULT MARKET '

    attemptsTotal = 10
    attemptsLeft = attemptsTotal
    delayBetweenAttempts = 6

    delayBetweenLimitOrder = 3

    apiKey = None
    apiKeySecret = None

    real_money = False
    limitOrderEnabled = False

    def __init__(self, marketApiKey, marketApiKeySecret, realMoney, name):
        self.apiKey = marketApiKey
        self.apiKeySecret = marketApiKeySecret
        self.real_money = realMoney
        self.connectorName = name

    @abstractmethod
    def connect(self):
        pass;

    @abstractmethod
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None,note=None ):
        pass;

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None,note=None):
        pass;

    @abstractmethod
    def getCurrentPrice(self, asset, currency):
        pass;

    @abstractmethod
    def closeLimitOrders(self, asset, currency):
        pass;

    @abstractmethod
    def getAmountOfItem(self, coin):
        pass;

    @abstractmethod
    def getAmountOfItem(self, coin):
        pass;


    @abstractmethod
    def getTickSize(self,asset,currency):
        pass

    def isInRange(self, type, firstPrice, currentPrice, percent, enabled=True):
        if enabled:
            if type == self.buyText:
                value = self.getLimit(type, firstPrice, percent) > currentPrice
                return value
            else:
                if type == self.sellText:
                    value = self.getLimit(type, firstPrice, percent) < currentPrice
                    return value
        else:
            return True

    def getLimit(self, type, price, percent):
        if type == self.buyText:
            value = price * (1 + percent)
            return value
        else:
            if type == self.sellText:
                value = price * (1 - percent)
                return value

    def calculateLimitPrice(self,currentPrice,tickSize):
        currentPrice = str(Decimal(currentPrice))
        tickSize = '{0:.10f}'.format(tickSize)[:10]
        decimalSpot =currentPrice.find(".")
        has5 =tickSize.find("5")


        if has5 > 0:
            nextDigit = currentPrice[decimalSpot + 1:decimalSpot + has5]
            if int(nextDigit) < 4:
                currentPrice=currentPrice[:decimalSpot + has5-1]+ str(0)
            else:
                currentPrice = currentPrice[:decimalSpot + has5-1]+str(5)
        else:
            to1 = tickSize.find("1")
            currentPrice = Decimal(tickSize) + Decimal(currentPrice)
            currentPrice = str(currentPrice)[:decimalSpot+to1]

        return currentPrice

    #'0.00008829000000000001018192474777634970450890250504016876220703125'
    #0.00008830000000000001018192474778
    def sendLimitOrder(self, type, currentPrice, asset, currency, orderQuantity, orderID,note=None):
        tickSize = self.getTickSize(asset,currency)

        limitPrice = Decimal(self.calculateLimitPrice(currentPrice,tickSize))

        if type == self.buyText:
            orderID = self.limitBuy(limitPrice, asset, currency, orderQuantity, orderID,note)
        else:
            if type == self.sellText:
                orderID = self.limitSell(limitPrice, asset, currency, orderQuantity, orderID,note)
        result = collections.namedtuple('result', ['limitPrice', 'orderID'])
        res = result(limitPrice, orderID)
        return res

    def marketOrder(self, type, asset, currency):
        try:
            currentAmount = self.getAmountOfItem(asset + currency)
            print("current amount of %s%s: %f \n" % (asset, currency, currentAmount))

            change = self.resetToEquilibrium_Market(currentAmount, asset, currency)
            # orderSize = self.bank.update(change)
            orderSize = self.getMaxAmountToUse(asset, currency) * 0.4
            if type == self.buyText:
                result = self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
            else:
                if type == self.sellText:
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
            self.attemptsLeft = self.attemptsTotal
            return result
        except Exception as e:
            logger.logError(e)
            if self.attemptsLeft == 0:
                self.attemptsLeft = self.attemptsTotal
                return None
            sleep(self.delayBetweenAttempts)
            self.connect()
            self.attemptsLeft = self.attemptsLeft - 1
            self.marketOrder(type, asset, currency)

    def switchOrder(self, type):
        if type == self.buyText:
            return self.sellText
        else:
            if type == self.sellText:
                return self.buyText

    def executeLimitOrder(self, type, asset, currency):
        amount = self.getAmountFromPair(asset, currency)

        if amount > 0:
            self.followingLimitOrder(self.sellText, asset, currency, amount, False,note='Buying for equilibrium')
        else:
            if amount < 0:
                self.followingLimitOrder(self.buyText, asset, currency, -amount, False,note='Selling for equilibrium')

        # noinspection PyTypeChecker
        orderQuantity = self.getMaxAmountToUse(asset, currency) * 0.4

        self.followingLimitOrder(type, asset, currency, orderQuantity, True,note='Standard limit order ')

    def followingLimitOrder(self, type, asset, currency, orderQuantity, restricted=True,initial_price = None, orderID = None,note = None):
        try:

            asset = self.interpretType(asset)
            currency = self.interpretType(currency)
            type = self.interpretType(type)

            initialPrice = initial_price
            if initialPrice == None:
                initialPrice = self.getCurrentPrice(asset, currency)
            currentPrice = initialPrice

            while self.isInRange(type, initialPrice, currentPrice, self.maximumDeviationFromPrice,
                                 restricted) and not self.limitOrderFilled(orderID) and orderQuantity != 0:
                res = self.sendLimitOrder(type, currentPrice, asset, currency, orderQuantity, orderID,note)
                orderID = res.orderID
                sleep(self.delayBetweenLimitOrder)
                currentPrice = self.getCurrentPrice(asset, currency)

            if (not self.limitOrderFilled(orderID)):
                self.closeLimitOrder(orderID)

        except Exception as e:
                logger.logError(e)
                if self.attemptsLeft == 0:
                    self.attemptsLeft = self.attemptsTotal
                    return None
                sleep(self.delayBetweenAttempts)
                self.connect()
                self.attemptsLeft = self.attemptsLeft - 1
                self.followingLimitOrder(type, asset, currency,orderQuantity,restricted,initialPrice,orderID)


    @abstractmethod
    def limitOrderFilled(self, orderID):
        pass

    @abstractmethod
    def interpretType(self,type):
        pass

    def getAmountToUse(self, asset, currency, orderType):
        if (orderType == self.buyText):
            return self.getAmountOfItem('BTC')
        return self.getAmountOfItem(asset)

    @abstractmethod
    def resetToEquilibrium_Market(self, currentAmount, asset, currency):
        pass

    def getAmountFromPair(self, asset, currency):
        result = self.getAmountOfItem(asset + currency)
        return result

    @abstractmethod
    def getMaxAmountToUse(self, asset, currency):
        pass

    @abstractmethod
    def marketBuy(self, orderSize, asset, currency, note):
        pass

    @abstractmethod
    def marketSell(self, orderSize, asset, currency, note):
        pass

    @abstractmethod
    def getAmountOfItem(self, coin):
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        pass
