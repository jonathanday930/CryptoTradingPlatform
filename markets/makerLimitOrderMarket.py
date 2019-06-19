import collections
import math
import traceback
from abc import abstractmethod
from asyncio import sleep

import debug.logger
from debug import logger
from markets.marketBaseClass import marketBaseClass


class makerLimitOrderMarket(marketBaseClass):
    maximumDeviationFromPrice = 0.02

    def __init__(self, marketApiKey, marketApiKeySecret, realMoney, name):
        super().__init__(marketApiKey, marketApiKeySecret, realMoney, name)
        self.delayBetweenAttempts = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def getAmountOfItem(self, val1, val2=None, orderType=None):
        pass

    @abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def getCurrentPrice(self, val1, val2=None):
        pass

    @abstractmethod
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

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
    def quantityLeftInOrder(self, orderID, orderQuantity=None):
        pass

    @abstractmethod
    def extractMakerLimitPrice(self, type, asset, currency):
        pass

    @abstractmethod
    def orderOpen(self, orderID):
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

    def sendLimitOrder(self, type, asset, currency, orderQuantity, orderID, note=None, currentLimitPrice=None):

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
        # order['type'] = self.interpretType(order['type'])

        amount = 0

        if not order.get('equilibrium'):
            amount = self.getAmountOfItem(str(order['currency']), str(order['asset']))
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
                # TODO: This should not be here long term
                if order['asset'] == 'USD':
                    amount = (self.getAmountOfItem(order['currency']) * self.getCurrentPrice(order['currency'],
                                                                                             order['asset'])) * .4
                else:
                    amount = (self.getAmountOfItem('xbt') / self.getCurrentPrice(order['currency'],order['asset'])) * .4

        order['initialPrice'] = self.getCurrentPrice(order['currency'], order['asset'])
        order['initialized'] = True
        order['orderQuantity'] = amount

    def makeOrder(self, order):
        tryMaxCount = 7
        tries = 0
        while tries < tryMaxCount:
            try:
                if not order.get('initialized'):
                    self.initializeLimitOrder(order)

                if order.get('completed'):
                    # logger.logDuplicateOrder(order)
                    return None

                order['orderQuantity'] = min(
                    abs(self.quantityLeftInOrder(order.get('orderID'), math.inf)),
                    abs(order.get('orderQuantity', math.inf)))

                if self.isInRange(order['action'], order['initialPrice'],
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
        if not order['equilibrium']:
            order['equilibrium'] = True
            order['initialized'] = False
        else:
            if not order.get('completed'):
                order['completed'] = True
                order['result'] = '0'
        logger.logCompletedOrder(self.marketName, ' Maker Limit ',
                                 order.get('previousOrderPrice', -9999),
                                 order.get('initialPrice', -69), order['action'], order['asset'],
                                 order['currency'], note=order.get('note'))
