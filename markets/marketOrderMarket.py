import traceback
from abc import abstractmethod
from asyncio import sleep

from debug import bank
import logger
from markets.marketBaseClass import marketBaseClass


class marketOrderMarket(marketBaseClass):
    @abstractmethod
    def getCurrentPrice(self, asset, currency):
        pass;

    @abstractmethod
    def marketBuy(self, orderSize, asset, currency, note):
        pass

    @abstractmethod
    def marketSell(self, orderSize, asset, currency, note):
        pass

    def makeOrder(self,order):
        try:
            currentAmount = self.getAmountOfItem(order['asset'], order['currency'])
            text = "current amount of %s%s: %f \n  %s" % (order['asset'], order['currency'], currentAmount, type)
            print(text)
            bank.logNote(text)

            if currentAmount != 0:
                self.marketBuy(-currentAmount, order['asset'], order['currency'], note='Resetting to equilibrium')
            orderSize = self.getAmountOfItem(order['asset'], order['currency'],orderType=order['action']) * 0.4
            if type == self.buyText:
                result = self.marketBuy(orderSize, order['asset'], order['currency'], note='Going long')
                bank.logContract(order['asset'], order['currency'], self.getAmountOfItem(order['asset'], order['currency']))
            else:
                if type == self.sellText:
                    result = self.marketSell(orderSize, order['asset'], order['currency'], note='Going short')
                    bank.logContract(order['asset'], order['currency'], self.getAmountOfItem(order['asset'], order['currency']))
            return True
        except:
            blue = 5
            # tb = traceback.format_exc()
            # logger.logError(tb)
            # if self.attemptsLeft == 0:
            #     self.attemptsLeft = self.attemptsTotal
            #     return None
            # sleep(self.delayBetweenAttempts)
            # self.connect()
            # self.attemptsLeft = self.attemptsLeft - 1
            # self.marketOrder(type, asset, currency)





