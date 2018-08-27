import time

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64

from email import email

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



class gmailHandler:
    label = 'inbox'
    fromFilter = None
    gmailAPI = None

    def __init__(self,locationOfCredentials):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(locationOfCredentials, SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))


    # responds with the message
    def listen(self,timeoutSeconds):
        count = 0
        while count < timeoutSeconds:
            response = self.gmailAPI.users().messages().list(userId='me',
                                                   q='is:unread').execute()
            if 'message' in response:
                self.readEmails(response)
            else:
                time.sleep(1)
                count = count + 1


    def readEmails(self,emails):
        messageIds = emails['messages']
        processedEmails = []

        for messageId in messageIds:
            message = self.gmailAPI.users().messages().get(userId='me', id=messageId['id']).execute()
            processedEmails.append(email(message))
