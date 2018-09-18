import datetime
from math import floor

import bitmexApi.bitmex
from market import market

# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(market):
    bitmex = None

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        # TODO: figure out quantity params
        orderQuantity = orderQuantity * -1
        self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, price=limitPrice,
                                    ordType="Limit").result()

    def limitShortStart(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        orderQuantity = 10
        orderQuantity = orderQuantity * -1
        self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, price=limitPrice,
                                    ordType="Limit").result()
        pass

    def limitShortEnd(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        pass

    def marketBuy(self, orderQuantity, asset, currency):
        amount = self.getAmountOfItem(asset + currency)
        print("current amount of %s%s: %f \n" % (asset, currency, amount))
        # if we are currently in a short
        if amount < 0:
            amountToBuy = amount * -1
            self.logOrder(amountToBuy, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
            self.logOrder(amountToBuy, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
        else:
            # in the case that we are in a long position and get passed a long signal we should check the allowed
            # percentage of the portfolio to invest and add the difference to our current position
            # numberOfCoins = self.getNumberOfTradingPairs()
            numberOfCoins = 2
            availableBalance = self.getAvailableBalanceInUsd()
            allowedAmount = availableBalance / numberOfCoins
            extraToBuy = allowedAmount - amount
            self.logOrder(extraToBuy, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=extraToBuy, ordType="Market").result()
        pass

    def marketSell(self, orderQuantity, asset, currency):
        amount = self.getAmountOfItem(asset + currency)
        print("current amount of %s%s: %f \n" % (asset, currency, amount))

        # if we are currently in a Long
        if amount > 0:
            amountToBuy = amount * -1
            self.logOrder(amountToBuy, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
            self.logOrder(amountToBuy, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
        else:
            # numberOfCoins = self.getNumberOfTradingPairs()
            numberOfCoins = 2
            allowedAmount = (self.getAvailableBalanceInUsd() / numberOfCoins)
            extraToSell = (allowedAmount - abs(amount)) * -1
            self.logOrder(extraToSell, asset, currency)
            self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=extraToSell, ordType="Market").result()
        pass

    def limitBuy(self, price, asset, currency, orderQuantity, orderId=None):
        if orderId == None:
            result = self.bitmex.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Limit",
                                                 price=price).result()
            tradeInfo = result[0]
            for key, value in tradeInfo.items():
                if key == "orderID":
                    newOrderId = (key + ": {0}".format(value))
            return newOrderId
        else:
            result = self.bitmex.Order.Order_amend(orderID=orderId, price=price)
            # tradeInfo = result[0]

        return None

    def closeLimitOrders(self, asset, currency):
        # client.Order.Order_cancel(orderID='').result()
        self.bitmex.Order.Order_cancelAll().result()


    # use this function to handle connecting to the market (this function is the constructor)
    # You should definitely add parameters to this, probably the api key info
    def __init__(self, priceMargin, maximum, limitThreshold, apiKey, apiKeySecret):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function

        self.bitmex = bitmexApi.bitmex.bitmex(test=False, config=None, api_key=apiKey, api_secret=apiKeySecret)

        # quote = self.bitmex.Quote.Quote_get(symbol="XBTUSD").result()
        # self.bitmex.Order.Order_amend(orderID="d2968e76-f796-fbfa-9ce0-d36336021f2f", price=7328.5)

        super(Bitmex, self).__init__(priceMargin, maximum, limitThreshold)
        pass

    def getAmountToUse(self, asset, currency, orderType):
        if orderType == self.buyText:
            return self.getAmountOfItem('XBt')
        return self.getAmountOfItem(asset)

    def getMaxAmountToUse(self, asset, currency, curr=None):
        percentLower = 0.01
        if curr is None:
            curr = self.getAmountOfItem('XBt') * (1 - percentLower)

        price = self.getCurrentPrice(asset, currency)
        if currency == 'USD' or (currency == 'U18' and asset == 'XBT'):
            result = floor(curr * price)
        else:
            result = floor((curr / price))
        return result

    def getAmountOfItem(self, coin):
        if coin.lower() == 'xbt':
            return self.bitmex.User.User_getMargin().result()[0]['availableMargin'] / self.btcToSatoshi
        else:
            symbol = '{"symbol": "' + coin + '"}'
            result = self.bitmex.Position.Position_get(filter=symbol).result()
            if len(result[0]) > 0:
                return result[0][0]['currentQty']
            else:
                return 0

    def getAvailableBalanceInUsd(self):
        availableBalance = self.bitmex.User.User_getMargin(currency="XBt").result()
        user = availableBalance[0]
        balanceInBtc = user['withdrawableMargin'] / 100000000
        balanceInUsd = floor((balanceInBtc * self.getCurrentPrice('XBT', 'USD'))) - 1
        return balanceInUsd

    def getCurrentPrice(self, asset, currency):
        startTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
        trades = self.bitmex.Trade.Trade_get(symbol=asset + currency, startTime=startTime).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        return sum / volume

    def get_orders(self, asset, currency):
        orders = self.bitmex.Order.Order_getOrders(symbol=asset + currency, reverse=True).result()
        orderList = orders[0]
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)
        return orderList

    def getWallet(self):
        return self.bitmex.User.User_getWallet().result()

    def getNumberOfTradingPairs(self):
        pass

    def logOrder(self, orderQuantity, asset, currency):
        print("Available Balance: %s \n" % (self.getAvailableBalanceInUsd()))
        print("Ordering %d contracts of %s%s \n" % (orderQuantity, asset, currency))
        pass

# inherit market
