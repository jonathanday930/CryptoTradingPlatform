import datetime


logFile = 'log.txt'


def getLogFile():
    return open(logFile, 'a')



def logOrder(exchange, orderType, price, asset, currency, amount, note=None):
    file = getLogFile()
    file.write(exchange +' '+ orderType + ' order at ' + str(datetime.datetime.now()) + ' : ' + str(amount) + ' of pair ' + str(
        asset) + str(currency) + ' at price ' + str(price) + ' Note: ' + str(note) + '\n')


def logCompletedOrder(exchange, orderType, price,initialPrice, asset, currency, note=None):
    file = getLogFile()
    difference = initialPrice - price
    percentChange = abs(100 * ((price - initialPrice)/initialPrice) )
    outputText = 'COMPLETED ORDER: ' + exchange + ' ' + orderType + ' order at ' + str(datetime.datetime.now()) + ' : of pair ' + str(
        asset) + str(currency) + ' final price: ' + str(price) + " initial price:  " + str(initialPrice) + ' price difference: ' + str(difference) + ' percent: ' +  str(percentChange) + '% Note: ' + str(note) + '\n'
    file.write(outputText)




def logError(exception):
    file = getLogFile()
    file.write('ERROR: \n')
    file.write(str(exception) + '\n')
    file.write('----- \n')
