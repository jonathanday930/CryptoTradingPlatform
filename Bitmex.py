from market import market


class Bitmex(market):
    def limitSell(self, price,currency, asset):
        pass

    def limitShortStart(self, price, currency, asset):
        pass

    def limitShortEnd(self, price, currency, asset):
        pass

    def limitBuy(self, price, currency, asset):
        pass

    def getCurrentPrice(self,currency, asset):
        pass

    def closeLimitOrders(self,currency, asset):
        pass

# inherit market
