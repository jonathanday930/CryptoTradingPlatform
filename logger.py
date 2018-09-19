import datetime


logFile = 'log.txt'


def getLogFile():
    return open(logFile, 'a')



def logOrder(exchange, orderType, price, asset, currency, amount, note=None):
    file = getLogFile()
    file.write(exchange + orderType + ' order at ' + str(datetime.datetime.now()) + ': ' + str(amount) + ' of pair ' + str(
        asset) + str(currency) + ' at price ' + str(price) + 'Note: ' + str(note) + '\n')


def logError(exception):
    file = getLogFile()
    file.write('ERROR: \n')
    file.write(str(exception) + '\n')
    file.write('----- \n')
