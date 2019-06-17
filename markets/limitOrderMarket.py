import math
from abc import abstractmethod

from markets.marketBaseClass import marketBaseClass


class limitOrderMarket(marketBaseClass):


    attemptsTotal = 10
    attemptsLeft = attemptsTotal
    delayBetweenAttempts = 6
    delayBetweenLimitOrder = 5


    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def getAmountOfItem(self, val1, val2=None, orderType=None):
        pass

    def initializeLimitOrder(self, order):
        # order['type'] = self.interpretType(order['type'])

        amount = 0

        if not order.get('equilibrium'):
            # noinspection PyTypeChecker
            amount = self.getAmountOfItem(str(order['currency']), str(order['asset']))

            # if we are already in a short we wont be shorting more. Current position of way we do things.
            if amount < 0 and order['action'] == self.sellText:
                order['completed'] = True
            else:
                if amount > 0 and order['action'] == self.buyText:
                    order['completed'] = True
            amount = abs(amount)

        if amount == 0:
            order['equilibrium'] = True
            # noinspection PyTypeChecker
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

                order['orderQuantity'] = min(abs(self.quantityLeftInOrder(order.get('orderID', math.inf))),
                    abs(int(order.get('orderQuantity', math.inf))))

                if order.get('orderQuantity') != 0:
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


@abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass

    @abstractmethod
    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass
