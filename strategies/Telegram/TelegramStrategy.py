'''Alexander McKee'''

'''Class for listening to Telegram chat messages and parsing for trade alerts'''

import datetime
import json
import logging
import re
try:
    from telethon import events
    from telethon.sync import TelegramClient

    from strategies.strategy import strategy
except ValueError:
    pass

class TelegramStrategy(strategy):
    """ """

    strategyName = 'Telegram'

    channel = None
    orders = []
    telegramClient = None
    message = None
    apiID = None
    apiSecret = None


    def __init__(self):

        self.importAPIKeys()

        self.telegramClient = TelegramClient('kcapbot', self.apiID, self.apiSecret)
        self.telegramClient.connect()

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        print("Telegram Account authorized:\nListening for Alerts\n\n")


    def listen(self):
        """ """
        @self.telegramClient.on(events.NewMessage)
        async def my_event_handler(event):
            print(event.raw_text)
            parseMessage(self, event.raw_text)

        self.telegramClient.start()
        self.telegramClient.run_until_disconnected()



    def importAPIKeys(self):
        """ """
        f = open('strategies/Telegram/TelegramCredentials.json', 'r')
        with open(f.name) as jsonFile:
            data = json.load(jsonFile)
            for keySet in data['API_Keys']:
                if keySet['keyID'] is not 'Fake':
                    self.apiID = keySet['keyID']
                    self.apiSecret = keySet['privateKey']
                else:
                    print('PLEASE ADD TELEGRAM API KEYS TO Telegram/TelegramCredentials.json\n')


    def runStrategy(self, marketControllers):
        """

        :param marketControllers: 

        """
        return self.orders

    def addOrder(self, order):
        """

        :param order: 

        """
        self.orders.append(order)


def parseMessage(telegramStrategy, text):
    """Grab the message parse the data and format for Gmail
    handler. subject looks like: '$$$ BUY BTC USD $$$'

    :param telegramStrategy: 
    :param text: 

    """

    market = 'BINANCE'
    currency = 'BTC'

    coin = None
    order = None
    takeGains = []

    alertIdentifiers = ["buy", "entry", "zone", "stop", "stoploss"]
    takeProfitIdentifiers = ["tg", "tp", "take", "profit", "gains"]
    entryPriceIdentifiers = ["buy", "zone", "buyzone", "enter", "entry"]
    stopPriceIdentifiers = ["stop", "stoploss", "loss", "enter", "entry"]

    text = text.lower()

    if any(x in text for x in alertIdentifiers):

        print("message:\n\n%s\n" % text)

        lines = text.splitlines(False)
        for line in lines:

            if '#' in line:
                coin = line[line.find("#") + 1:]
                if " " in line:
                    coin = coin[:line.find(" ")]
                print("Coin: " + coin + "\n")


            if any(x in line for x in entryPriceIdentifiers):
                entryPrice = int(re.search(r'\d+', line).group())
                print("Entry Price: %d\n" % entryPrice)


            if any(x in line for x in takeProfitIdentifiers):
                takeProfit = line[line.find(" "):]
                takeProfit = int(re.search(r'\d+', takeProfit).group())
                print("Take profit: %d\n" % takeProfit)
                takeGains.append(takeProfit)


            if any(x in line for x in stopPriceIdentifiers):
                stopPrice = int(re.search(r'\d+', line).group())
                print("Stop Price: %d\n" % stopPrice)



        '''final determination of whether the alert is actually an alert.
         if we have 2 or more take profit indicators'''
        if len(takeGains) >= 2:
            subject = ("$$ %s BTC LONG BINANCE $$" % coin.upper())
            print(coin + "\n" + subject + "\n")

            order = {
                'market': market,
                'currency': currency,
                'asset': coin,
                'amount': 'Determine with bank',
                'action': 'BUY',
                'action-type': 'Optional value for the method to buy or sell- such as market, limit, or limit-maker. Implemented on a per market basis',
                'price': entryPrice,
                'id': '%s Telegram_Alert_BUY_%s' % (str(datetime.datetime.now()), coin)
            }
            print(order)
            telegramStrategy.addOrder(order)
            return order
