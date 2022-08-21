import base64
import requests
import datetime
from urllib.parse import urlencode

client_id = '67b2ba6ce11547e6b7f5d8459aaaa09c'
client_secret = '4cd84636dbec44efb84c9bac251a9aa0'

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

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')
        
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')


    def search(self, query, search_type='artist'):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type": search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code in range(200,299):
            return r.json()
        return {}


client = SpotifyAPI(client_id, client_secret)
#print(client.get_artist("1hCkSJcXREhrodeIHQdav8"))
print(client.get_album("41zMFsCjcGenYKVJYUXU2n"))
#print(client.search("A lannister always pays his debts", search_type="track"))
client.access_token

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






