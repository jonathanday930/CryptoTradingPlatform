from googleapiclient.discovery import build
from httplib2 import Http

from oauth2client import file, client, tools

from markets import marketBaseClass

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

from strategies.strategy import strategy
from markets.marketBaseClass import marketBaseClass


class gmailStrategy(strategy):
    strategyName = 'Gmail'

    label = 'inbox'
    fromFilter = None
    gmailAPI = None
    refreshTime = 1
    real_money = False
    readEmailCommand = {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}

    boundaryString = '$$'
    assetSubjectNumber = 1
    currencySubjectNumber = 0
    typeSubjectNumber = 2
    marketSubjectNumber = 3

    def __init__(self, configFile=None):

        super().__init__(configFile)
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(configFile, SCOPES)
            creds = tools.run_flow(flow, store)
        self.gmailAPI = build('gmail', 'v1', http=creds.authorize(Http()))

    def runStrategy(self, marketControllers):

        if not self.real_money:
            response = self.gmailAPI.users().messages().list(userId='me',
                                                             q=' is:unread from:kalgofund@gmail.com').execute()
        else:
            response = self.gmailAPI.users().messages().list(userId='me',
                                                             q=' is:unread from:noreply@tradingview.com').execute()
        if 'messages' in response:
            return self.readEmails(response)
        else:
            return []

    def interpretType(self, word):
        if word.upper() == 'LONG':
            return marketBaseClass.buyText
        else:
            if word.upper() == 'SHORT':
                return marketBaseClass.sellText
            else:
                return word

    # Returns a list of orders created from the email
    def readEmails(self, emails):
        messageIds = emails['messages']

        orders = []
        for messageId in messageIds:
            message = self.gmailAPI.users().messages().get(userId='me', id=messageId['id']).execute()
            if self.authEmail(message):
                params = self.getSubjectMessage(message)

                order = {'currency': params[self.currencySubjectNumber], 'asset': params[self.assetSubjectNumber],
                         'action': self.interpretType(params[self.typeSubjectNumber]),
                         'market': params[self.marketSubjectNumber],
                         'action-type': 'LIMIT', 'id': messageId['id']}
                orders.append(order)
        return orders

    def getSubjectMessage(self, email):
        subject = self.getSubjectFromMessage(email)

        firstIndex = subject.find(self.boundaryString)
        secondIndex = subject.find(self.boundaryString, firstIndex + 1)
        return subject[firstIndex + self.boundaryString.__len__():secondIndex].split()

    def getSubjectFromMessage(self, email):
        for header in email['payload']['headers']:
            if header['name'] == 'Subject':
                return header['value']

    def finalizeOrder(self, order):
        if str(order['result']) == str(0):
            self.setEmailToRead(order['id'])

    def setEmailToRead(self, messageID):
        self.gmailAPI.users().messages().modify(userId='me', id=messageID,
                                                body=self.readEmailCommand).execute()

    def authEmail(self, email):
        return self.getSubjectFromMessage(email).find(
            self.boundaryString) != -1
