import time

# from markets.livetest.livetest import livetest
from recording import bank
from markets.bitmex.Bitmex import Bitmex

import os

import json


class controller:
    """ This class controlls everything. It asks strategy type files to determine if it is time to buy/sell,
    and then sends orders to market type classes to send orders to the market."""
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
        """ Runs continuously. Has the markets connect to their crypto markets and then loops through the current strategies. When a strategy sends in
        an order, it handles sending the order to the market. A market may immediately finish the order, or in other cases (like maker limit orders) it wont, and will
        keep getting updated every loop iteration. """
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
        """

        :param currentOrders: The list of current orders that have not been filled.

        """
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
        """
        Checks if this order is a duplicate order. With some strategies implemented, such as gmail, the same order can
        be submitted multiple times. This makes sure that only one order is carried out per order.

        :param newOrders: The new orders that just got submitted, that need to be validated.
        :param orders: The current orders that the controller has that have not been fulfilled completely yet.

        """
        for newOrder in newOrders[:]:
            if 'id' in newOrder:
                for order in orders:
                    if 'id' in order:
                        if order['id'] == newOrder['id'] and order['strategy'] == newOrder['strategy']:
                            newOrders.remove(newOrder)

    def importAPIKeys(self):
        """ Imports API keys from json files in the API_KEYS folder"""
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
        """
        Adds a market to the controller's list of markets to use.

        :param market: A child of marketBaseClass
        :param name: The name of this market instance, which is arbitrary (could be 'Jday's_Bitmex').

        """
        market.marginFromPrice = self.marginFromPrice
        market.maximumDeviationFromPrice = self.maximumDeviationFromPrice
        self.marketControllers[name] = market

    def addStrategy(self, strategy):
        """
        Adds a strategy to the controller's list of currently enabled strategies.

        :param strategy: A child of the strategy class.

        """
        self.strategies[strategy.strategyName] = strategy

    # def marketOrder(self, market, asset, currency, type):
    #     """
    #
    #     :param market:
    #     :param asset:
    #     :param currency:
    #     :param type:
    #
    #     """
    #
    #     if type == 'LONG':
    #         return market.marketOrder('buy', asset, currency)
    #     else:
    #         return market.marketOrder('sell', asset, currency)
