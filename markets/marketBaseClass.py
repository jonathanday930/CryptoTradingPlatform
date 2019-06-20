from abc import ABC, abstractmethod

from debug import bank


def getIfExists(dict, key):
    if key in dict:
        return dict[key]
    else:
        return None


class marketBaseClass(ABC):
    limitOrderEnabled = None
    buyText = 'BUY'
    sellText = 'SELL'
    connectorName = None
    market = None
    btcToSatoshi = 100000000
    bank = None
    marketName = ' marketName is set to nothing. You must change it '
    contractExchange = False

    apiKey = None
    apiKeySecret = None

    real_money = False

    def __init__(self, marketApiKey, marketApiKeySecret, realMoney, name):
        self.apiKey = marketApiKey
        self.apiKeySecret = marketApiKeySecret
        self.real_money = realMoney
        self.connectorName = name

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def getAmountOfItem(self, val1, val2=None, orderType=None):
        pass

    @abstractmethod
    def makeOrder(self, order):
        pass

    @abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def getCurrentPrice(self, val1, val2=None):
        pass

    def parseOrderForBasicInfo(self, order):
        sliceDict = {}
        for key in order:
            if key in ['market', 'asset', 'currency', 'currentPrice', 'action', 'action-type']:
                sliceDict[key] = order[key]
        return sliceDict

    def logOrderInBank(self, order, orderAmount=None, orderPrice=None, action=None):
        transactionStatement = {}
        transactionStatement['market'] = order['market']
        transactionStatement['currency'] = order['currency']
        transactionStatement['asset'] = order['asset']
        transactionStatement['amount'] = orderAmount
        transactionStatement['currency'] = order['currency']
        transactionStatement['price'] = orderPrice
        transactionStatement['action'] = action
        transactionStatement['action-type'] = order.get('action-type')
        bank.logTransaction(transactionStatement)
