from Bitmex import Bitmex
from market import market

assetSubjectNumber = 0
currencySubjectNumber = 1
typeSubjectNumber = 2
marketSubjectNumber = 3

import os

import json
from pprint import pprint


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


class controller:
    gmailController = None
    marketControllers = {}
    marketOrderPercent = 0.4
    real_money = False
    marginFromPrice = None
    maximumDeviationFromPrice = None
    goodLimitThreshold = None

    def __init__(self, gmail, priceMargin, maximum, limitThreshold):
        self.marginFromPrice = priceMargin
        self.maximumDeviationFromPrice = maximum
        self.goodLimitThreshold = limitThreshold
        self.gmailController = gmail
        self.timeOutTime = -1

    def run(self):
        for market in self.marketControllers:
            self.marketControllers[market].connect()

        while True:
            emails = self.gmailController.listen(-1)
            if emails is not None:
                for email in emails:
                    self.createOrder(email)

    def setupAPIFiles(self):
        pass

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

                                # '/Users/Desktop/febROSTER2012.xls'

                # print(os.path.join(directory, filename))
                continue
            else:
                continue

        # for
        # with open('./API_KEYS/*.json') as f:
        #     data = json.load(f)

    def addMarket(self, market, name):
        self.marketControllers[name] = market

    def createOrder(self, email):
        # self.marketControllers['bitmex'].followingLimitOrder(email.parameters[typeSubjectNumber],
        #                                                                                email.parameters[
        #                                                                                    currencySubjectNumber],
        #                                                                                email.parameters[
        #                                                                                    assetSubjectNumber])
        market = email.parameters[marketSubjectNumber]
        if market in self.marketControllers:
            self.marketOrder(self.marketControllers[market], self.marketOrderPercent,
                             email.parameters[assetSubjectNumber],
                             email.parameters[currencySubjectNumber], email.parameters[typeSubjectNumber])

    def marketOrder(self, market, percentOfAvailableToUse, asset, currency, type):

        if type == 'LONG':
            market.marketOrder('buy', asset, currency)
        else:
            market.marketOrder('sell', asset, currency)



