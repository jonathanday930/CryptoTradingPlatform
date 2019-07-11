from controller import controller
from recording import bank
from strategies.gmail.gmailStrategy import gmailStrategy
from strategies.Telegram.TelegramStrategy import TelegramStrategy
import threading




# CHANGE THIS TO GO FROM TESTNET TO LIVENET
real_money = False

telegramBot = TelegramStrategy()
telegramThread = threading.Thread(target=telegramBot.listen()).start()

trader = controller(.001, .1, real_money)
trader.importAPIKeys()
trader.addStrategy(gmailStrategy('strategies/gmail/credentials.json'))
trader.addStrategy(telegramBot)
trader.run()

