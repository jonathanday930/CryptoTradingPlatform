import math
from decimal import Decimal
from math import floor
from time import sleep

import markets.bitmex.bitmexApi.bitmex
from recording import logger

from markets.makerLimitOrderMarket import makerLimitOrderMarket


# a controller for ONE bitmex connection. This is a basic formula for how it should look.
from markets.marketOrderMarket import marketOrderMarket


class Bitmex(marketOrderMarket):
    """ """
    apiKey = None
    apiKeySecret = None

    marketName = 'BITMEX'

    limitOrderEnabled = True

    def orderisOpen(self, orderID):
        """

        :param orderID: 

        """
        pass

    def extractMakerLimitPrice(self, type, asset, currency):
        """

        :param type: 
        :param asset: 
        :param currency: 

        """
        orderBook = self.getOrderBook(currency, asset)

        limitPrice = -5

        if type == self.buyText:
            limitPrice = -math.inf
        else:
            if type == self.sellText:
                limitPrice = math.inf

        for order in orderBook:

            if self.buyText.lower() == order['side'].lower():
                if order['price'] > limitPrice:
                    limitPrice = order['price']
            else:
                if self.sellText.lower() == order['side'].lower():
                    if order['price'] < limitPrice:
                        limitPrice = order['price']
        return limitPrice

    def getOrderPrice(self, orderID):
        """

        :param orderID: 

        """
        order = self.limitOrderStatus(orderID)
        if order is not None:
            return order['price']
        return None



    def orderCanceled(self, orderID):
        """

        :param orderID: 

        """
        order = self.limitOrderStatus(orderID)
        if order != False:
            return order['ordStatus'] == 'Canceled'
        return True

    def getOrderBook(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        res = self.market.OrderBook.OrderBook_getL2(symbol=asset + currency).result()[0]
        return res

    def quantityLeftInOrder(self, orderID, orderQuantity=None):
        """

        :param orderID: 
        :param orderQuantity:  (Default value = None)

        """
        if orderID == None:
            return orderQuantity
        else:
            status = self.limitOrderStatus(orderID)
            return status['orderQty'] - status['cumQty']

    def orderOpen(self, orderID):
        """

        :param orderID: 

        """
        if orderID == None:
            return False
        order = self.limitOrderStatus(orderID)
        status = order['ordStatus']
        one = order['ordStatus'] != 'Canceled'
        two = order['ordStatus'] != 'Filled'
        return one and two

    def limitOrderStatus(self, orderID, triesLeft=None):
        """

        :param orderID: 
        :param triesLeft:  (Default value = None)

        """
        if triesLeft == None:
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
        """

        :param asset: 
        :param currency: 

        """
        res = self.market.Instrument.Instrument_get(symbol=asset + currency).result()[0][0]['tickSize']
        return res

    def closeLimitOrder(self, orderID):
        """

        :param orderID: 

        """
        if orderID != None:
            res = self.market.Order.Order_cancel(orderID=orderID).result()
            return res
        else:
            return None

    def interpretType(self, type):
        """

        :param type: 

        """
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
        """

        :param limitPrice: 
        :param asset: 
        :param currency: 
        :param orderQuantity: 
        :param orderNumber:  (Default value = None)
        :param note:  (Default value = None)

        """
        return self.limitBuy(limitPrice, asset, currency, -orderQuantity, orderNumber, note)

    def parsePrice(self, asset, currency, price):
        """

        :param asset: 
        :param currency: 
        :param price: 

        """
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
        """

        :param price: 
        :param asset: 
        :param currency: 
        :param orderQuantity: 
        :param orderId:  (Default value = None)
        :param note:  (Default value = None)

        """
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
                    orderQuantity = self.quantityLeftInOrder(orderId, orderQuantity)
                    if orderQuantity != 0:
                        openOrder = False
                else:
                    logger.logError('UNKNOWN LIMIT ERROR: ' + str(e))
                    raise e

        if not openOrder and orderQuantity != 0:
            result = self.market.Order.Order_new(symbol=currency + asset, orderQty=orderQuantity, ordType="Limit",
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

    def marketBuy(self, orderQuantity, currency, asset, note=None):
        """

        :param orderQuantity: 
        :param currency: 
        :param asset: 
        :param note:  (Default value = None)

        """
        result = self.market.Order.Order_new(symbol=currency + asset, orderQty=orderQuantity, ordType="Market").result()
        logger.logOrder('Bitmex', 'market', self.getCurrentPrice(currency, asset), asset, currency, orderQuantity,
                        note=note)
        return result

    def marketSell(self, orderQuantity, asset, currency, note=None):
        """

        :param orderQuantity: 
        :param asset: 
        :param currency: 
        :param note:  (Default value = None)

        """
        return self.marketBuy(-orderQuantity, asset, currency, note=note)

    def closeLimitOrders(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        # client.Order.Order_cancel(orderID='').result()
        self.market.Order.Order_cancelAll().result()


    def __init__(self, realMoney, name,apiKey, apiKeySecret):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(Bitmex, self).__init__(realMoney, name)
        self.apiKey = apiKey
        self.apiKeySecret= apiKeySecret
        self.connect()

    def connect(self):
        """ """
        self.market = markets.bitmex.bitmexApi.bitmex.bitmex(test=not self.real_money, config=None, api_key=self.apiKey,
                                                             api_secret=self.apiKeySecret)

    def getAmountToUse(self, asset, currency, orderType):
        """

        :param asset: 
        :param currency: 
        :param orderType: 

        """
        if orderType == self.buyText:
            return self.getAmountOfItem('XBt')
        return self.getAmountOfItem(asset)

    def getAmountOfItem(self, val1, val2=None,orderType=None):
        """

        :param val1: 
        :param val2:  (Default value = None)
        :param orderType:  (Default value = None)

        """
        if val1.lower() == 'xbt' and val2 is None:
            return self.market.User.User_getMargin().result()[0]['availableMargin'] / self.btcToSatoshi
        else:
            symbol = '{"symbol": "' + str(val1) + str(val2) + '"}'
            result = self.market.Position.Position_get(filter=symbol).result()
            if len(result[0]) > 0:
                return result[0][0]['currentQty']
            else:
                return 0

    def getCurrentPrice(self, val1, val2=None):
        """

        :param val1: 
        :param val2:  (Default value = None)

        """
        trades = self.market.Trade.Trade_get(symbol=val1 + val2, count=4, reverse=True).result()
        sum = 0
        volume = 0
        for trade in trades[0]:
            sum = sum + (trade['price'] * trade['size'])
            volume = volume + trade['size']
        strRes = sum / volume
        strRes = str(strRes)
        return float(strRes)

    def get_orders(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        orders = self.market.Order.Order_getOrders(symbol=asset + currency, reverse=True).result()
        orderList = orders[0]
        # for i in range(len(orderList)):
        #     x = orderList[i]
        #     print(x)
        return orderList

    def getWallet(self):
        """ """
        return self.market.User.User_getWallet().result()

    def getNumberOfTradingPairs(self):
        """ """
        pass

    def setLeverage(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        self.market.Position.Leverage(symbol=(asset + currency), leverage=2)
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
