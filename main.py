# If modifying these scopes, delete the file token.json.
import sys

import logger
from Bitmex import Bitmex
from BinanceTrader import BinanceTrader
from gmailHandler import gmailHandler
from controller import controller
# import ccxt
# exchange = ccxt.binance()
# exchange_time = exchange.public_get_time()['serverTime']
# your_time = exchange.milliseconds()
# print('Exchange UTC time:', exchange_time, exchange.iso8601(exchange_time))
# print('Your UTC time:', your_time, exchange.iso8601(your_time))
# SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():
    # gmail tests
    # gmail = gmailHandler('credentials.json')
    # count = 1
    # result = gmail.listen(1)
    # if not result is None:
    #     for email in result:
    #         print(str(count) + ':')
    #         email.print()
    #         count = count + 1

    # # controller tests
    # trader = controller(gmailHandler('credentials.json'), .1, .1, .1)
    # # trader.addMarket(Bitmex("4Utv4iqL31w88lLvRXN7qDtq", "lmoptxdUE8wFcn9GDdJRaecn_XfXDwfJ8_B14Bk3FOIK5Z9q",False,"test"),'BITMEX')
    # trader.importAPIKeys()
    #
    # trader.addMarket(Bitmex(.2, .11, .1, "B3aMhRrNhewW1SfHYT3M4h", "gQLdIXBUXar7PoDUND2DKYsLfAfMh0isCCmPQJjaDUxO0pdV"),
    #                  'BITMEX')
    #
    # while True:
    #     try:
    #         trader.run()
    #     except Exception as e:
    #         logger.logError(e)


    # # controller tests
    test = BinanceTrader("D82391RviO0eyFGm4QMK3EGTkd2D0p4viQesB8W4tVVpSo4nIUo0IDnVcCk65OGR", "G1n85emNiXJNWdMWAE7HlwQ1FvDx7OSNE8ZN8hmqNgvj5pJMTuU0XVUjyRRa2G4d", True, "test1")

    trader = controller(gmailHandler('credentials.json'), .1, .1, .1)
    trader.addMarket(test, "binance")


    test.marketBuy(1, "XRP", "BTC", None)

    amt = test.getAmountOfItem("XRP")
    print(amt)

    test.marketSell(1, "XRP", "BTC", "")



    # market = Bitmex(.1,.1,.1,"Bm23pmDAYgPq4JN-bbKipuq_", "gMH-WNVpS17cstY_0YOCe8kirlItoURrsYNCJKd6UhUjyoOp")
    # price = market.getMaxAmountToUse('ETH','U18')
    # print(price)

    # market.limitBuy(market.getCurrentPrice('XRP','USD'),'XRP','U18',1)


if __name__ == '__main__':
    main()
