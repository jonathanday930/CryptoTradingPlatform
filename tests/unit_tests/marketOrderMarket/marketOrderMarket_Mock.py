from markets.marketOrderMarket import marketOrderMarket



class marketOrderMarket_Mock(marketOrderMarket):
    prices = None
    amounts = None

    pricingFile = "prices.txt"
    amountsFile = "amounts.txt"

    logFile = "testLog.txt"
    commandList = []

    def __init__(self, realMoney, name, *args):
        super().__init__(realMoney, name, *args)
        self.pricingFile = args[0]
        self.amountsFile = args[1]


    def connect(self):
        self.prices = open(self.pricingFile)
        self.amounts = open(self.amountsFile)
        # self.commandList.append("Connected")

    def getAmountOfItem(self, val1, val2=None, orderType=None):
        amount = int(self.amounts.readline(30))
        # self.commandList.append("Got amount: " + str(amount))
        return amount

    def interpretType(self, type):
        # self.commandList.append("Interpret type for: " + str(type))
        pass

    def getCurrentPrice(self, val1, val2=None):
        price = self.prices.readline(30)
        price = int(price)
        # self.commandList.append("Got price: " + str(price))
        return price

    def marketBuy(self, orderQuantity, asset, currency, note=None):
        self.commandList.append({'asset': asset, 'currency': currency, 'orderQuantity': orderQuantity, 'note': note, 'type':self.buyText})

    def marketSell(self, orderQuantity, asset, currency, note=None):
        self.commandList.append({'asset': asset, 'currency': currency, 'orderQuantity': orderQuantity, 'note': note, 'type':self.sellText})
