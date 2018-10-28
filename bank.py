import datetime
import market


def getBankFile():
    file = open("bank.txt", 'a')
    return file


def logBalance(availableBalance, exchangeName):
    file = getBankFile()
    text = format("Exchange: %s:\nAvalable balance: %s\nTime: %s\n\n" % (exchangeName,
                                                                         str(availableBalance),
                                                                         str(datetime.datetime.now())))
    file.write(text)
    file.close()


def logContract(asset, currency, amount, exchangeName):
    file = getBankFile()
    text = str("Exchange: %s:\nCoin: %s\nAmount: %d\nTime: %s\n\n" % (exchangeName,
                                                                      asset+currency,
                                                                      amount,
                                                                      str(datetime.datetime.now())))
    file.write(text)
    file.close()

def logNote(note):
    file = getBankFile()
    file.write(str(datetime.datetime.now()) + " - " + note + "\n")
    file.close()

