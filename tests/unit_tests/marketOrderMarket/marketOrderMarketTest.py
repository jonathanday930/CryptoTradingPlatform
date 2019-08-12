import json
import os

from tests.unit_tests.marketOrderMarket.marketOrderMarket_Mock import marketOrderMarket_Mock

def test_allConfigs():
    path = 'tests/unit_tests/marketOrderMarket/'
    tests = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and f != '__pycache__']
    for test in tests:
        singleTest(os.path.join(path, test))

def singleTest(folder):
    prices = os.path.join(folder,"prices.txt")
    amounts = os.path.join(folder,"amounts.txt")
    order = os.path.join(folder,"order.json")
    with open(order, 'r') as log_json:
        data = json.load(log_json)
    order = data

    mock_market = marketOrderMarket_Mock(False,"mock",prices,amounts)
    mock_market.connect()
    mock_market.makeOrder(order)
