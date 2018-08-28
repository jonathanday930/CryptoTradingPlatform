import base64

HEADER_FROM = 14
HEADER_TO = 15
HEADER_SUBJECT = 16
HEADER_DATE = 17

def getParamFromHeader(messageHeaders,nameOfParam):
    for header in messageHeaders:
        if header['name'] == nameOfParam:
            return header['value']
    return None


class email:
    sender = None
    subject = None
    parameters = None
    date = None
    validEmail = True
    
    def __init__(self,message):
        self.subject = getParamFromHeader(message ['payload']['headers'], 'Subject')
        self.date = getParamFromHeader(message ['payload']['headers'], 'Date')
        self.sender = getParamFromHeader(message ['payload']['headers'], 'From')
        self.parseParams(message['payload'])

    def parseParams(self,messages):
        text = ''
        self.parameters = {}

        if 'parts' in messages:
            messages = messages['parts']
            for message in messages:
                text = text + message['body']['data']
        else:
            text = text + messages['body']

        paramText = self.decode_base64(self.authentication(text))
        #paramText = base64.b64decode(self.authentication(text))
        #paramText = self.authentication(text)

        paramName = None
        for word in paramText.split():
            if not isinstance(word, str):
                pass;
                word = word.decode('ASCII')
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



    def print(self):
        print('Subject:' + self.subject)
        print('From:' + self.sender)
        print('Date:' + self.date)
        print('Parameters:' + str(self.parameters))