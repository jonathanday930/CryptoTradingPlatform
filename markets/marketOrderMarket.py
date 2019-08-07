import traceback
from abc import abstractmethod
from asyncio import sleep

from recording import bank
from recording import logger
from markets.marketBaseClass import marketBaseClass


class marketOrderMarket(marketBaseClass):
    """ An abstract class that is a child of marketBaseClass. This class lays out all the functions that need to be implemented by an exchange in order for market orders to be managed."""

    @abstractmethod
    def connect(self):
        """ Connects to the exchange, if necessary. """
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

    @abstractmethod
    def marketBuy(self, orderQuantity, asset, currency, note=None):
        """
        Initiates a market order buy on the exchange

        :param orderQuantity: 
        :param asset: The asset, a string
        :param currency:  The currency, a string
        :param note:  (Default value = None) A

        """
        pass

    @abstractmethod
    def marketSell(self, orderQuantity, asset, currency, note=None):
        """
        Initiates a market order sell on the exchange


        :param orderQuantity: 
        :param asset: The asset, a string
        :param currency:  The currency, a string
        :param note:  (Default value = None) A

        """
        pass

    def makeOrder(self, order):
        """
        Handles the boilerplate operations for creating a market order. For contractural exchanges with shorts, sends out an order to equilibriumize the balance.

        :param order: The order dict

        """
        tries = 0
        maxTries = 7
        while tries < maxTries:

            try:
                currentAmount = self.getAmountOfItem(order['currency'], order['asset'])
                text = "current amount of %s%s: %f \n " % (order['currency'], order['asset'], currentAmount)
                print(text)

                if currentAmount > 0 and order['action'] == self.sellText or currentAmount < 0 and order[
                    'action'] == self.buyText:
                    self.marketBuy(-currentAmount, order['currency'], order['asset'], note='Resetting to equilibrium')
                    self.logOrderInBank(order, action=self.buyText if -currentAmount > 0 else self.sellText,
                                        orderAmount=abs(currentAmount),
                                        orderPrice=self.getCurrentPrice(order['currency'], order['asset']))

                orderSize = order['orderQuantity']

                if order['action'] == self.buyText:
                    result = self.marketBuy(orderSize, order['currency'], order['asset'], note='Going long')
                    self.logOrderInBank(order, action=self.buyText,
                                        orderAmount=self.getAmountOfItem(order['currency'], order['asset']),
                                        orderPrice=self.getCurrentPrice(order['currency'], order['asset']))
                else:
                    if order['action'] == self.sellText:
                        result = self.marketSell(orderSize, order['currency'], order['asset'], note='Going short')
                        self.logOrderInBank(order, action=self.sellText,
                                            orderAmount=self.getAmountOfItem(order['currency'], order['asset']),
                                            orderPrice=self.getCurrentPrice(order['currency'], order['asset']))
                order['result'] = '0'
                break
            except:
                tries = tries + 1
                tb = traceback.format_exc()
                logger.logError(tb)
                sleep(4)
                self.connect()
        if order.get('result') is None:
            order['result'] = 'Failure'
