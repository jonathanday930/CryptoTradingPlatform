from Bitmex import Bitmex
# If modifying these scopes, delete the file token.json.

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'



def main():

    market = Bitmex(.1, .1, .1, "Bm23pmDAYgPq4JN-bbKipuq_", "gMH-WNVpS17cstY_0YOCe8kirlItoURrsYNCJKd6UhUjyoOp")


if __name__ == '__main__':
    main()

