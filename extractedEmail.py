import base64

HEADER_FROM = 14
HEADER_TO = 15
HEADER_SUBJECT = 16
HEADER_DATE = 17

class email:
    sender = None
    subject = None
    parameters = {}
    date = None
    validEmail = True
    
    def __init__(self,message):
        self.subject = message ['payload']['headers'][HEADER_SUBJECT]
        self.date = message['payload']['headers'][HEADER_DATE]
        self.sender = message['payload']['headers'][HEADER_FROM]
        self.parseParams(message['payload']['parts'])

    def parseParams(self,messages):
        text = ''

        for message in messages:
            text = text + message['body']['data']

        paramText = base64.b64decode(self.authentication(text))


        paramName = None
        for word in paramText.split():
            if paramName is None and paramName != '\n':
                paramName = word
                if paramName[len(paramName) - 1] == '=':
                    paramName = paramName[:-1]
            else:
                if word[0] != '=':
                    self.parameters.update({paramName: word})
                    paramName = None


    def authentication(self,data):
        return data