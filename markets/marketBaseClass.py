from abc import ABC, abstractmethod

from recording import bank

buyText = 'BUY'
sellText = 'SELL'

class marketBaseClass(ABC):
    """ This is a basic market class that all other market connectors must be a child of. """
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
        """Connects to the market, if necessary. """
        pass

    @abstractmethod
    def getAmountOfItem(self, val1, val2=None, orderType=None):
        """
        Gets the amount of an item, like XRPBTC

        :param val1: The first value
        :param val2:  (Default value = None) The second value in the pair, if there is one.
        :param orderType:  (Default value = None) The type of order. Must be able to handle marketBaseClass.buyText, or marketBaseClass.sellText

        """
        pass

    @abstractmethod
    def makeOrder(self, order):
        """
        This is called every few seconds until the order is complete. For market connections that use a market order instead of a limit order, odds are this function will only be called once.

        :param order: The order dictionary created by a strategy class. See the strategy class for specification on the contents.

        """
        pass

    @abstractmethod
    def interpretType(self, type):
        """
        Interprets a type into the market accepted type. For example, USD could be turned into USDT if the market uses USDT.

        :param type: A string for the type to be converted.

        """
        pass

    @abstractmethod
    def getCurrentPrice(self, val1, val2=None):
        """
        Gets the price of an item on the exchange. Val1 and Val2 exist because some markets are contractural and some are with actual currency.

        :param val1: The first value
        :param val2:  (Default value = None) The second value

        """
        pass

    def parseOrderForBasicInfo(self, order):
        """
        Parses an order dict to get the important details
        :param order:

        TODO: Delete if necessary. Does not currently have use

        """
        sliceDict = {}
        for key in order:
            if key in ['market', 'asset', 'currency', 'currentPrice', 'action', 'action-type']:
                sliceDict[key] = order[key]
        return sliceDict

    def logOrderInBank(self, order, orderAmount=None, orderPrice=None, action=None):
        """
        Logs a completed order in the bank so that profits can be calculated.

        :param order: The order dict
        :param orderAmount:  (Default value = None) The amount bought or sold
        :param orderPrice:  (Default value = None) The price
        :param action:  (Default value = None) Either marketBaseClass.buyText, or marketBaseClass.sellText, signifying whether it was a buy/long or sell/short.

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
