import logger
from Bitmex import Bitmex
from BinanceTrader import BinanceTrader
from market import market

assetSubjectNumber = 0
currencySubjectNumber = 1
typeSubjectNumber = 2
marketSubjectNumber = 3

import os

import json


class controller:
    gmailController = None
    marketControllers = {}
    marketOrderPercent = 0.4
    real_money = True
    marginFromPrice = None
    maximumDeviationFromPrice = None
    goodLimitThreshold = None

    def __init__(self, gmail, priceMargin, maximum, realMoney):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum
        self.gmailController = gmail
        self.timeOutTime = -1
        self.real_money = realMoney
        self.gmailController.real_money = realMoney

    def run(self):
        for market in self.marketControllers:
            self.marketControllers[market].connect()

        while True:
            emails = self.gmailController.listen(-1)
            if len(emails) != 0:
                for email in emails:
                    result = self.createOrder(email)
                    if result:
                        self.gmailController.setEmailsToRead()


    def importAPIKeys(self):
        folder = 'API_KEYS/'
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                f = open('./' + folder + filename)
                a = f.name
                with open(f.name) as jsonFile:
                    data = json.load(jsonFile)
                    for keySet in data['API_Keys']:
                        if keySet['market'] == 'BITMEX':
                            if keySet['real_money'] == self.real_money:
                                self.addMarket(
                                    Bitmex(keySet['keyID'], keySet['privateKey'], keySet['real_money'], keySet['name']),
                                    keySet['market'])

                        if keySet['market'] == 'BINANCE':
                            apiKey = keySet['keyID']
                            test = BinanceTrader(keySet['keyID'], keySet['privateKey'], keySet['real_money'], keySet['name'])
                            self.addMarket(test, keySet['market'])
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

    def createOrder(self, email):
        market = email.parameters[marketSubjectNumber]
        type = email.parameters[typeSubjectNumber]
        asset = email.parameters[assetSubjectNumber]
        currency = email.parameters[currencySubjectNumber]
        logger.logEmail(market, type, asset, currency)
        if market in self.marketControllers:
            if self.marketControllers[market].limitOrderEnabled:
                return self.marketControllers[market].executeLimitOrder(type, asset, currency)
            else:
                return self.marketOrder(self.marketControllers[market],
                             asset,
                             currency, type)

    def marketOrder(self, market, asset, currency, type):

        if type == 'LONG':
            return market.marketOrder('buy', asset, currency)
        else:
            return market.marketOrder('sell', asset, currency)



