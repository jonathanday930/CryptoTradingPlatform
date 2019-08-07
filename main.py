import threading
from strategies.Telegram.TelegramStrategy import TelegramStrategy
from strategies.gmail.gmailStrategy import gmailStrategy

from controller import controller

# CHANGE THIS TO GO FROM TESTNET TO LIVENET
from tests.unit_tests.marketOrderMarket import marketOrderMarketTest

real_money = False


marketOrderMarketTest.test_allConfigs()
#
# try:
#     telegramBot = TelegramStrategy()
#     telegramThread = threading.Thread(target=telegramBot.listen()).start()
#
# except ValueError:
#     pass
#
#
# trader = controller(.001, .1, real_money)
# trader.importAPIKeys()
# trader.addStrategy(gmailStrategy('strategies/gmail/credentials.json'))
# trader.addStrategy(telegramBot)
# trader.run()
#
