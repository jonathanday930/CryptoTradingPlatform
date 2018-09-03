import bitmexApi.bitmex
from market import market


# a controller for ONE bitmex connection. This is a basic formula for how it should look. 
# Feel free to message me about the design.
class Bitmex(market):
    def getAmountOfItem(self, coin):
        pass

    # You will store the market API object in bitmex variable in init function
    bitmex = None
    def limitSell(self, price,currency, asset):
        pass

    def limitShortStart(self, price, currency, asset):
        pass

    def limitShortEnd(self, price, currency, asset):
        pass

    def limitBuy(self, price, currency, asset):
        # TODO: figure out quantity params
        orderQuantity = 10
        self.bitmex.Order.Order_new(symbol=currency + asset, orderQty=orderQuantity, price=price).result()
        pass

    def getCurrentPrice(self,currency, asset):
        quote = self.bitmex.Quote.Quote_get(symbol=currency + asset).result()
        return quote

    def closeLimitOrders(self,currency, asset):
        #client.Order.Order_cancel(orderID='').result()
        self.bitmex.Order.Order_cancelAll().result()
        pass
    
    # use this function to handle connecting to the market (this function is the constructor)
    # You should definitely add parameters to this, probably the api key info
    def __init__(self, priceMargin, maximum, limitThreshold, apiKey, apiKeySecret):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function

        self.bitmex = bitmexApi.bitmex.bitmex(test=True, api_key=apiKey, api_secret=apiKeySecret)

        ### get orderbook
        orderbook = self.bitmex.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=20).result()
        #print(orderbook)

        ### private api test ( needs api key and secret )

        ### get your orders
        orders = self.bitmex.Order.Order_getOrders(symbol='XBTUSD', reverse=True).result()
        #print(orders)

        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass;

# inherit market
