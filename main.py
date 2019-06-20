# If modifying these scopes, delete the file token.json.


from controller import controller
from debug import bank
from strategies.gmail.gmailStrategy import gmailStrategy

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
#
# bank.updateBalanceHistory('BITMEX')

# CHANGE THIS TO GO FROM TESTNET TO LIVENET
real_money = False

trader = controller(.001, .1, real_money)
trader.importAPIKeys()
trader.addStrategy(gmailStrategy('strategies/gmail/credentials.json'))
trader.run()
