import hashlib
import hmac
import urllib
from copy import deepcopy

from jsonref import requests

from markets.marketBaseClass import marketBaseClass


class commas3(marketBaseClass):
    """ """
    name = '3commas'
    header = {}
    urlBase = 'https://api.3commas.io'

    def __init__(self, realMoney, name, *args):
        super().__init__(realMoney, name, *args)
        self.header['apiKey'] = args[0]
        self.header['secretKey'] = args[1]
        self.connect()


    def connect(self):
        """ """
        pass

    def getAmountOfItem(self, val1, val2=None, orderType=None):
        """

        :param val1: 
        :param val2:  (Default value = None)
        :param orderType:  (Default value = None)

        """
        pass

    def encryptOrder(self,requestText,privateKey):
        """

        :param requestText: 
        :param privateKey: 

        """
        return hmac.new(bytes(privateKey, 'utf-8'), bytes(requestText, 'utf-8'), hashlib.sha256).hexdigest()


    def makeOrder(self, order):
        """

        :param order: 

        """
        query = {}
        query['units_to_buy'] = order['amount']
        query['buy_price'] = order['price']
        query['buy_method'] = 'market'
        urlCommand = ''

        urlRequest = urlCommand + urllib.parse.urlencode(query)
        # if need to sign, then:
        headerForOrder = deepcopy(self.header)
        headerForOrder['Signature'] = self.encryptOrder(urlRequest,self.header['secretKey'])
        # response = requests.get(self.urlBase + urlCommand, headers=)

    def interpretType(self, type):
        """

        :param type: 

        """
        pass

    def getCurrentPrice(self, val1, val2=None):
        """

        :param val1: 
        :param val2:  (Default value = None)

        """
        pass