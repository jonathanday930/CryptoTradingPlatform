from abc import ABC, abstractmethod

from recording import bank

buyText = 'BUY'
sellText = 'SELL'

class marketBaseClass(ABC):
    """ """
    limitOrderEnabled = None
    buyText = buyText
    sellText = sellText
    connectorName = None
    market = None
    btcToSatoshi = 100000000
    bank = None

    marketName = ' marketName is set to nothing. You must change it in market specifications'
    contractExchange = False

    apiKey = None
    apiKeySecret = None

    real_money = False

    def __init__(self, realMoney,name,*args):
        self.real_money = realMoney
        self.connectorName = name

    @abstractmethod
    def connect(self):
        """ """
        pass

    @abstractmethod
    def getAmountOfItem(self, val1, val2=None, orderType=None):
        """

        :param val1: 
        :param val2:  (Default value = None)
        :param orderType:  (Default value = None)

        """
        pass

    @abstractmethod
    def makeOrder(self, order):
        """

        :param order: 

        """
        pass

    @abstractmethod
    def interpretType(self, type):
        """

        :param type: 

        """
        pass

    @abstractmethod
    def getCurrentPrice(self, val1, val2=None):
        """

        :param val1: 
        :param val2:  (Default value = None)

        """
        pass

    def parseOrderForBasicInfo(self, order):
        """

        :param order: 

        """
        sliceDict = {}
        for key in order:
            if key in ['market', 'asset', 'currency', 'currentPrice', 'action', 'action-type']:
                sliceDict[key] = order[key]
        return sliceDict

    def logOrderInBank(self, order, orderAmount=None, orderPrice=None, action=None):
        """

        :param order: 
        :param orderAmount:  (Default value = None)
        :param orderPrice:  (Default value = None)
        :param action:  (Default value = None)

        """
        transactionStatement = {}
        transactionStatement['market'] = order['market']
        transactionStatement['strategy'] = order['strategy']
        transactionStatement['currency'] = order['currency']
        transactionStatement['asset'] = order['asset']
        transactionStatement['amount'] = orderAmount
        transactionStatement['currency'] = order['currency']
        transactionStatement['price'] = orderPrice
        transactionStatement['action'] = action
        transactionStatement['action-type'] = order.get('action-type')
        bank.logTransaction(transactionStatement)
