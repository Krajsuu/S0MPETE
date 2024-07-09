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

    def get_playlist(self, playlist_id):
        response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}' + '?market=PL', headers={'Authorization': 'Bearer ' + self.token})
        #https://api.spotify.com/v1/playlists/37i9dQZF1EIf4OaZ1XTJYw?market=PL'
        return response.json()
