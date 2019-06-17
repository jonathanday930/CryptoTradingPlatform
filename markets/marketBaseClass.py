import collections
import traceback
from decimal import Decimal

from abc import ABC, abstractmethod
from time import sleep

import logger
import bank
import orderDataConstants

from order import order


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
    marketName = ' DEFAULT MARKET '
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
    def getAmountOfItem(self, val1,val2=None,orderType=None):
        pass

    @abstractmethod
    def makeOrder(self,order):
        pass

    @abstractmethod
    def interpretType(self, type):
        pass

    @abstractmethod
    def getCurrentPrice(self,val1,val2=None):
        pass




