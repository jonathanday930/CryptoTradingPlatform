from abc import ABC, abstractmethod
from time import sleep


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
    def limitBuy(self, limitPrice, currency, asset):
        pass;

    @abstractmethod
    def limitSell(self, limitPrice, currency, asset):
        pass;

    @abstractmethod
    def limitShortStart(self, limitPrice, currency, asset):
        pass;

    @abstractmethod
    def limitShortEnd(self, limitPrice, currency, asset):
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
        if type == 'buy':
            return self.getLimit(type, previousPrice, percent) < currentPrice
        else:
            if type == 'sell':
                return self.getLimit(type, previousPrice, percent) > currentPrice
            else:
                if type == 'shortOpen':
                    return self.getLimit(type, previousPrice, percent) < currentPrice
                else:
                    if type == 'shortClose':
                        return self.getLimit(type, previousPrice, percent) > currentPrice

    def getLimit(self, type, price, percent):
        if type == 'buy':
            return price * (1 + percent)
        else:
            if type == 'sell':
                return price * (1 - percent)
        if type == 'shortOpen':
            return price * (1 - percent)
        else:
            if type == 'shortClose':
                return price * (1 + percent)

    def isFittingPrice(self, limitPrice, currentPrice):
        return ((1 + self.goodLimitThreshold) * limitPrice > currentPrice > (
                1 - self.goodLimitThreshold) * limitPrice) or limitPrice == 0

    def sendOrder(self, type, currentPrice, currency, asset):

        limitPrice = self.getLimit(type, currentPrice, self.marginFromPrice)

        if type == 'buy':
            self.limitBuy(limitPrice, currency, asset)
        else:
            if type == 'sell':
                self.limitSell(limitPrice, currency, asset)
        if type == 'shortOpen':
            self.limitShortStart(limitPrice, currency, asset)
        else:
            if type == 'shortClose':
                self.limitShortEnd(limitPrice, currency, asset)

        return limitPrice

    def followingLimitOrder(self, type, currency, asset):
        initialPrice = self.getCurrentPrice()
        currentPrice = initialPrice
        limitPrice = 0

        while self.isInRange(type, initialPrice, currentPrice, self.maximumDeviationFromPrice) or self.orderFilled(
                currency):
            if self.isInRange(type, limitPrice, currentPrice, self.goodLimitThreshold):
                self.closeLimitOrders(currency, asset)
                limitPrice = self.sendOrder(type, currentPrice, currency, asset)
            sleep(self.refreshDelay)
            currentPrice = self.getCurrentPrice()

    # we can alter this side of things later to only use a certain amount
    def orderFilled(self, currency):
        return currency == 0
