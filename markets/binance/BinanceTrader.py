from recording import logger
from markets.marketBaseClass import market
from markets.binance.binance import Client


class BinanceTrader (market):
    """ """

    def __init__(self, apiKey, apiKeySecret,realMoney,name):
        # The super function runs the constructor on the market class that this class inherits from. In other words,
        # done mess with it or the parameters I put in this init function
        super(BinanceTrader, self).__init__(apiKey, apiKeySecret,realMoney,name)
        self.connect()

    def marketOrder(self, type, asset, currency):
        """

        :param type: 
        :param asset: 
        :param currency: 

        """
        red = 5

    def resetToEquilibrium_Market(self, currentAmount, asset, currency):
        """

        :param currentAmount: 
        :param asset: 
        :param currency: 

        """
        red = 5

    def getMaxAmountToUse(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        red = 5

    def marketBuy(self, orderSize, asset, currency, note):
        """

        :param orderSize: 
        :param asset: 
        :param currency: 
        :param note: 

        """
        if self.real_money:
            result = self.market.order_market_buy(
                symbol=asset + currency,
                quantity=orderSize)
            logger.logOrder('Binance', 'market', self.getCurrentPrice(asset, currency), asset, currency,
                            orderSize,
                            note=note)
            return result
        else:
            result = self.market.create_test_order(
                symbol=asset + currency,
                side='BUY',
                type='MARKET',
                timeInForce='GTC',
                quantity=orderSize)

    def marketSell(self, orderSize, asset, currency, note):
        """

        :param orderSize: 
        :param asset: 
        :param currency: 
        :param note: 

        """
            if self.real_money == True:
                result = self.market.order_market_sell(
        symbol=asset+currency,
        quantity=-orderSize)
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
        """ """
        self.market = Client(self.apiKey, self.apiKeySecret)



    def limitBuy(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        """

        :param limitPrice: 
        :param asset: 
        :param currency: 
        :param orderQuantity: 
        :param orderNumber:  (Default value = None)

        """
        red = 5

    def limitSell(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        """

        :param limitPrice: 
        :param asset: 
        :param currency: 
        :param orderQuantity: 
        :param orderNumber:  (Default value = None)

        """
        red = 5

    def limitShortEnd(self, limitPrice, asset, currency, orderQuantity, orderNumber=None):
        """

        :param limitPrice: 
        :param asset: 
        :param currency: 
        :param orderQuantity: 
        :param orderNumber:  (Default value = None)

        """
        red = 5

    def getCurrentPrice(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        prices = self.market.get_all_tickers()

    def closeLimitOrders(self, asset, currency):
        """

        :param asset: 
        :param currency: 

        """
        red = 5

    def getAmountOfItem(self, coin):
        """

        :param coin: 

        """
        balance = self.market.get_asset_balance(asset=coin)
        return balance
