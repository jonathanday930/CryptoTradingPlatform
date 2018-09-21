import collections
import bank
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
    goodLimitThreshold = None
    refreshDelay = 1
    bank = None

    attemptsTotal = 10
    attemptsLeft = attemptsTotal
    delayBetweenAttempts = 6

    apiKey = None
    apiKeySecret = None

    real_money = False


    def __init__(self,  marketApiKey, marketApiKeySecret,realMoney,name):
        self.apiKey = marketApiKey
        self.apiKeySecret = marketApiKeySecret
        self.real_money = realMoney
        self.connectorName = name

    @abstractmethod
    def connect(self):
        pass;


    @abstractmethod
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None,):
        pass;

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        pass;



    @abstractmethod
    def marketOrder(self, type, asset, currency):
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

    def isInRange(self, type, previousPrice, currentPrice, percent):
        if type == self.buyText:
            value =  self.getLimit(type, previousPrice, percent) < currentPrice
            return value
        else:
            if type == self.sellText:
                value = self.getLimit(type, previousPrice, percent) > currentPrice
                return value

    def getLimit(self, type, price, percent):
        if type == self.buyText:
            value =  price * (1 + percent)
            return value
        else:
            if type == self.sellText:
                value = price * (1 - percent)
                return value

    def isFittingPrice(self, limitPrice, currentPrice):
        return ((1 + self.goodLimitThreshold) * limitPrice > currentPrice > (
                1 - self.goodLimitThreshold) * limitPrice) or limitPrice == 0

    def sendOrder(self, type, currentPrice, asset, currency, orderID):

        limitPrice = self.getLimit(type, currentPrice, self.marginFromPrice)

        if type == self.buyText:
            orderID = self.limitBuy(limitPrice, asset, currency, orderID)
        else:
            if type == self.sellText:
                orderID = self.limitSell(limitPrice, asset, currency, 1, orderID)
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
            if type ==  self.buyText:
                result = self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
            else:
                if type == self.sellText:
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
            self.attemptsLeft = self.attemptsTotal
            return result
        except Exception as e:
            logger.logError(e)
            if self.attemptsLeft == 0:
                return None
            sleep(self.delayBetweenAttempts)
            self.connect()
            self.attemptsLeft = self.attemptsLeft - 1
            self.marketOrder(type, asset, currency)


    def followingLimitOrder(self, type, asset, currency):
        initialPrice = self.getCurrentPrice(asset, currency)
        currentPrice = initialPrice
        limitPrice = 0
        orderID = None

        while self.isInRange(type, initialPrice, currentPrice, self.maximumDeviationFromPrice) or not self.orderFilled(
                currency):
            if self.isInRange(type, limitPrice, currentPrice, self.goodLimitThreshold):
                res = self.sendOrder(type, currentPrice, asset, currency, orderID)
                limitPrice = res.limitPrice
                orderID = res.orderID
            sleep(self.refreshDelay)
            currentPrice = self.getCurrentPrice(asset, currency)

    # we can alter this side of things later to only use a certain amount
    def orderFilled(self, currency):
        return currency == 0

    def gma(self, asset, currency):
        percentLower = .05
        curr = self.getAmountOfItem(currency)
        price = self.getCurrentPrice(asset,currency)
        return (curr/price) * (1-percentLower)

    def getAmountToUse(self, asset, currency, orderType):
        if(orderType == self.buyText):
            return self.getAmountOfItem('BTC')
        return self.getAmountOfItem(asset)

    @abstractmethod
    def resetToEquilibrium_Market(self, currentAmount, asset, currency):
        pass

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

