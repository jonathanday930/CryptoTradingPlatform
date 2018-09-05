import bitmexApi.bitmex
from market import market

# a controller for ONE bitmex connection. This is a basic formula for how it should look. 
# Feel free to message me about the design.
class Bitmex(market):
    def getAmountOfItem(self, coin):
        pass

    # You will store the market API object in bitmex variable in init function
    bitmex = None

    def limitSell(self, price, currency, asset, orderId, orderQuantity):
        # TODO: figure out quantity params
        orderQuantity = orderQuantity * -1
        self.bitmex.Order.Order_new(symbol=currency + asset, orderQty=orderQuantity, price=price, ordType="Limit").result()
        pass

    def limitShortStart(self, price, currency, asset):
        pass

    def limitShortEnd(self, price, currency, asset):

        pass

    def marketBuy(self, orderQuantity, currency, asset):
        self.bitmex.Order.Order_new(symbol=currency+asset, orderQty=orderQuantity, ordType="Market").result()
        pass

    def limitBuy(self, price, currency, asset, orderQuantity, orderId):
        # TODO: figure out quantity params
        if orderId == None:
            orderQuantity = 10
            self.bitmex.Order.Order_new(symbol=currency + asset, orderQty=orderQuantity, price=price).result()
        else:
            self.bitmex.Order.Order_amend(orderID=orderId, price=price)
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

        self.bitmex = bitmexApi.bitmex.bitmex(test=True, config=None, api_key=apiKey, api_secret=apiKeySecret)

        #quote = self.bitmex.Quote.Quote_get(symbol="XBTUSD").result()

        orderQuantity = 10
        # result = self.bitmex.Order.Order_new(symbol="XBTUSD", orderQty= -20, ordType="Limit", price=7329).result()
        # print(result)

        # self.bitmex.Order.Order_amend(orderID="d2968e76-f796-fbfa-9ce0-d36336021f2f", price=7328.5)

        ### get orderbook
        orderbook = self.bitmex.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=20).result()
        #print(orderbook)

        ### get your orders
        orders = self.bitmex.Order.Order_getOrders(symbol='XBTUSD', reverse=True).result()
        print(orders)

        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass;

# inherit market
