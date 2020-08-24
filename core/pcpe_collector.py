import requests
import time
import datetime

class PrometheusWrapper(object):
    
    def __init__(self, **kwargs):
        
        self.PROMETHEUS_SERVER = 'http://demo.robustperception.io:9090/'
        #self.PROMETHEUS_SERVER = 'http://10.7.229.183:9090/'
        self.PROMETHEUS_API = self.PROMETHEUS_SERVER + '/api/v1/query' 
        
    def runQuery(self, query):
        
        response = requests.post(self.PROMETHEUS_API,
                                params={
                                    'query': query
                                })
        results = response.json()['data']['result']
        return results