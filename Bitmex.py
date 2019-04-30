import datetime
from decimal import Decimal
from math import floor
from time import sleep

import bitmexApi.bitmex
import logger
from market import market


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
class Bitmex(market):

    def getOrderPrice(self, orderID):
        order = self.limitOrderStatus(orderID)
        if order is not None:
            return order['price']
        return None

    marketName = 'BITMEX'

    limitOrderEnabled = True



    def orderCanceled(self, orderID):
        order = self.limitOrderStatus(orderID)
        if order != False:
            return order['ordStatus'] == 'Canceled'
        return True


    def getOrderBook(self, asset, currency):
        res = self.market.OrderBook.OrderBook_getL2(symbol=asset+currency).result()[0]
        return res


    def extractLimitPrice(self, type, asset, currency):
        orderBook = self.getOrderBook(asset,currency)

        limitPrice = -5

        if type == self.buyText:
            limitPrice = 0
        else:
            if type == self.sellText:
                limitPrice = 999999

        for order in orderBook:

            if self.buyText.lower() == order['side'].lower():
                if order['price'] > limitPrice:
                    limitPrice = order['price']
            else:
                if self.sellText.lower() == order['side'].lower():
                    if order['price'] < limitPrice:
                        limitPrice = order['price']
        return limitPrice


    def quantityLeftInOrder(self, orderID,orderQuantity):
        if orderID == None:
            return orderQuantity
        else:
            status = self.limitOrderStatus(orderID)
            return status['orderQty']-status['cumQty']

    def orderOpen(self, orderID):
        if orderID == None:
            return False
        order = self.limitOrderStatus(orderID)
        status = order['ordStatus']
        one = order['ordStatus'] != 'Canceled'
        two = order['ordStatus'] != 'Filled'
        return one and two

    def limitOrderStatus(self, orderID, triesLeft = None):
        if triesLeft==None:
            triesLeft = 1
        if orderID == None:
            return False
        filter = '{"orderID": "' + orderID + '"}'
        res = self.market.Order.Order_getOrders(filter=filter).result()

        try:
            res = res[0][0]
            status = res['ordStatus']
        except:
            if triesLeft != 0:
                sleep(1)
                return self.limitOrderStatus(orderID)
            triesLeft = triesLeft - 1
            logger.logError('--- ORDER LIST ERROR ---')

        return res


    def getTickSize(self, asset, currency):
        res = self.market.Instrument.Instrument_get(symbol=asset+currency).result()[0][0]['tickSize']
        return res

    def closeLimitOrder(self, orderID):
        if orderID != None:
            res = self.market.Order.Order_cancel(orderID=orderID).result()
            return res
        else:
            return None

    def interpretType(self, type):
        if type.lower() == 'LONG'.lower():
            return self.buyText
        else:
            if type.lower() == 'SHORT'.lower():
                return self.sellText
            else:
                if type.lower() == 'u18':
                    return 'Z18'
        return type


    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        return self.limitBuy(limitPrice, asset, currency, -orderQuantity, orderNumber, note)

    def parsePrice(self, asset, currency, price):
        digits = 2
        if asset + currency == 'XRPU18':
            digits = 9
        else:
            if asset + currency == 'XBTUSD':
                return str(price)[:str(price).find(".")]

        strPrice = str(price)
        decimalPlace = strPrice.find(".")
        nextDigit = strPrice[decimalPlace + digits:decimalPlace + digits + 1]
        if int(nextDigit) > 4:
            increment = Decimal((1 * 10 ** -digits))
            price = price + increment
            strPrice = str(price)
        return strPrice[:decimalPlace + digits]

    def limitBuy(self, price, asset, currency, orderQuantity, orderId=None, note=None):
        result = None

        openOrder = self.orderOpen(orderId)
        if openOrder and orderQuantity != 0:
            try:
                result = self.market.Order.Order_amend(orderID=orderId, price=price).result()
                logger.logOrder(self.marketName, 'Limit', price, asset, currency, orderQuantity,
                                str(note) + ' amend for order: ' + str(orderId))
            except Exception as e:

                if e.response.status_code == 400:
                    logger.logError('LIMIT AMEND ERROR')
                    orderQuantity = self.quantityLeftInOrder(orderId,orderQuantity)
                    if orderQuantity != 0:
                        openOrder = False
                else:
                    logger.logError('UNKNOWN LIMIT ERROR: ' + str(e))
                    raise e


        if not openOrder and orderQuantity != 0:
            result = self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Limit",
                                             price=price, execInst='ParticipateDoNotInitiate').result()
            logger.logOrder(self.marketName, 'Limit', price, asset, currency, orderQuantity, note)
        if result is not None:
            tradeInfo = result[0]
            for key, value in tradeInfo.items():
                if key == "orderID":
                    newOrderId = (key + ": {0}".format(value))
                    return newOrderId[9:]
        else:
            return None

    def resetToEquilibrium_Market(self, amount, asset, currency):
        before = self.getAmountOfItem('xbt')

        if amount < 0:
            self.marketBuy(-amount, asset, currency, note='Buying for equilibrium')
        else:
            if amount > 0:
                self.marketSell(amount, asset, currency, note='Selling for equilibrium')
        after = self.getAmountOfItem('xbt')
        return after - before

    def marketBuy(self, orderQuantity, asset, currency, note=None):
        result = self.market.Order.Order_new(symbol=asset + currency, orderQty=orderQuantity, ordType="Market").result()
        logger.logOrder('Bitmex', 'market', self.getCurrentPrice(asset, currency), asset, currency, orderQuantity,
                        note=note)
        return result

    def marketSell(self, orderQuantity, asset, currency, note=None):
        return self.marketBuy(-orderQuantity, asset, currency, note=note)

    def closeLimitOrders(self, asset, currency):
        # client.Order.Order_cancel(orderID='').result()
        self.market.Order.Order_cancelAll().result()

    def __init__(self, apiKey, apiKeySecret, realMoney, name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(Bitmex, self).__init__(apiKey, apiKeySecret, realMoney, name)
        self.connect()

    def connect(self):
        self.market = bitmexApi.bitmex.bitmex(test=not self.real_money, config=None, api_key=self.apiKey,
                                              api_secret=self.apiKeySecret)

    def getAmountToUse(self, asset, currency, orderType):
        if orderType == self.buyText:
            return self.getAmountOfItem('XBt')
        return self.getAmountOfItem(asset)

    def getMaxAmountToUse(self, asset, currency, curr=None):
        percentLower = 0.01
        if curr is None:
            curr = self.getAmountOfItem('XBt') * (1 - percentLower)

        price = self.getCurrentPrice(asset, currency)
        if currency == 'USD' or (currency == 'Z18' and asset == 'XBT'):
            result = floor(curr * price)
        else:
            result = floor((curr / price))
        return result

    def getAmountOfItem(self, coin):
        if coin.lower() == 'xbt':
            return self.market.User.User_getMargin().result()[0]['availableMargin'] / self.btcToSatoshi
        else:
            symbol = '{"symbol": "' + coin + '"}'
            result = self.market.Position.Position_get(filter=symbol).result()
            if len(result[0]) > 0:
                return result[0][0]['currentQty']
            else:
                return 0

    def getCurrentPrice(self, asset, currency):
        trades = self.market.Trade.Trade_get(symbol=asset + currency, count=4, reverse=True).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        strRes = sum / volume
        strRes =str(strRes)
        return float(strRes)


    def get_orders(self, asset, currency):
        orders = self.market.Order.Order_getOrders(symbol=asset + currency, reverse=True).result()
        orderList = orders[0]
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)
        return orderList

    def getWallet(self):
        return self.market.User.User_getWallet().result()

    def getNumberOfTradingPairs(self):
        pass

    def setLeverage(self, asset, currency):
        self.market.Position.Leverage(symbol=(asset+currency), leverage=2)
        pass

    # def logOrder(self, orderQuantity, asset, currency):
    #     print("Available Balance: %s \n" % (self.getAvailableBalanceInUsd()))
    #     print("Ordering %d contracts of %s%s \n" % (orderQuantity, asset, currency))
    #     pass
#
#
#
#
#         amount = self.getAmountOfItem(asset + currency)
#         print("current amount of %s%s: %f \n" % (asset, currency, amount))
#
#         # if we are currently in a Long
#         if amount > 0:
#             amountToBuy = amount * -1
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#             self.logOrder(amountToBuy, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=amountToBuy, ordType="Market").result()
#         else:
#             # numberOfCoins = self.getNumberOfTradingPairs()
#             numberOfCoins = 2
#             allowedAmount = (self.getAvailableBalanceInUsd() / numberOfCoins)
#             extraToSell = (allowedAmount - abs(amount)) * -1
#             self.logOrder(extraToSell, asset, currency)
#             self.market.Order.Order_new(symbol=asset + currency, orderQty=extraToSell, ordType="Market").result()
#         pass

#
# def figureOutShare(self):
#        numberOfCoins = 2
#        availableBalance = self.getAvailableBalanceInUsd()
#        allowedAmount = availableBalance / numberOfCoins
#        extraToBuy = allowedAmount - amount
#        self.logOrder(extraToBuy, asset, currency)


# def getAvailableBalanceInUsd(self):
#     availableBalance = self.market.User.User_getMargin(currency="XBt").result()
#     user = availableBalance[0]
#     balanceInBtc = user['withdrawableMargin'] / 100000000
#     balanceInUsd = floor((balanceInBtc * self.getCurrentPrice('XBT', 'USD'))) - 1
#     return balanceInUsd
