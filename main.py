import configs
import requests
import json
import base64
def generate_token():
    url = 'https://accounts.spotify.com/api/token'
    string = configs.CLIENT_ID + ":" + configs.CLIENT_SECRET
    string = string.encode("ascii")
    headers = "Basic " + base64.b64encode(string).decode("ascii")
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers={'Authorization': headers}, data=data)
    response = response.json()
    return response['access_token']
#https://open.spotify.com/album/6ArHFD3swnTCCwCeMWM5Oj?si=YD63qkk7SyGn0uwqBLvU1A
token = generate_token()
response = requests.get('https://api.spotify.com/v1/albums/6ArHFD3swnTCCwCeMWM5Oj', headers={'Authorization': 'Bearer ' + token})
print(response.json(), end='\n\n')