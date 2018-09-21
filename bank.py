import datetime
import market


def getBankFile():
    file = open("bank.txt", 'a')
    return file


def logBalance(availableBalance):
    file = getBankFile()
    file.write(str(datetime.datetime.now()) + ' - Available Balance: ' + str(availableBalance) + "\n\n")


def logContract(asset, currency, amount):
    file = getBankFile()
    file.write(str(datetime.datetime.now()) + ' - Amt Of ' + str(asset + currency) + ": " + str(amount))

