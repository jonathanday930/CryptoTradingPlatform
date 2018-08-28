

# If modifying these scopes, delete the file token.json.
from gmailHandler import gmailHandler

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



def main():
    gmail = gmailHandler('credentials.json')
    result = gmail.listen(1000)
    count = 1
    for email in result:
        print(str(count) + ':')
        email.print()
        count = count + 1

if __name__ == '__main__':
    main()

