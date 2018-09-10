assetSubjectNumber = 0
currencySubjectNumber = 1
typeSubjectNumber = 2
marketSubjectNumber = 3


class controller:
    gmailController = None
    marketControllers = {}

    def __init__(self, gmail):
        self.gmailController = gmail
        self.timeOutTime = -1

    def run(self):
        while True:
            emails = self.gmailController.listen(-1)
            if emails is not None:
                for email in emails:
                    self.createOrder(email)

    def addMarket(self, market, name):
        self.marketControllers[name] = market

    def createOrder(self, email):
        # self.marketControllers['bitmex'].followingLimitOrder(email.parameters[typeSubjectNumber],
        #                                                                                email.parameters[
        #                                                                                    currencySubjectNumber],
        #                                                                                email.parameters[
        #                                                                                    assetSubjectNumber])

        self.marketControllers['bitmex'].marketBuy(20, email.parameters[currencySubjectNumber],
                                                             email.parameters[assetSubjectNumber])

