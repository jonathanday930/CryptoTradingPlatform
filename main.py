# If modifying these scopes, delete the file token.json.
from Bitmex import Bitmex
from gmailHandler import gmailHandler
from controller import controller

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():
    # gmail = gmailHandler('credentials.json')
    # count = 1
    # result = gmail.listen(1)
    # if not result is None:
    #     for email in result:
    #         print(str(count) + ':')
    #         email.print()
    #         count = count + 1

    trader = controller(gmailHandler('credentials.json'))
    trader.addMarket(Bitmex(.01, .01, .01), 'BITMEX')
    trader.run()


if __name__ == '__main__':
    main()
