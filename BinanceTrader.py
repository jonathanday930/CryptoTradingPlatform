import math
import bank
import logger
import traceback
from time import sleep
from market import market
from binance.client import Client


class BinanceTrader (market):

    allocationAmtInBtc = 0
    NUMBER_OF_COINS = 6
    AVAILABLE_BALANCE = 0.007

    def __init__(self, apiKey, apiKeySecret,realMoney,name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function

        super(BinanceTrader, self).__init__(apiKey, apiKeySecret, realMoney, name)
        self.connect()
        self.setAllocationAmt(self.NUMBER_OF_COINS)

    def setAllocationAmt(self, numberOfCoins):
        self.allocationAmtInBtc = self.AVAILABLE_BALANCE / numberOfCoins
        print("Allocation amount for %d coins: %.8f" % (self.NUMBER_OF_COINS, self.allocationAmtInBtc))
        bank.logBalance(self.AVAILABLE_BALANCE, "BINANCE")
        return

    def marketOrder(self, type, asset, currency):
        try:
            currentAmount = self.getAmountOfItem(asset)
            text = "current amount of %s: %f \n  %s" % (asset, currentAmount, type)
            print(text)

            if type == 'buy':
                assetPrice = self.getCurrentPrice(asset, currency)
                orderSize = (self.allocationAmtInBtc/assetPrice)
                stepSize = self.getStepSize(asset, currency)
                orderSize = self.calculateOrderSize(orderSize, stepSize)

                if currentAmount > orderSize:
                    print("attempted to buy %s%s while already in a position" % (asset, currency))
                    return True

                print("Buying %d" % (orderSize))
                self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
                bank.logContract(asset, currency, orderSize, "BINANCE")
            else:
                if type == 'sell':
                    orderSize = self.getAmountOfItem(asset)
                    stepSize = self.getStepSize(asset, currency)
                    orderSize = self.calculateOrderSize(orderSize, stepSize)
                    print("Selling %d" % (orderSize))
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
                    bank.logContract(asset, currency, orderSize, "BINANCE")
            self.attemptsLeft = self.attemptsTotal
            return True
        except:
            tb = traceback.format_exc()
            logger.logError(tb)
            print(tb)
            if self.attemptsLeft == 0:
                self.attemptsLeft = self.attemptsTotal
                return None
            sleep(self.delayBetweenAttempts)
            self.connect()
            self.attemptsLeft = 0
            # self.marketOrder(type, asset, currency)
        pass


    def calculateOrderSize(self, orderSize, stepSize):
        stepSize = str(stepSize)
        if stepSize == "1.0" or stepSize == "1":
            orderSize = math.floor(orderSize)
        elif stepSize == "0.1":
            orderSize = (math.floor(orderSize * 10)) * .1
        elif stepSize == "0.01":
            orderSize = (math.floor(orderSize * 100)) * .01
        elif stepSize == "0.001":
            orderSize = (math.floor(orderSize * 1000)) * .001
        elif stepSize == "0.0001":
            orderSize = (math.floor(orderSize * 10000)) * .0001
        elif stepSize == "0.00001":
            orderSize = (math.floor(orderSize * 100000)) * .00001
        elif stepSize == "0.000001":
            orderSize = (math.floor(orderSize * 1000000)) * .000001
        return orderSize


    def marketBuy(self, orderSize, asset, currency, note):
        if self.real_money:
            result = self.market.order_market_buy(
                symbol=asset + currency,
                quantity=orderSize)
            bank.logBalance("Binance", self.getAmountOfItem(asset))
            logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                            orderSize,
                            note=note)
            return result
        else:
            print("Testing an order, REAL MONEY = False")


    def marketSell(self, orderSize, asset, currency, note):
        #if ordersize is less than stepsize
            if orderSize < self.getStepSize(asset, currency):
                return
            if self.real_money == True:
                print("selling %d of %s" % (orderSize, asset + currency))
                result = self.market.order_market_sell(symbol=asset + currency, quantity=orderSize)
                logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                                orderSize,
                                note=note)
                return result

            else:
                result = self.market.create_test_order(
                symbol=asset + currency,
                side='SELL',
                type='MARKET',
                timeInForce='GTC',
                quantity=orderSize)

    def connect(self):
        self.market = Client(self.apiKey, self.apiKeySecret)
        pass

    def getCurrentPrice(self, asset, currency):
        allPrices = self.market.get_all_tickers()

        for item in allPrices:
            if item["symbol"] == asset+currency:
                print("%s: %s" % (item['symbol'], item["price"]))
                return float(item["price"])


    def getAmountOfItem(self, asset):
        balance = self.market.get_asset_balance(asset=asset)["free"]
        return float(balance)

    def getAvailableBalance(self):
        response = self.market.get_account()["balances"]
        print("Available balance: " + response[0]['free'])
        return float(response[0]['free'])


    def getPrice(self, symbol):
        return self.market.get_orderbook_ticker(symbol=symbol)

    def getStepSize(self, asset, currency):
        symbols = self.market.get_exchange_info()['symbols']
        for item in symbols:
            if item['symbol'] == asset+currency:
                daShit = item['filters'][1]['stepSize']
                print("%s stepSize: %s" % (asset+currency, daShit))
                return float(daShit)
        print("error")
        return

    def getOrderPrice(self, orderID):
        pass

    def closeLimitOrders(self, asset, currency):
        pass;

    def getOrderBook(self, asset, currency):
        pass

    def extractLimitPrice(self, type, asset, currency):
        pass

    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass;

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None, note=None):
        pass;

    def limitOrderStatus(self, orderID):
        pass

    def interpretType(self, type):
        pass

    def orderOpen(self, orderID):
        pass

    def closeLimitOrder(self, orderID):
        pass

    def orderCanceled(self, orderID):
        pass

    def quantityLeftInOrder(self, orderID, orderQuantity):
        pass

    def resetToEquilibrium_Market(self, currentAmount, asset, currency):
        pass

    def getMaxAmountToUse(self, asset, currency):
        pass