import bank
import logger
import traceback
from time import sleep
from market import market
from binance.client import Client


class BinanceTrader (market):

    allocationAmtInBtc = 0

    def __init__(self, apiKey, apiKeySecret,realMoney,name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(BinanceTrader, self).__init__(apiKey, apiKeySecret,realMoney,name)
        self.connect()
        self.setAllocationAmt(10)


    def setAllocationAmt(self, numberOfCoins):
        self.allocationAmtInBtc = self.getAvailableBalance() / numberOfCoins
        print(self.allocationAmtInBtc)
        return


    def marketOrder(self, type, asset, currency):
        try:
            currentAmount = self.getAmountOfItem(asset)
            text = "current amount of %s: %f \n  %s" % (asset, currentAmount, type)
            print(text)

            if type == 'buy':
                amtOfBtcToBuy = self.allocationAmtInBtc
                assetPrice = self.getCurrentPrice(asset, currency)
                orderSize = (amtOfBtcToBuy/assetPrice) - (assetPrice % self.getStepSize(asset, currency))
                self.marketBuy(orderSize, asset, currency, note='Going long.. Previous round trip profit')
            else:
                if type == 'sell':
                    assetPrice = self.getAmountOfItem(asset)
                    orderSize = assetPrice - (assetPrice % self.getStepSize(asset, currency))
                    result = self.marketSell(orderSize, asset, currency, note='Going short')
            self.attemptsLeft = self.attemptsTotal
            return True
        except:
            tb = traceback.format_exc()
            logger.logError(tb)
            if self.attemptsLeft == 0:
                self.attemptsLeft = self.attemptsTotal
                return None
            sleep(self.delayBetweenAttempts)
            self.connect()
            self.attemptsLeft = self.attemptsLeft - 1
            self.marketOrder(type, asset, currency)
        pass



    def marketBuy(self, orderSize, asset, currency, note):
        if self.real_money:
            result = self.market.order_market_buy(
                symbol=asset + currency,
                quantity=orderSize)
            bank.logBalance("Binance", self.getAmountOfItem(asset+currency))
            logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                            orderSize,
                            note=note)
            return result
        else:
            result = self.market.create_test_order(
                symbol=asset + currency,
                side='BUY',
                type='MARKET',
                quantity=orderSize)


    def marketSell(self, orderSize, asset, currency, note):
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
        print("%s: %s" % (asset, balance))
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