'''Jira data extraction'''
import requests
from collector import Collector
import base64
import urllib.parse

class Jira:
    '''
    Jira class
    '''
    def __init__(self,**KW):
        '''
        Setup the main Jira data extraction
        '''
        self.collector = Collector()
        self.collector.log('INFO',f'Starting {__name__}')

        # -- define all the input variables we need for this API
        self.input = self.collector.check_inputs(
            {
                "username" : None,
                "password" : None,
                "endpoint" : None
            },
            **KW
        )

        # -- authenticate is expected to return headers to be used by the API call
        # https://developer.atlassian.com/server/jira/platform/basic-authentication/
        token_base64 = base64.b64encode(f"{self.input['username']}:{self.input['password']}".encode()).decode()
        
        self.headers = {
            "Authorization" : f"Basic {token_base64}",
            "Content-Type"  : "application/json"
        }
        
    def search(self,jql):
        jql_safe = urllib.parse.quote_plus(jql)
        block_size = 100
        block_num = 0
        data = []
        while True:
            start_idx = block_num * block_size
            self.collector.log("INFO",f" - Making API call : Page {block_num}")
            req = requests.get(
                f"{self.input['endpoint']}/rest/api/2/search?jql={jql_safe}&startAt={start_idx}&maxResults={block_size}",
                headers = self.headers,
                timeout = 30
            )

            if req.status_code == 208:
                result = req.json()
                if len(result['issues']) == 0:
                    break
                block_num += 1
                for issue in result['issues']:
                    data.append(issue)
            else:
                self.collector.log('ERROR',f"HTTP error code : {req.status_code}")
                return []

        self.collector.log('SUCCESS',f"Retrieved {len(data)} records")
        return data
