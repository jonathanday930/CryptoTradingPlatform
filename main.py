# If modifying these scopes, delete the file token.json.
import sys

import logger
from Bitmex import Bitmex
from gmailHandler import gmailHandler
from controller import controller

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


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

    # controller tests
    trader = controller(gmailHandler('credentials.json'))
    trader.addMarket(Bitmex(.1, .1, .1, "FEN58-cdNHcj_JmgPDSF3U0-", "PmJYn7nifJ60pKFo9t8fjIpk7wEJh5KBsnq1kvQiviJBLaJz"),
                     'BITMEX')

    while True:
        try:
            trader.run()
        except Exception as e:
            logger.logError(e)

    # market = Bitmex(.1,.1,.1,"Bm23pmDAYgPq4JN-bbKipuq_", "gMH-WNVpS17cstY_0YOCe8kirlItoURrsYNCJKd6UhUjyoOp")
    # price = market.getMaxAmountToUse('ETH','U18')
    # print(price)

    # market.limitBuy(market.getCurrentPrice('XRP','USD'),'XRP','U18',1)


if __name__ == '__main__':
    main()
