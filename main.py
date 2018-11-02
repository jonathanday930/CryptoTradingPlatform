# If modifying these scopes, delete the file token.json.

from gmailHandler import gmailHandler
from controller import controller
from BinanceTrader import BinanceTrader



SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():

    #  CHANGE THIS TO GO FROM TESTNET TO LIVENET
    real_money = False
    #
    trader = controller(gmailHandler('credentials.json'), .001, .1, real_money)
    #
    # trader.importAPIKeys()
    # trader.run()

    # test = BinanceTrader("",
    #                      "", True, "test1")
    #
    # trader.addMarket(test, "BINANCE")
    # test.getCurrentPrice("BTC", "USDT")
    # availableBalance = test.getAvailableBalance()
    # xrpPrice = test.getCurrentPrice("XRP", "BTC")
    # test.getAmountOfItem("XRP")
    # test.getStepSize("XRP", "BTC");
    # test.marketOrder("sell", "XRP", "BTC")




if __name__ == '__main__':
    main()
