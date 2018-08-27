HEADER_FROM = 14
HEADER_TO = 15
HEADER_SUBJECT = 16
HEADER_DATE = 17

class email:
    sender = None
    data = None
    subject = None
    parameters = {}
    date = None
    validEmail = True
    
    def __init__(self,message):
        self.data = message['body']['data']
        self.subject = message ['header'][HEADER_SUBJECT]
        self.date = message['header'][HEADER_DATE]
        self.sender = message['header'][HEADER_FROM]

    def parseParams(self,text):
        paramText = self.authentication(text)

        paramName = None
        for word in paramText.split():
            if paramName is None and paramName != '\n':
                paramName = word
                if paramName[len(paramName) - 1] == '=':
                    paramName = paramName[:-1]
            else:
                if word[0] != '=':
                    self.parameters.update({paramName: int(word)})


    def authentication(self,data):
        return data