import collections
import math
import traceback
from abc import abstractmethod
from asyncio import sleep

import debug.logger
from debug import logger
from markets.limitOrderMarket import limitOrderMarket
from markets.marketBaseClass import marketBaseClass


class makerLimitOrderMarket(limitOrderMarket):
    maximumDeviationFromPrice = None

    @abstractmethod
    def closeLimitOrders(self, asset, currency):
        pass;

    @abstractmethod
    def getOrderBook(self, asset, currency):
        pass

    @abstractmethod
    def orderCanceled(self, orderID):
        pass

    @abstractmethod
    def limitOrderStatus(self, orderID):
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        pass

    @abstractmethod
    def orderisOpen(self, orderID):
        pass

    @abstractmethod
    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    @abstractmethod
    def getOrderPrice(self, orderID):
        pass

    @abstractmethod
    def getOrderBook(self, asset, currency):
        pass

    @abstractmethod
    def extractMakerLimitPrice(self, type, asset, currency):
        pass

    @abstractmethod
    def orderCanceled(self, orderID):
        pass

    @abstractmethod
    def limitOrderStatus(self, orderID):
        pass

    @abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def closeLimitOrder(self, orderID):
        pass

    @abstractmethod
    def orderOpen(self, orderID):
        pass

    @abstractmethod
    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    @abstractmethod
    def getOrderPrice(self, orderID):
        pass

    def getLimit(self, type, price, percent):
        if type == self.buyText:
            value = price * (1 + percent)
            return value
        else:
            if type == self.sellText:
                value = price * (1 - percent)
                return value

    def isInRange(self, type, firstPrice, currentPrice, percent, enabled=True):
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

    def sendLimitOrder(self, type, asset, currency, orderQuantity, orderID, note=None, previousLimitPrice=None):

        result = collections.namedtuple('result', ['limitPrice', 'orderID'])
        res = result(previousLimitPrice, orderID)

        limitPrice = self.extractMakerLimitPrice(type, asset, currency)

        if limitPrice != previousLimitPrice or orderID is None:
            if type == self.buyText:
                orderID = self.limitBuy(limitPrice, asset, currency, orderQuantity, orderID, note)
            else:
                if type == self.sellText:
                    orderID = self.limitSell(limitPrice, asset, currency, orderQuantity, orderID, note)

            if not self.orderCanceled(orderID):
                limitPrice = self.getOrderPrice(orderID)
                result = collections.namedtuple('result', ['limitPrice', 'orderID'])
                res = result(limitPrice, orderID)
            else:
                res = None

        if not self.orderOpen(orderID):
            res = None
        return res

    def initializeLimitOrder(self, order):
        # order['type'] = self.interpretType(order['type'])

        amount = 0

        if not order['equilibrium']:
            amount = self.getAmountOfItem(str(order['currency']), str(order['asset']))

            # if we are already in a short we wont be shorting more. Current position of way we do things.
            if amount < 0 and order['action'] == self.sellText:
                order['completed'] = True
            else:
                if amount > 0 and order['action'] == self.buyText:
                    order['completed'] = True
                else:
                    if amount > 0:
                        order['currentAction'] = self.sellText
                        order['orderQuantity'] = amount
                    else:
                        if amount < 0:
                            order['currentAction'] = self.buyText
                            order['orderQuantity'] = amount


            amount = abs(amount)

        if amount == 0:
            order['equilibrium'] = True
            # noinspection PyTypeChecker
            #TODO: Change to take amount from order info
            amount = abs(self.getAmountOfItem(order['currency'], order['asset']) * 0.4)

        order['initialized'] = True
        order['orderQuantity'] = amount
        order['initialPrice'] = self.getCurrentPrice(order['asset'], order['currency'])

    def makeOrder(self, order):
        tryMaxCount = 7
        tries = 0
        while tries < tryMaxCount:

            try:
                if not order.get('initialized'):
                    self.initializeLimitOrder(order)

                if order.get('completed') == True:
                    # logger.logDuplicateOrder(order)
                    return None

                order['orderQuantity'] = min(
                    abs(self.quantityLeftInOrder(order.get('orderID', math.inf))),
                    abs(int(order.get('orderQuantity', math.inf))))

                if self.isInRange(order['action'], order['initialPrice'], order.get('previousLimitPrice',
                                                                                    self.getCurrentPrice(order['asset'],
                                                                                                         order[
                                                                                                             'currency'])),
                                  self.maximumDeviationFromPrice,
                                  order['equilibrium']) and order.get('orderQuantity') != 0:
                    res = self.sendLimitOrder(order['currentAction'], order['asset'], order['currency'],
                                              order['orderQuantity'],
                                              order.get('orderID'),
                                              order.get('note'),
                                              previousLimitPrice=order.get('previousLimitPrice'))
                    if hasattr(res, 'orderID'):
                        order['orderID'] = res.orderID
                        order['previousOrderPrice'] = res.limitPrice
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
        if not order['equilibrium']:
            order['equilibrium'] = True
            order['initialized'] = False
        else:
            if not order['completed']:
                order['completed'] = True

        logger.logCompletedOrder(self.marketName, ' Maker Limit ',
                                 order.get('previousOrderPrice', -9999),
                                 order.get('initialPrice', -69), order['action'], order['asset'],
                                 order['currency'], note=order['note'])
