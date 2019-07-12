from abc import ABC, abstractmethod


class strategy(ABC):
    """ """

    strategyName = 'Default. You need to override this value'
    # Initializes a strategy. This could mean logging into gmail or twitter. The config file will serve to store any
    # API keys or access info
    def __init__(self, configFile=None):
        pass

    # Checks if it is time to buy or sell, and then returns a list of orders to be made.
    # If you want to store more information in this dict, you can. It will not be removed and will be available when
    # finalizeOrder is run.
    # The function must return a list of dictionaries that follow this format:
    # {'market': 'The market to execute the trade on',
    #  'currency': 'The coin/denomination used for the first part of the pair- usualy BTC or ETH or USDT',
    #  'asset': 'The coin used for the second part- the asset. Could be like VEN,XLM,etc',
    #  'amount': 'The amount of asset to buy/sell',
    #  'action': 'The type of action. Can be either BUY or SELL
    #  'action-type': 'Optional value for the method to buy or sell- such as market, limit, or limit-maker. Implemented on a per market basis',
    #  'price': 'An optional value for the price to buy or sell at. If not included, will just find the current price.
    #  'id': 'An Optional value that is used to ensure that duplicate orders are not carried out. This would be used when an email has been
    #   read but has not been carried out yet, and the strategy code looks to unread emails to create orders. We wouldnt want duplicate messages'}

    @abstractmethod
    def runStrategy(self, marketControllers):
        """

        :param marketControllers: 

        """
        pass

    # Sometimes you want to do something after an order is finished or removed. In this case, there is this function.
    # There will be a value in the dict called 'result' which will contain whether the order was successful or not.
    # If the result value is 0, then it was a success. Might add more things to this depending on what fields are useful.
    # The immediate application of this function is for marking an email as read after the order has been carried out.
    def finalizeOrder(self,order):
        """

        :param order: 

        """
        pass