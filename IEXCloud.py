#import requests
import urllib3
import json

class IEXCloudAPI:
    def __init__(self, key):
        self.key = key

    def dividend_info(self, symbol):
        dividend_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/dividends/2y?token={self.key}'
        http = urllib3.PoolManager()
        response = http.request('GET', dividend_url)
        return json.loads(response.data.decode('utf-8'))

    def split_info(self, symbol):
        split_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/splits/2y?token={self.key}'
        http = urllib3.PoolManager()
        response = http.request('GET', split_url)
        return json.loads(response.data.decode('utf-8'))

    def stats_info(self, symbol):
        stats_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/stats?token={self.key}'
        http = urllib3.PoolManager()
        response = http.request('GET', stats_url)
        return json.loads(response.data.decode('utf-8'))