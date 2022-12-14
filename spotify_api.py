import base64
import requests
import datetime
from urllib.parse import urlencode


#hide client_id and client_secret (still to do!!)
client_id = '67b2ba6ce11547e6b7f5d8459aaaa09c'
client_secret = '4cd84636dbec44efb84c9bac251a9aa0'

#Api models to used from here and place it into app.py file
#For homepage i need to create another method that allows me to get for example newest tracks released on spotify (to do!!)
class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_credentials = f'{client_id}:{client_secret}'
        client_credentials_b64 = base64.b64encode(client_credentials.encode())
        return client_credentials_b64.decode()

    def get_token_headers(self):
        client_credentials_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_credentials_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        request = requests.post(token_url, data=token_data, headers=token_headers)
        if request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client")
        data = request.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        self.access_token = access_token
        expires_in = data['expires_in'] #seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    #Getting resources area
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resources(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def get_resource(self, resource_type='artists', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resources(_id, resource_type='albums')
        
    def get_artist(self, _id):
        return self.get_resources(_id, resource_type='artists')
    #Not working
    def get_several_artists(self):
        return self.get_resource(resource_type='artists')

    def get_new_releases(self):
        endpoint = f"https://api.spotify.com/v1/browse/new-releases"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        response = r.json()
        if r.status_code not in range(200,299):
            return {}
        return response['albums']['items']
        
        #return self.get_resource(resource_type="browse/new-releases")

    def search(self, query, search_type='artist'):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type": search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code in range(200,299):
            return r.json()
        return {}
    
    def improved_search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.search(query_params)



client = SpotifyAPI(client_id, client_secret)
#print(client.get_artist("1hCkSJcXREhrodeIHQdav8"))
print(client.get_new_releases())
#print(client.improved_search(query="Time", operator="NOT", operator_query="Billie Ellish", search_type="track"))
#print(client.search("A lannister always pays his debts", search_type="track"))


#Propper search endpoint
def endpoint_data():
    access_token = client.access_token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    endpoint = "https://api.spotify.com/v1/search"
    data = urlencode({"q": "Time", "type": "track"})
    lookup_url = f"{endpoint}?{data}"
    r = requests.get(lookup_url, headers=headers)
    print(r.json())






