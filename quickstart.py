import os


from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    #os.system('set GOOGLE_APPLICATION_CREDENTIALS= "C:\Users\juliann\PycharmProjects\TradingViewTrader\TradingView-671a4e28ff18" ')

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
         flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
         creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    response = service.users().messages().list(userId='me',
                                               q='is:unread').execute()
    messageId = response['messages'][0]['id']

    message = service.users().messages().get(userId='me', id=messageId).execute()
    ex = message['payload']['body']

    coded_string = message['payload']['parts'][0]['body']['data']
    print (coded_string)
    print(base64.b64decode(coded_string))

    # print(message['payload']['body'])
    # print(message['payload']['headers'])
    # print('a')
if __name__ == '__main__':
    main()

