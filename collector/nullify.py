'''Nullify data extraction'''
import requests
from collector import Collector

class Nullify:
    '''
    Nullify class
    '''
    def __init__(self,**KW):
        '''
        Setup the main Nullify data extraction
        '''
        self.collector = Collector()
        self.collector.log('INFO',f'Starting {__name__}')

        # -- define all the input variables we need for this API
        self.input = self.collector.check_inputs(
            {
                'token'     : None,
                'endpoint'  : None,
                'githubOwnerId' : None
            },
            **KW
        )

        # -- authenticate is expected to return headers to be used by the API call
        self.headers = {
            "Authorization" : f"Bearer {self.input['token']}",
            "Accept"        : "application/json",
        }

    def sca_events(self,fromTime = '2024-01-22T00:00:00Z'):
        print(f"{self.input['endpoint']}/sast/events?githubOwnerId={self.input['githubOwnerId']}&fromTime={fromTime}")
        req = requests.get(
            f"{self.input['endpoint']}/sast/events?githubOwnerId={self.input['githubOwnerId']}&fromTime={fromTime}",
            headers = self.headers,
            timeout = 30
        )
        if req.status_code != 200:
            print(req.content)
            return []
        else:
            response = req.json()
            return response['events']
        
    def sca_counts(self):
        req = requests.get(
            f"{self.input['endpoint']}/sca/counts/severity/latest?githubOwnerId={self.input['githubOwnerId']}",
            headers = self.headers,
            timeout = 30
        )
        if req.status_code != 200:
            print(req.content)
            return []
        else:
            response = req.json()
            return response['counts']

    def sast_events(self,fromTime = '2006-01-02T15:04:05Z'):
        req = requests.get(
            f"{self.input['endpoint']}/sast/events?githubOwnerId={self.input['githubOwnerId']}&fromTime={fromTime}",
            headers = self.headers,
            timeout = 30
        )
        if req.status_code != 200:
            print(req.content)
            return []
        else:
            response = req.json()
            return response['events']
