import requests
import base64
import urllib.parse

class Jira:
    def __init__(self,**KW):
        self.input = KW

        # -- authenticate is expected to return headers to be used by the API call
        # https://developer.atlassian.com/server/jira/platform/basic-authentication/
        token_base64 = base64.b64encode(f"{self.input['JIRA_USERNAME']}:{self.input['JIRA_PASSWORD']}".encode()).decode()
        
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
            try:
                req = requests.get(
                    f"{self.input['JIRA_ENDPOINT']}/rest/api/2/search?jql={jql_safe}&startAt={start_idx}&maxResults={block_size}",
                    headers = self.headers,
                    timeout = 30
                )
                req.raise_for_status()
            except:
                print("something went wrong")
                return []

            if req.status_code == 200:
                result = req.json()
                if len(result['issues']) == 0:
                    break
                block_num += 1
                for issue in result['issues']:
                    data.append(issue)
            else:
                print(f"HTTP error code : {req.status_code}")
                return []
        return data
