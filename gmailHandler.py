from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

HEADER_FROM = 14
HEADER_TO = 15
HEADER_SUBJECT = 16
HEADER_DATE = 17

class gmailHandler:
    label = 'inbox'
    fromFilter = None
    gmailAPI = None

    def __init__(self,locationOfCredentials):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

    def login(self):
        pass

    # responds with the message
    def listen(self):
        response = self.gmailAPI.users().messages().list(userId='me',
                                                   q='is:unread').execute()

    def readEmails(self,emails):
        messageIds = emails['messages']

        for messageId in messageIds:
            message = self.gmailAPI.users().messages().get(userId='me', id=messageId['id']).execute() 
