import datetime
import market


class bank():
    daMattress = "bank.txt"
    file = open(daMattress, "a")
    market = market(ABC)

    def getFile(self):
        file = open(logFile, 'a')
        return file

    def logBalance(asset, currency):
        getFile()
        file.write(
            exchange + orderType + ' order at ' + datetime.datetime.now() + ': ' + str(amount) + ' of pair ' + str(
                asset) + str(currency) + ' at price ' + str(price) + 'Note: ' + str(note))

    def logContract(self, asset, currency):
        getFile()
        file.write('ERROR: ')
        file.write(str(exception))
        file.write('-----')

    def getAmountOfItem(asset, currency=None):
        market.getAmountOfItem(asset + currency)


