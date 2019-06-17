import datetime


def getBankFile():
    file = open("bank.txt", 'a')
    return file


def logBalance(availableBalance):
    file = getBankFile()
    text = str(datetime.datetime.now()) + ' - Available Balance: ' + str(availableBalance) + "\n\n"
    file.write(text)
    file.close()


def logContract(asset, currency, amount):
    file = getBankFile()
    text = str(datetime.datetime.now()) + ' - Amt Of ' + str(asset + currency) + ": " + str(amount)
    file.write(text)
    file.close()

def logNote(note):
    file = getBankFile()
    file.write(str(datetime.datetime.now()) + " - " + note + "\n")
    file.close()

