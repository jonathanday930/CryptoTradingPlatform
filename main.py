

# If modifying these scopes, delete the file token.json.
from gmailHandler import gmailHandler

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



def main():
    gmail = gmailHandler('credentials.json')
    result = gmail.listen(10)
    print('here')

if __name__ == '__main__':
    main()

