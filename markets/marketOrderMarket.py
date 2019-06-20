import traceback
from abc import abstractmethod
from asyncio import sleep

from debug import bank
from debug import logger
from markets.marketBaseClass import marketBaseClass


class marketOrderMarket(marketBaseClass):

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
    def marketBuy(self, orderQuantity, asset, currency, note=None):
        pass

    @abstractmethod
    def marketSell(self, orderQuantity, asset, currency, note=None):
        pass

    def makeOrder(self, order):
        tries = 0
        maxTries = 7
        while tries < maxTries:

            try:
                currentAmount = self.getAmountOfItem(order['currency'], order['asset'])
                text = "current amount of %s%s: %f \n " % (order['currency'], order['asset'], currentAmount)
                print(text)

                if currentAmount > 0 and order['action'] == self.sellText or currentAmount < 0 and order['action'] == self.buyText:
                    self.marketBuy(-currentAmount, order['currency'], order['asset'], note='Resetting to equilibrium')
                    self.logOrderInBank(order, action=self.buyText if -currentAmount > 0 else self.sellText,
                                        orderAmount=abs(currentAmount),
                                        orderPrice=self.getCurrentPrice(order['currency'], order['asset']))

                # TODO: This should not be here long term
                if order['asset'] == 'USD':
                    orderSize = (self.getAmountOfItem('xbt') * self.getCurrentPrice(order['currency'],
                                                                                    order['asset'])) * .4
                else:
                    orderSize = (self.getAmountOfItem('xbt') / self.getCurrentPrice(order['currency'],
                                                                                    order['asset'])) * .4

                if order['action'] == self.buyText:
                    result = self.marketBuy(orderSize, order['currency'], order['asset'], note='Going long')
                    self.logOrderInBank(order, action=self.buyText, orderAmount=self.getAmountOfItem(order['currency'], order['asset']),
                                        orderPrice=self.getCurrentPrice(order['currency'], order['asset']))
                else:
                    if order['action'] == self.sellText:
                        result = self.marketSell(orderSize, order['currency'], order['asset'], note='Going short')
                        self.logOrderInBank(order, action=self.sellText, orderAmount=self.getAmountOfItem(order['currency'], order['asset']),
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
