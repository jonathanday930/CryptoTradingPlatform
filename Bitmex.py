import datetime

import bitmexApi.bitmex
from market import market


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(market):
    bitmex = None
    def limitSell(self, price, asset, currency, orderId, orderQuantity):
        # TODO: figure out quantity params
        orderQuantity = orderQuantity * -1
        self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, price=price, ordType="Limit").result()

    def getAmountOfItem(self, coin=None):
        return self.bitmex.User.User_getMargin().result()[0]['availableMargin']/self.btcToSatoshi

    # TODO: we need to get the current amount of the symbol that we already have so that we can sell it all and then place the short with the negative orderQuantity
    def limitShortStart(self, price, asset, currency):
        orderQuantity = 10
        orderQuantity = orderQuantity * -1
        self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, price=price, ordType="Limit").result()
        pass

    def limitShortEnd(self, price, currency, asset):
        pass

    def marketBuy(self, orderQuantity, asset, currency):
        self.bitmex.Order.Order_new(symbol=asset+currency, orderQty=orderQuantity, ordType="Market").result()
        pass

    def limitBuy(self, price, asset, currency, orderQuantity, orderId):
        if orderId == None:
            result = self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Limit", price=price).result()
            tradeInfo = result[0]
            for key, value in tradeInfo.items():
                if key == "orderID":
                    newOrderId = (key + ": {0}".format(value))
            return newOrderId
        else:
            result = self.bitmex.Order.Order_amend(orderID=orderId, price=price)
            # tradeInfo = result[0]

        return None

    def getCurrentPrice(self, asset, currency):
        startTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
        trades = self.bitmex.Trade.Trade_get(symbol=asset+currency, startTime=startTime).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        return sum / volume

    def closeLimitOrders(self, asset, currency):
        # client.Order.Order_cancel(orderID='').result()
        self.bitmex.Order.Order_cancelAll().result()
        pass

    def get_orders(self, asset, currency):
        # .open_orders() doesn't seem to work
        # return self.bitmex.open_orders()

        ### get your orders
        orders = self.bitmex.Order.Order_getOrders(symbol=asset+currency, reverse=True).result()
        orderList = orders[0]
        # TODO: your decision on how we keep the ledger for all of our trades, but this will print all of our trades and their status nicely if you wanna uncomment it
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)
        return orderList

    # Not working
    def getPosition(self, currency, asset):
        symbol = '{"symbol": "'+currency+asset + '"}'
        return self.bitmex.Position.Position_get(filter=symbol).result()
    def getWallet(self):
        return self.bitmex.User.User_getWallet()

    # use this function to handle connecting to the market (this function is the constructor)
    # You should definitely add parameters to this, probably the api key info
    def __init__(self, priceMargin, maximum, limitThreshold, apiKey, apiKeySecret):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function

        self.bitmex = bitmexApi.bitmex.bitmex(test=True, config=None, api_key=apiKey, api_secret=apiKeySecret)

        #quote = self.bitmex.Quote.Quote_get(symbol="XBTUSD").result()

        # self.bitmex.Order.Order_amend(orderID="d2968e76-f796-fbfa-9ce0-d36336021f2f", price=7328.5)

        ### get orderbook
        # orderbook = self.bitmex.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=20).result()
        # print(orderbook)

        # testing order amending
        # orderID = self.limitBuy(6401.5, "XBT", "USD", -260, None)
        # print(orderID)
        # orderID = self.limitBuy(6400.5, "XBT", "USD", 20, "efefbd9d-0c98-9d81-a60d-60d2a3d17d92")
        # print(orderID)

        # self.marketBuy(20, "XBT", "USD")
        # print(self.getPosition('XBT', 'USD'))
        # wallet = self.getWallet()
        # print(wallet)

        ### get your orders
        # orders = self.bitmex.Order.Order_getOrders(symbol='XBTUSD', reverse=True).result()
        # print(orders)
        # orderList = orders[0]
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)

        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass;

# inherit market
