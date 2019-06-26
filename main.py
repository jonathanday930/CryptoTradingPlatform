from controller import controller
from recording import bank
from strategies.gmail.gmailStrategy import gmailStrategy


# CHANGE THIS TO GO FROM TESTNET TO LIVENET
real_money = False

trader = controller(.001, .1, real_money)
trader.importAPIKeys()
trader.addStrategy(gmailStrategy('strategies/gmail/credentials.json'))
trader.run()

