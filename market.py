import collections
from abc import ABC, abstractmethod
from time import sleep

buyText = 'BUY'
sellText = 'SELL'
shortOpenText = 'SHORT'
shortCloseText = 'SHORTCLOSE'


class market(ABC):
    marginFromPrice = None
    maximumDeviationFromPrice = None
    goodLimitThreshold = None
    refreshDelay = 1

    def __init__(self, priceMargin, maximum, limitThreshold):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum
        self.goodLimitThreshold = limitThreshold

    @abstractmethod
    def limitBuy(self, limitPrice, currency, asset, orderNumber=None):
        pass;

    @abstractmethod
    def limitSell(self, limitPrice, currency, asset, orderNumber=None):
        pass;

    @abstractmethod
    def limitShortStart(self, limitPrice, currency, asset, orderNumber=None):
        pass;

    @abstractmethod
    def limitShortEnd(self, limitPrice, currency, asset, orderNumber=None):
        pass;

    @abstractmethod
    def getCurrentPrice(self, currency, asset):
        pass;

    @abstractmethod
    def closeLimitOrders(self, currency, asset):
        pass;

    @abstractmethod
    def getAmountOfItem(self, coin):
        pass;

    def isInRange(self, type, previousPrice, currentPrice, percent):
        if type == buyText:
            return self.getLimit(type, previousPrice, percent) < currentPrice
        else:
            if type == sellText:
                return self.getLimit(type, previousPrice, percent) > currentPrice
            else:
                if type == shortOpenText:
                    return self.getLimit(type, previousPrice, percent) < currentPrice
                else:
                    if type == shortCloseText:
                        return self.getLimit(type, previousPrice, percent) > currentPrice

    def getLimit(self, type, price, percent):
        if type == buyText:
            return price * (1 + percent)
        else:
            if type == sellText:
                return price * (1 - percent)
        if type == shortOpenText:
            return price * (1 - percent)
        else:
            if type == shortCloseText:
                return price * (1 + percent)

    def isFittingPrice(self, limitPrice, currentPrice):
        return ((1 + self.goodLimitThreshold) * limitPrice > currentPrice > (
                1 - self.goodLimitThreshold) * limitPrice) or limitPrice == 0

    def sendOrder(self, type, currentPrice, currency, asset, orderID):

        limitPrice = self.getLimit(type, currentPrice, self.marginFromPrice)
        if type == buyText:
            orderID = self.limitBuy(limitPrice, currency, asset, orderID)
        else:
            if type == sellText:
                orderID = self.limitSell(limitPrice, currency, asset, orderID, orderQuantity)
        if type == shortOpenText:
            orderID = self.limitShortStart(limitPrice, currency, asset, orderID)
        else:
            if type == shortCloseText:
                orderID = self.limitShortEnd(limitPrice, currency, asset, orderID)
        result = collections.namedtuple('result', ['limitPrice', 'orderID'])
        res = result(limitPrice, orderID)
        return res

    def followingLimitOrder(self, type, currency, asset):
        initialPrice = self.getCurrentPrice(currency, asset)
        currentPrice = initialPrice
        limitPrice = 0
        orderID = None

        while self.isInRange(type, initialPrice, currentPrice, self.maximumDeviationFromPrice) or self.orderFilled(
                currency):
            if self.isInRange(type, limitPrice, currentPrice, self.goodLimitThreshold):
                res = self.sendOrder(type, currentPrice, currency, asset, orderID)
                limitPrice = res.limitPrice
                orderID = res.orderID
            sleep(self.refreshDelay)
            currentPrice = self.getCurrentPrice(currency, asset)

    # we can alter this side of things later to only use a certain amount
    def orderFilled(self, currency):
        return currency == 0
