import requests

class Nullify:
    def __init__(self,**KW):
        self.input = KW
        
        # -- authenticate is expected to return headers to be used by the API call
        self.headers = {
            "Authorization" : f"Bearer {self.input['NULLIFY_TOKEN']}",
            "Accept"        : "application/json",
        }

    def sca_events(self,fromTime = '2024-03-01T00:00:00Z'):
        data = []
        nextEventId = ''
        while True:
            print(f"nextEventId = {nextEventId} - {len(data)}")
            req = requests.get(
                f"{self.input['NULLIFY_ENDPOINT']}/sca/events?githubOwnerId={self.input['NULLIFY_GITHUB_OWNER_ID']}&fromTime={fromTime}&fromEvent={nextEventId}",
                headers = self.headers,
                timeout = 30
            )
            if req.status_code != 200:
                return []
            else:
                response = req.json()
                if response['events'] is not None:
                    data += response['events']
                if 'nextEventId' in response and response['events'] is not None and response['events'] != []:
                    nextEventId = response['nextEventId']
                else:
                    break
        return data

    def sast_events(self,fromTime = '2024-03-01T00:00:00Z'):
        data = []
        nextEventId = ''
        while True:
            print(f"nextEventId = {nextEventId} - {len(data)}")
            req = requests.get(
                f"{self.input['NULLIFY_ENDPOINT']}/sast/events?githubOwnerId={self.input['NULLIFY_GITHUB_OWNER_ID']}&fromTime={fromTime}&fromEvent={nextEventId}",
                headers = self.headers,
                timeout = 30
            )
            if req.status_code != 200:
                return []
            else:
                response = req.json()
                if response['events'] is not None:
                    data += response['events']
                if 'nextEventId' in response and response['events'] is not None:
                    nextEventId = response['nextEventId']
                else:
                    break
        return data
        
    def sca_counts(self):
        req = requests.get(
            f"{self.input['NULLIFY_ENDPOINT']}/sca/counts/severity/latest?githubOwnerId={self.input['NULLIFY_GITHUB_OWNER_ID']}",
            headers = self.headers,
            timeout = 30
        )
        if req.status_code != 200:
            print(req.content)
            return []
        else:
            response = req.json()
            return response['counts']
        
    def admin_repositories(self):
        req = requests.get(
            f"{self.input['NULLIFY_ENDPOINT']}/admin/repositories?githubOwnerId={self.input['NULLIFY_GITHUB_OWNER_ID']}",
            headers = self.headers,
            timeout = 30
        )
        if req.status_code != 200:
            print(req.content)
            return []
        else:
            response = req.json()
            return response['counts']
