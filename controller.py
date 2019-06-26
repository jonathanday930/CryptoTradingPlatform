import time

from markets.livetest.livetest import livetest
from recording import bank
from markets.bitmex.Bitmex import Bitmex

import os

import json


class controller:
    marketControllers = {}
    marketOrderPercent = 0.4
    real_money = False
    marginFromPrice = None
    maximumDeviationFromPrice = None
    goodLimitThreshold = None

    def __init__(self, priceMargin, maximum, realMoney):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum
        self.timeOutTime = -1
        self.real_money = realMoney

        self.strategies = {}

    def run(self):
        for market in self.marketControllers:
            self.marketControllers[market].connect()
        currentOrders = []
        while True:
            for strategy in self.strategies.values():
                newOrders = strategy.runStrategy(self.marketControllers)
                for order in newOrders:
                    order['strategy'] = strategy.strategyName
                self.removeDuplicateOrders(newOrders, currentOrders)
                currentOrders.extend(newOrders)

            self.processOrders(currentOrders)
            time.sleep(5)

    def processOrders(self, currentOrders):
        for order in currentOrders:
            if order['market'].upper() in self.marketControllers:
                self.marketControllers[order['market'].upper()].makeOrder(order)

        for order in currentOrders[:]:
            if 'result' in order:
                # TODO: LOG FUNCTION
                self.strategies[order['strategy']].finalizeOrder(order)
                currentOrders.remove(order)
                # TODO: make bank updates correctly done
                bank.updateAllBalances()

    def removeDuplicateOrders(self, newOrders, orders):
        for newOrder in newOrders[:]:
            if 'id' in newOrder:
                for order in orders:
                    if 'id' in order:
                        if order['id'] == newOrder['id'] and order['strategy'] == newOrder['strategy']:
                            newOrders.remove(newOrder)

    def importAPIKeys(self):
        folder = 'API_KEYS/'
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                f = open('./' + folder + filename)
                with open(f.name) as jsonFile:
                    data = json.load(jsonFile)
                    for keySet in data['API_Keys']:
#TODO allow for multiple markets of the same type but different name
                        if keySet['market'] == 'BITMEX':
                            if keySet['real_money'] == self.real_money:
                                self.addMarket(
                                    Bitmex( keySet['real_money'], keySet['name'],keySet['keyID'], keySet['privateKey']),
                                    keySet['market'])
                        else:
                            if keySet['market'] == 'LIVETEST':
                                self.addMarket(livetest(keySet['real_money'],keySet['name'],keySet['key']),keySet['market'] )
                continue
            else:
                continue

        # for
        # with open('./API_KEYS/*.json') as f:
        #     data = json.load(f)

    def addMarket(self, market, name):
        market.marginFromPrice = self.marginFromPrice
        market.maximumDeviationFromPrice = self.maximumDeviationFromPrice
        self.marketControllers[name] = market

    def addStrategy(self, strategy):
        self.strategies[strategy.strategyName] = strategy

    def marketOrder(self, market, asset, currency, type):

        if type == 'LONG':
            return market.marketOrder('buy', asset, currency)
        else:
            return market.marketOrder('sell', asset, currency)
