'''Alexander McKee'''
'''Class for listening to Telegram chat messages and parsing for trade alerts'''

import json
from strategies.strategy import strategy
from telethon.sync import TelegramClient
from telethon import events


class TelegramStrategy(strategy):

    strategyName = 'Telegram'
    channel = None
    telegramClient = None
    message = None
    apiID = None
    apiSecret = None


    def __init__(self):

        self.importAPIKeys()

        with TelegramClient('name', self.apiID, self.apiSecret) as client:
            self.telegramClient = client
            client.send_message('me', 'New Telegram bot created, listening for alerts...')



    def run(self):
        @self.telegramClient.on(events.NewMessage())
        async def listen(event):
            message = await event.get_chat()
            print(message)
            return message

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
                alert = self.gmailController.createMessage(subject, takeGains[0])
                self.gmailController.sendEmail(alert)

    def runStrategy(self, marketControllers):
        pass