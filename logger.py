import datetime


logFile = 'log.txt'
file = None


def maintainFile():
    file = open(logFile, 'a')
    return file


def logOrder(exchange, orderType, price, asset, currency, amount, note=None):
    maintainFile()
    file.write(exchange + orderType + ' order at ' + datetime.datetime.now() + ': ' + str(amount) + ' of pair ' + str(
        asset) + str(currency) + ' at price ' + str(price) + 'Note: ' + str(note))


def logError(exception):
    maintainFile()
    file.write('ERROR: ')
    file.write(str(exception))
    file.write('-----')
