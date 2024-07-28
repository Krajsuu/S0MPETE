import configs
import requests
import base64

class CSpotify:

    url = 'https://accounts.spotify.com/api/token'

    def __init__(self):
        self.token = self.generate_token()

    def generate_token(self):
        string = configs.CLIENT_ID + ":" + configs.CLIENT_SECRET
        string = string.encode("ascii")
        headers = "Basic " + base64.b64encode(string).decode("ascii")
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.url, headers={'Authorization': headers}, data=data)
        response = response.json()
        return response['access_token']

    def get_album(self, album_id):
        response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}', headers={'Authorization': 'Bearer ' + self.token})
        return response.json()

    def get_playlist_link(self, playlist_id):
        link = f'https://api.spotify.com/v1/playlists/{playlist_id}' + '?market=PL'
        param = {
            'market': 'PL'
        }
        response = requests.get(link, headers={'Authorization': 'Bearer ' + self.token} , params = param)
        return response.json()

    def get_playlist_name(self, playlist_name):
        params = {
            'q' : playlist_name,
            'type' : 'playlist',
            'market' : 'ES'
        }
        response = requests.get('https://api.spotify.com/v1/search', headers={'Authorization': 'Bearer ' + self.token}, params=params)
        response = self.get_playlist_link(response['playlists']['items'][0]['id'])
        return response.json()

