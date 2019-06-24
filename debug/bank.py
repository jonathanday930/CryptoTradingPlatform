import collections
import datetime
import json
import math
import os
import traceback
import copy
from os import path

from recordtype import recordtype

from debug import logger
from markets.marketBaseClass import marketBaseClass

orderBookLocation = 'logs'

bankFile = 'bank.txt'
allTradeFileName = 'allTrades.json'
pairsFilename = 'pairs.json'
balanceFilename = 'balance.json'

calculateChange = lambda firstPrice, secondPrice: ((secondPrice - firstPrice) / firstPrice)



def sign(number):
    if number < 0:
        return -1
    else:
        if number > 0:
            return 1
        else:
            return 0


def trimDict(transactionStatement):
    for key in transactionStatement:
        if key not in ['time', 'action', 'price', 'amount', 'note', 'market', 'asset', 'currency', "action-type"]:
            del transactionStatement[key]


def createDirectoryForTransaction(transactionStatement):
    try:
        os.makedirs('logs/' + str(transactionStatement['market']) + '/' + str(transactionStatement['currency']) +
                    str(transactionStatement['asset']) + '/')
    except FileExistsError:
        pass


def readJsonFile(file):
    try:
        with open(file, 'r') as log_json:
            data = json.load(log_json)
    except Exception as error:
        data = []
        logger.logError(error)
    return data


def logTransaction(transactionStatement):
    trimDict(transactionStatement)
    getCorrectSignForRecord(transactionStatement)

    transactionStatement['time'] = str(datetime.datetime.now())

    createDirectoryForTransaction(transactionStatement)

    jsonFile = orderBookLocation + '/' + transactionStatement['market'] + '/' + transactionStatement['currency'] + \
               transactionStatement['asset'] + '/' + allTradeFileName
    data = readJsonFile(jsonFile)
    transactionStatement['count'] = len(data)
    data.append(transactionStatement)
    overwriteJsonFile(jsonFile, data)


def overwriteJsonFile(file, jsonValue):
    with open(file, 'w+') as log_json:
        json.dump(jsonValue, fp=log_json)


def updateAllBalances():
    for root, dirs, files in os.walk(orderBookLocation + '/', topdown=False):
        for name in dirs:
            dirPath = os.path.join(root, name)
            if dirPath.count('/') == 1:
                updateMarketBalanceFromDir(dirPath)


def getCorrectSignForRecord(record):
    if record['action'] == marketBaseClass.sellText:
        record['amount'] = - abs(record['amount'])
    else:
        record['amount'] = abs(record['amount'])


def calculateProfit(oldTrans, newTrans, amount, initialAction):
    change = calculateChange(oldTrans['price'], newTrans['price'])

    if initialAction == marketBaseClass.sellText:
        monetaryChange = abs(amount) * (- change)
    else:
        monetaryChange = abs(amount) * change
    return monetaryChange


def updatePairBalance(pairPath):
    maxBalance = -math.inf
    data = readJsonFile(pairPath + '/' + allTradeFileName)
    balance = {'currentBal': 0,
               'totalProfits': 0,
               'maxBalance':-math.inf,
               'balanceDecomposition': []
               }
    # balanceDecompEntry = record with key for closers
    # closer = record with profit and amount traded in that transaction

    finishedPairs = []

    for record in data:
        if abs(balance['currentBal']) > abs(balance['maxBalance']):
            balance['maxBalance'] = abs(balance['currentBal'])

        if balance['currentBal'] == 0 and len(balance['balanceDecomposition']) == 0:
            balance['currentBal'] = record['amount']
            record['closers'] = []
            balance['balanceDecomposition'].append(copy.deepcopy(record))
        else:
            if sign(record['amount']) == sign(balance['currentBal']):
                balance['currentBal'] = balance['currentBal'] + record['amount']
                record['closers'] = []
                balance['balanceDecomposition'].append(record)
            else:
                changeAmount = record['amount']
                while changeAmount != 0 and len(balance['balanceDecomposition']) > 0:
                    oldTrans = getOldestTransaction(balance['balanceDecomposition'])
                    recordCopy = copy.deepcopy(record)
                    newTransBalance = oldTrans['amount'] + record['amount']

                    if sign(newTransBalance) == 0:
                        amountChanged = changeAmount
                        changeAmount = 0
                        finishedPairs.append(oldTrans)
                        balance['balanceDecomposition'].remove(oldTrans)
                    else:
                        if sign(newTransBalance) == sign(oldTrans['amount']):
                            # Then the record only accounts for a part of old trans amount
                            oldTrans['amount'] = newTransBalance
                            amountChanged = newTransBalance
                            changeAmount = 0
                        else:
                            changeAmount = newTransBalance
                            amountChanged = oldTrans['amount']
                            finishedPairs.append(oldTrans)
                            balance['balanceDecomposition'].remove(oldTrans)

                    recordCopy['profit'] = calculateProfit(oldTrans, recordCopy, amountChanged, oldTrans['action'])
                    balance['totalProfits'] += recordCopy['profit']
                    oldTrans['closers'].append(recordCopy)
                    balance['currentBal'] = sign(balance['currentBal']) * (
                                abs(balance['currentBal']) - abs(amountChanged))

                if len(balance['balanceDecomposition']) == 0 and changeAmount != 0:
                    balance['currentBal'] = changeAmount
                    record['closers']=[]
                    balance['balanceDecomposition'] = [record]
    calculatePairProfits(finishedPairs)
    overwriteJsonFile(pairPath + '/' + balanceFilename, balance)
    overwriteJsonFile(pairPath + '/' + pairsFilename, finishedPairs)


def calculatePairProfits(pairs):
    for pair in pairs:
        profitAmount = 0
        for closer in pair['closers']:
            profitAmount += closer['profit']
        pair['profitPercent'] = profitAmount/abs(pair['amount'])
        pair['totalprofits'] = profitAmount

def updateMarketBalanceFromDir(marketPath):
    for root, dirs, files in os.walk(marketPath, topdown=False):
        for name in dirs:
            pairPath = os.path.join(root, name)
            if pairPath.count('/') == 2:
                updatePairBalance(pairPath)



def getOldestTransaction(balanceDecomp):
    max = {'count': math.inf}
    for transaction in balanceDecomp:
        if transaction['count'] < max['count']:
            max = transaction
    return max


