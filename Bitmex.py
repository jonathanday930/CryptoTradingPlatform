from market import market

# a controller for ONE bitmex connection. This is a basic formula for how it should look. 
#Feel free to message me about the design.
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
    
    # use this function to handle connecting to the market (this function is the constructor)
    # You should definitely add parameters to this, probably the api key info
    def __init__(self):


# inherit market
