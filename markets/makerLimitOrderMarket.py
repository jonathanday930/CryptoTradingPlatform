import collections
import math
import traceback
from abc import abstractmethod
from asyncio import sleep

import recording.logger
from recording import logger
from markets.marketBaseClass import marketBaseClass


class makerLimitOrderMarket(marketBaseClass):
    """ A class to manage making a maker type limit order on the market. Involved changing the price so that it is as close to the price as possible to be fulfilled fast enough, but
    also will cancel if the price deviates enough
    """
    maximumDeviationFromPrice = 0.02

    def __init__(self, marketApiKey, marketApiKeySecret, realMoney, name):
        super().__init__(marketApiKey, marketApiKeySecret, realMoney, name)
        self.delayBetweenAttempts = None

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
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        """
        Sends a limit order to buy at a given price. If a limit order has already been put in place, orderNumber will not be None, and
        instead of sending in a new order, this function simply updates it to match the limitPrice.

        In other words, it sends in an order, and if an order is already in place, changes the price.

        :param limitPrice: The price, a decimal
        :param asset: The asset, a string
        :param currency:  The currency, a string
        :param orderQuantity:  The quantity, a decimal
        :param orderNumber:  (Default value = None) The orderNumber of the current limit order, if None, then create a new order. If not, change the price on the exchange.
        :param note:  (Default value = None)

        """
        pass

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        """

        Sends a limit order to sell at a given price. If a limit order has already been put in place, orderNumber will not be None, and
        instead of sending in a new order, this function simply updates it to match the limitPrice.

        In other words, it sends in an order, and if an order is already in place, changes the price.

        :param limitPrice: The price, a decimal
        :param asset: The asset, a string
        :param currency:  The currency, a string
        :param orderQuantity:  The quantity, a decimal
        :param orderNumber:  (Default value = None) The orderNumber of the current limit order, if None, then create a new order. If not, change the price on the exchange.
        :param note:  (Default value = None)

        """
        pass

    @abstractmethod
    def closeLimitOrders(self, asset, currency):
        """
        Cancells the limit orders for an asset and currency pair if they are still open.

        :param asset: The asset, a string
        :param currency: The currency, a string

        """
        pass;

    @abstractmethod
    def getOrderBook(self, asset, currency):
        """
        Gets the order book of the market, which lists the asks around the current price. This will be used to calculate
        the price that is one tick below the current price, so that a maker order closest to the price can be maintained for fastest fulfillment.
        :param asset: The asset, a string
        :param currency: The currency, a string

        """
        pass

    @abstractmethod
    def orderCanceled(self, orderID):
        """
        Checks to see if an order has been cancelled.
        :param orderID:  The order ID

        """
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        """
        Cancells a particular limit order.
        :param orderID: The order id, a string

        """
        pass


    @abstractmethod
    def quantityLeftInOrder(self, orderID, orderQuantity=None):
        """
        Finds the quantity left in an order. If the orderID is None or the order is not valid, then return orderQuantity.
        :param orderID: The order id, a string
        :param orderQuantity:  (Default value = None)

        """
        pass

    @abstractmethod
    def extractMakerLimitPrice(self, type, asset, currency):
        """
        Extracts the maker limit price from the market. In implementing this, call getOrderBook and then get the price closest
        to the price that isnt a taker order.

        :param type: Either marketBaseClass.buyText, or marketBaseClass.sellText
        :param asset: The asset, a string
        :param currency: The currency, a string

        """
        pass

    @abstractmethod
    def orderOpen(self, orderID):
        """
        Checks if an order is still open

        :param orderID: The order id, a string

        """
        pass

    @abstractmethod
    def getOrderPrice(self, orderID):
        """
        Gets the received price of an order. This is useful because if a market receives a certain price and truncates it to
        fit a tick amount (like every 0.5) then it is good to get the price the market is using.
        :param orderID: The orderID, a string

        """
        pass

    def getLimit(self, type, price, percent):
        """
        Returns either a percent above or percent below the price

        :param type: Either marketBaseClass.buyText, or marketBaseClass.sellText
        :param price: 
        :param percent: 

        """
        if type == self.buyText:
            value = price * (1 + percent)
            return value
        else:
            if type == self.sellText:
                value = price * (1 - percent)
                return value

    def isInRange(self, type, firstPrice, currentPrice, percent, enabled=True):
        """
         Checks if the current price has deviated too far from the original ordered price.

        :param type: Either marketBaseClass.buyText, or marketBaseClass.sellText
        :param firstPrice: The first price when the order was received, a decimal.
        :param currentPrice: The current price, a decimal
        :param percent: A decimal
        :param enabled:  (Default value = True) If False, then returns True. Used in makeOrder

        """
        if enabled and currentPrice is not None:
            if type == self.buyText:
                value = self.getLimit(type, firstPrice, percent) > currentPrice
                return value
            else:
                if type == self.sellText:
                    value = self.getLimit(type, firstPrice, percent) < currentPrice
                    return value
        else:
            return True

    def sendLimitOrder(self, type, asset, currency, orderQuantity, orderID, note=None, currentLimitPrice=None):
        """
        Sends a limit order.

        :param type: Either marketBaseClass.buyText, or marketBaseClass.sellText
        :param asset: The asset, a string
        :param currency: A string
        :param orderQuantity: A decimal
        :param orderID: A string
        :param note:  (Default value = None) A string or None
        :param currentLimitPrice:  (Default value = None) The current price of the limit order, if there is an order open.

        """

        result = collections.namedtuple('result', ['limitPrice', 'orderID'])
        res = result(currentLimitPrice, orderID)

        limitPrice = self.extractMakerLimitPrice(type, asset, currency)

        if limitPrice != currentLimitPrice or orderID is None:
            if type == self.buyText:
                orderID = self.limitBuy(limitPrice, asset, currency, orderQuantity, orderID, note)
            else:
                if type == self.sellText:
                    orderID = self.limitSell(limitPrice, asset, currency, orderQuantity, orderID, note)

            if not self.orderCanceled(orderID):
                limitPrice = self.getOrderPrice(orderID)
                res = result(limitPrice, orderID)
            else:
                res = None

        if not self.orderOpen(orderID):
            res = None
        return res

    def initializeLimitOrder(self, order):
        """
        Initializes the limit order process.

        :param order: The order dict, specified in strategy

        """
        # order['type'] = self.interpretType(order['type'])

        amount = 0

        if not order.get('equilibrium'):
            amount = self.getAmountOfItem(str(order['currency']), str(order['asset']))
            order['equilibriumQuantity'] = amount
            if amount > 0 and order['action'] == self.sellText:
                order['currentAction'] = self.sellText
            else:
                if amount < 0 and order['action'] == self.buyText:
                    order['currentAction'] = self.buyText

        amount = abs(amount)

        if amount == 0:
            order['equilibrium'] = True
            order['currentAction'] = order['action']

            if 'amount' in order:
                amount = order['amount']
            else:
                # TODO: This should not be here long term. Amounts need to be taken care of in strategy.
                if order['asset'] == 'USD':
                    amount = (self.getAmountOfItem(order['currency']) * self.getCurrentPrice(order['currency'],
                                                                                             order['asset'])) * .4
                else:
                    amount = (self.getAmountOfItem('xbt') / self.getCurrentPrice(order['currency'],
                                                                                 order['asset'])) * .4

        order['initialPrice'] = self.getCurrentPrice(order['currency'], order['asset'])
        order['initialized'] = True
        order['orderQuantity'] = amount

    def makeOrder(self, order):
        """
        Makes the order happen, and when called in the future checks the status.

        :param order: The order dict, specified in strategy

        """
        tryMaxCount = 7
        tries = 0
        while tries < tryMaxCount:
            try:
                if not order.get('initialized'):
                    #TODO: Allow option to not reach equilibrium
                    self.initializeLimitOrder(order)

                if order.get('completed'):
                    # logger.logDuplicateOrder(order)
                    return None

                order['orderQuantity'] = min(
                    abs(self.quantityLeftInOrder(order.get('orderID'), math.inf)),
                    abs(order.get('orderQuantity', math.inf)))

                if self.isInRange(order['currentAction'], order['initialPrice'],
                                  self.getCurrentPrice(order['currency'], order['asset']),
                                  self.maximumDeviationFromPrice,
                                  order['equilibrium']) and order.get('orderQuantity') != 0:
                    res = self.sendLimitOrder(order['currentAction'], order['asset'], order['currency'],
                                              order['orderQuantity'],
                                              order.get('orderID'),
                                              order.get('note'),
                                              currentLimitPrice=order.get('currentLimitPrice'))
                    if hasattr(res, 'orderID'):
                        order['orderID'] = res.orderID
                        order['currentLimitPrice'] = res.limitPrice
                    else:
                        order['orderQuantity'] = self.quantityLeftInOrder(order['orderID'], order['orderQuantity'])
                        orderID = order['orderID']
                        order['orderID'] = None
                        self.closeLimitOrder(orderID)
                else:
                    if self.orderOpen(order['orderID']):
                        self.closeLimitOrder(order['orderID'])
                    self.finishOrderStep(order)

                break
            except:
                tries = tries + 1
                tb = traceback.format_exc()
                logger.logError(tb)
                sleep(self.delayBetweenAttempts)
                self.connect()

    def finishOrderStep(self, order):
        """
        Finalizes an order.

        :param order: The order dict, specified in strategy

        """
        if not order['equilibrium']:
            order['equilibrium'] = True
            order['initialized'] = False
            self.logOrderInBank(order, action=order['currentAction'], orderAmount=order['equilibriumQuantity'],
                                orderPrice=order.get('currentPrice'))

        else:
            if not order.get('completed'):
                order['completed'] = True
                order['result'] = '0'
                self.logOrderInBank(order, action=order['action'], orderAmount=order['amount'],
                                    orderPrice=order.get('currentPrice'))

        logger.logCompletedOrder(self.marketName, ' Maker Limit ',
                                 order.get('previousOrderPrice', -9999),
                                 order.get('initialPrice', -69), order['action'], order['asset'],
                                 order['currency'], note=order.get('note'))
