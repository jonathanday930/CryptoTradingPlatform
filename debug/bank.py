import collections
import datetime
import json
import os
import traceback
import copy
from os import path

from recordtype import recordtype

from markets.marketBaseClass import marketBaseClass

bankFile = 'bank.txt'

sign = lambda x: (1, -1)[x < 0]
calculateChange = lambda firstPrice, secondPrice: ((secondPrice - firstPrice) / firstPrice)


def getBankFileToAppend():
    file = open(bankFile, 'a')
    return file


def getBankFileLines():
    with open(bankFile) as file:  # Use file to refer to the file object
        return file.readlines()


def logTransaction(transactionStatement):
    try:
        os.makedirs('logs/' + str(transactionStatement['market']) + '/' + transactionStatement['currency'] +
                    transactionStatement['asset'] + '/')
    except FileExistsError:
        pass

    transactionStatement['count'] = len(getBankFileLines())
    try:
        with open('logs/' + str(transactionStatement['market']) + '/all trades.json', 'r') as log_json:
            data = json.load(log_json)
    except:
        data = []
        tb = traceback.format_exc()

    with open('logs/' + str(transactionStatement['market']) + '/all trades.json', 'w+') as log_json:
        transactionStatement['time'] = str(datetime.datetime.now())
        data.append(transactionStatement)
        json.dump(data, fp=log_json)


def updateBalancesAndHistory(balance, historyEntry, amount, transaction, record):
    change = calculateChange(transaction.price, record['price'])
    monetaryChange = (change) * amount

    transaction.profit = transaction.profit + monetaryChange

    balance.totalProfits = balance.totalProfits + monetaryChange
    balance.totalBalance = sign(balance.totalBalance) * (abs(balance.totalBalance) - abs(amount))

    historyEntry.profit = historyEntry.profit + transaction.profit


def updateBalanceHistory(marketName):
    transactionTuple = recordtype('transactionTuple', ['time', 'action', 'price', 'amount', 'profit'])
    balancesTuple = recordtype('balancesTuple', ['balanceDecomp', 'totalProfits', 'totalBalance'])
    if path.exists('logs/' + str(marketName) + '/all trades.json'):

        with open('logs/' + str(marketName) + '/all trades.json', 'r') as log_json:
            orderHistory = json.load(log_json)
            balances = {}
            perCoinHistory = {}
            finishedPairs = {}
            for record in orderHistory:
                if record['currency'] + record['asset'] not in balances:

                    try:
                        os.makedirs('logs/' + str(record['market']) + '/' + record['currency'] +
                                    record['asset'] + '/')
                    except FileExistsError:
                        pass

                    perCoinHistoryEntry = transactionTuple(record['time'], record['action'], record['price'],
                                                           record['amount'], 0)

                    balanceCompEntry = transactionTuple(record['time'], record['action'], record['price'],
                                                        record['amount'],
                                                        0)
                    if balanceCompEntry.action == marketBaseClass.sellText:
                        balanceCompEntry.amount = - abs(balanceCompEntry.amount)
                    else:
                        balanceCompEntry.amount = abs(balanceCompEntry.amount)

                    newBalance = balancesTuple([balanceCompEntry], 0, balanceCompEntry.amount)

                    perCoinHistory[record['currency'] + record['asset']] = [perCoinHistoryEntry]
                    balances[record['currency'] + record['asset']] = newBalance
                    finishedPairs[record['currency'] + record['asset']] = []
                else:

                    perCoinHistoryEntry = transactionTuple(record['time'], record['action'], record['price'],
                                                           record['amount'], 0)

                    thisBalance = balances[record['currency'] + record['asset']]
                    thisHistory = perCoinHistory[record['currency'] + record['asset']]
                    thisFinishedPair = finishedPairs[record['currency'] + record['asset']]

                    if record['action'] == marketBaseClass.sellText:
                        amountChange = - abs(record['amount'])
                    else:
                        amountChange = abs(record['amount'])

                    while amountChange != 0 and len(thisBalance.balanceDecomp) > 0:

                        transaction = getOldestTransaction(thisBalance.balanceDecomp)
                        newBalanceForTransact = transaction.amount + amountChange

                        if newBalanceForTransact == 0:

                            updateBalancesAndHistory(thisBalance, perCoinHistoryEntry, abs(amountChange), transaction,
                                                     record)

                            # We have now accounted for that transaction
                            transaction.amount = 0
                            thisFinishedPair.append(transaction)
                            thisHistory.append(perCoinHistoryEntry)
                            thisBalance.balanceDecomp.remove(transaction)

                            amountChange = 0
                        else:
                            if sign(newBalanceForTransact) != sign(transaction.amount):

                                updateBalancesAndHistory(thisBalance, perCoinHistoryEntry, abs(transaction.amount),
                                                         transaction, record)

                                transaction.amount = 0
                                thisFinishedPair.append(transaction)
                                thisBalance.balanceDecomp.remove(transaction)

                                amountChange = newBalanceForTransact

                            else:
                                if abs(newBalanceForTransact) < abs(transaction.amount):

                                    updateBalancesAndHistory(thisBalance, perCoinHistoryEntry,
                                                             abs(transaction.amount) - abs(transaction.amount),
                                                             transaction,
                                                             record)
                                    transaction.amount = newBalanceForTransact
                                    thisHistory.append(perCoinHistoryEntry)
                                    amountChange = 0
                                else:
                                    if abs(newBalanceForTransact) > abs(transaction.amount):
                                        balanceCompEntry = transactionTuple(record['time'], record['action'],
                                                                            record['price'], record['amount'], 0)

                                        if record['action'] == marketBaseClass.sellText:
                                            perCoinHistoryEntry.amount = - abs(perCoinHistoryEntry.amount)
                                            balanceCompEntry.amount = - abs(balanceCompEntry.amount)
                                        else:
                                            perCoinHistoryEntry.amount = abs(perCoinHistoryEntry.amount)
                                            balanceCompEntry.amount = abs(balanceCompEntry.amount)

                                        thisHistory.append(perCoinHistoryEntry)
                                        thisBalance.balanceDecomp.append(balanceCompEntry)
                                        amountChange = 0
                    if amountChange != 0:
                        print('amountChange not zero')
                        thisBalance.balanceDecomp = [transactionTuple(record['time'], record['action'], record['price'],
                                                                      amountChange, 0)]
                        thisHistory.append(perCoinHistoryEntry)

        calculateTotalBalances(balances)

        outputDictLineByLine(balances, 'balances', marketName)
        outputDictLineByLine(finishedPairs, 'pairs', marketName)
        outputDictLineByLine(perCoinHistory, 'history', marketName)


def calculateTotalBalances(allBalances):
    for coin in allBalances:
        bal = 0
        for transaction in allBalances[coin].balanceDecomp:
            bal = bal + transaction.amount
        allBalances[coin].totalBalance = bal


def outputDictLineByLine(dictionary, typeOfDict, market):
    for key in dictionary:
        with open('logs/' + str(market) + '/' + str(key) + '/' + str(typeOfDict) + '.txt', 'w+') as logFile:
            logFile.writelines([str(line) + "\n" for line in dictionary[key]])


def getOldestTransaction(balanceDecomp):
    max = balanceDecomp[0]
    for transaction in balanceDecomp:
        if transaction.time < max.time:
            max = transaction
    return max
