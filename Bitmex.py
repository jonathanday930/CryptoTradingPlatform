from market import market

# a controller for ONE bitmex connection. This is a basic formula for how it should look. 
# Feel free to message me about the design.
class Bitmex(market):
    # You will store the market API object in bitmex variable in init function
    bitmex = None
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
    def __init__(self, priceMargin, maximum, limitThreshold):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass;

# inherit market
