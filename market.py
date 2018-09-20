import collections
from abc import ABC, abstractmethod
from time import sleep



class market(ABC):
    buyText = 'BUY'
    sellText = 'SELL'

    market = None
    btcToSatoshi = 100000000
    marginFromPrice = None
    maximumDeviationFromPrice = None
    goodLimitThreshold = None
    refreshDelay = 1
    bank = None

    apiKey = None
    apiKeySecret = None

    def __init__(self, priceMargin, maximum, limitThreshold, marketApiKey, marketApiKeySecret):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum
        self.goodLimitThreshold = limitThreshold
        self.apiKey = marketApiKey
        self.apiKeySecret = marketApiKeySecret

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
    def getCurrentPrice(self, asset, currency):
        pass;

    @abstractmethod
    def closeLimitOrders(self, asset, currency):
        pass;

    @abstractmethod
    def getAmountOfItem(self, coin):
        pass;

    def isInRange(self, type, previousPrice, currentPrice, percent):
        if type == self.buyText:
            return self.getLimit(type, previousPrice, percent) < currentPrice
        else:
            if type == self.sellText:
                return self.getLimit(type, previousPrice, percent) > currentPrice

    def getLimit(self, type, price, percent):
        if type == self.buyText:
            return price * (1 + percent)
        else:
            if type == self.sellText:
                return price * (1 - percent)

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

    def followingLimitOrder(self, type, asset, currency):
        initialPrice = self.getCurrentPrice(asset, currency)
        currentPrice = initialPrice
        limitPrice = 0
        orderID = None

        while self.isInRange(type, initialPrice, currentPrice, self.maximumDeviationFromPrice) or self.orderFilled(
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
