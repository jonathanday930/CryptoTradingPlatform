from abc import ABC, abstractmethod
class market(ABC):

    marginFromPrice = None
    maximumDeviationFromPrice = None

    def __init__(self, priceMargin,maximum):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum

    @abstractmethod
    def limitBuy(self):
        pass;

    @abstractmethod
    def limitSell(self):
        pass;

    @abstractmethod
    def limitShortStart(self):
        pass;

    @abstractmethod
    def limitShortEnd(self):
        pass;

    @abstractmethod
    def getCurrentPrice(self):
        pass;

    @abstractmethod
    def closeLimitOrders(self):
        pass;


    def inRange(self,type, initPrice, currentPrice):

        if type == 'buy':
            return initPrice *(1+self.maximumDeviationFromPrice) < currentPrice
        else:
            if type == 'sell':
                return initPrice * (1 - self.maximumDeviationFromPrice) > currentPrice
        if type == 'shortOpen':
            return initPrice * (1 - self.maximumDeviationFromPrice) < currentPrice
        else:
            if type == 'shortClose':
                return initPrice * (1 + self.maximumDeviationFromPrice) > currentPrice


    def processOrder(self,type):


    def followingLimitOrder(self,type):
        initialPrice = self.getCurrentPrice()
        currentPrice = initialPrice


        while(self.inRange(type,initialPrice,currentPrice)):
            self.closeLimitOrders()

