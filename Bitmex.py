import datetime

import bitmexApi.bitmex
from market import market


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(market):
    bitmex = None

    def getAmountOfItem(self, coin=None):
        return self.bitmex.User.User_getMargin().result()[0]['availableMargin']/self.btcToSatoshi

    def limitSell(self, price, currency, asset):
        pass

    def limitShortStart(self, price, currency, asset):
        pass

    def limitShortEnd(self, price, currency, asset):
        pass

    def limitBuy(self, price, currency, asset):
        # TODO: figure out quantity params
        return self.bitmex.Order.Order_new(symbol="XBTUSD", orderQty=10, ordType="Market").result()

    def getCurrentPrice(self, currency, asset):
        startTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
        trades = self.bitmex.Trade.Trade_get(symbol=asset + currency, startTime=startTime).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        return sum / volume

    def closeLimitOrders(self, currency, asset):
        # client.Order.Order_cancel(orderID='').result()
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
        # print(orderbook)

        ### private api test ( needs api key and secret )

        ### get your orders
        orders = self.bitmex.Order.Order_getOrders(symbol='XBTUSD', reverse=True).result()
        # print(orders)

        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass;

# inherit market
