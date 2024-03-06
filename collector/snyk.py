import requests

class Snyk:
    def __init__(self,**KW):
        self.input = KW

        self.headers = {
            "Authorization" : f"token {self.input['SNYK_TOKEN']}",
            "Content-Type"  : "application/json",
            "Accept"        : "application/vnd.api+json" 
        }
        self.endpoint = 'https://api.snyk.io'

    def snyk_call(self,url):
        nexturl = f"{self.endpoint}{url}?version=2024-02-28&limit=100"
        data = []
        while True:
            print(f"Snyk -> {len(data)}")
            req = requests.get(
                nexturl,
                headers = self.headers,
                timeout=30
            )
            
            if req.status_code == 200:
                data += req.json()['data']
                if 'next' in req.json()['links']:
                    nexturl = f"{self.endpoint}{req.json()['links']['next']}"
                else:
                    break
            else:
                print(req.status_code)

        return data

        
