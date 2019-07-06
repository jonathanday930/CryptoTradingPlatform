'''Alexander McKee'''

'''Class for listening to Telegram chat messages and parsing for trade alerts'''

import logging
import json
from time import strftime, sleep
from telethon.sync import TelegramClient
from telethon import events



class TelegramStrategy():

    strategyName = 'Telegram'

    market = 'BINANCE'
    currency = 'BTC'
    channel = None
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
        @self.telegramClient.on(events.NewMessage)
        async def my_event_handler(event):
            print(event.raw_text)
            parseMessage(self, event.raw_text)
        self.telegramClient.start()
        self.telegramClient.run_until_disconnected()



    def importAPIKeys(self):
        f = open('strategies/Telegram/TelegramCredentials.json', 'r')
        with open(f.name) as jsonFile:
            data = json.load(jsonFile)
            for keySet in data['API_Keys']:
                if keySet['keyID'] is not 'Fake':
                    self.apiID = keySet['keyID']
                    self.apiSecret = keySet['privateKey']
                else:
                    print('PLEASE ADD TELEGRAM API KEYS TO Telegram/TelegramCredentials.json\n')




def parseMessage(self, text):
    """Grab the message parse the data and format for Gmail
    handler. subject looks like: '$$$ BUY BTC USD $$$' """

    coin = None
    takeGains = []
    alertIdentifiers = ["BUY", "Buy", "Entry", "ENTRY"]
    takeProfitIdentifiers = ["Tg", "TG", "Tp", "TP"]

    if any(x in text for x in alertIdentifiers):

        print("message:\n\n%s\n" % text)

        lines = text.splitlines(False)
        for line in lines:

            if "#" in line:
                coin = line[line.find("#") + 1:]

                if " " in line:
                    coin = coin[:line.find(" ")]

                print("Coin: " + coin + "\n")

            if any(x in line for x in takeProfitIdentifiers):
                takeProfit = line[line.find(" "):]

                if " " in line:
                    takeProfit = takeProfit[:line.find(" ")]

                print("Take profit: " + takeProfit + "\n")
                takeGains.append(takeProfit)

            subject = ("$$ %s BTC LONG BINANCE $$" % coin.upper())
            print(coin + "\n" + subject + "\n")

        '''final determination of whether the alert is actually an alert.
         if we have 2 or more take profit indicators'''
        if len(takeGains) >= 2:
            order = {
                'market': self.market,
                 'currency': self.currency,
                 'asset': coin,
                 'amount': 'The amount of asset to buy/sell',
                 'action': 'BUY',
                 'action-type': 'Optional value for the method to buy or sell- such as market, limit, or limit-maker. Implemented on a per market basis',
                 'price': 'An optional value for the price to buy or sell at. If not included, will just find the current price.',
                 'id': 'Telegram_Alert_BUY_%s_%s' % (coin, strftime())
            }