import time

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import extractedEmail
from extractedEmail import email

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'


class gmailHandler:
    label = 'inbox'
    fromFilter = None
    gmailAPI = None
    refreshTime = 1
    real_money = True
    readEmailCommand = {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}
    lastReceivedEmails = None

    def __init__(self, locationOfCredentials):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(locationOfCredentials, SCOPES)
            creds = tools.run_flow(flow, store)
        self.gmailAPI = build('gmail', 'v1', http=creds.authorize(Http()))

    # responds with the message
    def listen(self, timeoutSeconds):
        count = 0
        while count < timeoutSeconds or timeoutSeconds < 0:

            if not self.real_money:
                response = self.gmailAPI.users().messages().list(userId='me',
                                                             q=' is:unread from:kalgofund@gmail.com').execute()
            else:
                response = self.gmailAPI.users().messages().list(userId='me',
                                                                 q=' is:unread from:noreply@tradingview.com').execute()

            if 'messages' in response:
                return self.readEmails(response)
            else:
                time.sleep(self.refreshTime)
                print("Listened for " + str(count) + " seconds")
                count = count + 1

    def readEmails(self, emails):
        messageIds = emails['messages']
        processedEmails = []

        self.lastReceivedEmails = messageIds

        for messageId in messageIds:
            message = self.gmailAPI.users().messages().get(userId='me', id=messageId['id']).execute()
            if self.authEmail(message):
                processedEmails.append(email(message))

        return processedEmails




    def setEmailsToRead(self):
        for messageId in self.lastReceivedEmails:
            self.gmailAPI.users().messages().modify(userId='me', id=messageId['id'],
                                                    body=self.readEmailCommand).execute()

    def authEmail(self, email):
        return extractedEmail.getParamFromHeader(email['payload']['headers'], 'Subject').find(
            extractedEmail.email.boundaryString) != -1
