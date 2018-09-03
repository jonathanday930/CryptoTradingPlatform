import base64
import re

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
    boundaryString = '$$'


    def __init__(self,message):
        self.subject = getParamFromHeader(message ['payload']['headers'], 'Subject')
        self.date = getParamFromHeader(message ['payload']['headers'], 'Date')
        self.sender = getParamFromHeader(message ['payload']['headers'], 'From')
        self.parseSubjectForParams()


    def parseSubjectForParams(self):
        self.parameters = []

        for word in self.subjectAuth(self.subject).split():
            self.parameters.append(word)


    def parseBodyForParams(self,messages):
        text = " "
        self.parameters = {}

        if 'parts' in messages:
            messages = messages['parts']
            for message in messages:
                strin = str(message['body']['data'])
                text = str(text) + str(base64.urlsafe_b64decode(strin))
        else:
            text = text + base64.urlsafe_b64decode(messages['body'])

        text = text.encode().decode()
        paramText = self.authentication(text)

        print(paramText)
        paramName = None
        for word in paramText.split():
            if not isinstance(word, str):
                pass;
            if paramName is None and paramName != '\n':
                paramName = word
                if paramName[len(paramName) - 1] == '=':
                    paramName = paramName[:-1]
            else:

                if word[0] != '=':
                    self.parameters.update({paramName: word})
                    paramName = None

    def authentication(self,data):

        f = open(self.filterFileName, "r")

        data = self.cleanhtml(data)

        for line in f:
            line = line.replace('\n','')
            #line = line.replace('\','',1)
            data = data.replace(line,"")

        return data

    def cleanhtml(self,raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


    def print(self):
        print('Subject:' + self.subject)
        print('From:' + self.sender)
        print('Date:' + self.date)
        print('Parameters:' + str(self.parameters))

    def subjectAuth(self, subject):
        firstIndex = subject.find(self.boundaryString)

        secondIndex = subject.find(self.boundaryString,firstIndex + 1)
        return subject[firstIndex + self.boundaryString.__len__():secondIndex]

    'adawdwdw TEST $$ EOS SHORT 2hr $$'