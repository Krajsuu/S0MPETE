import configs
import aiohttp
import base64
import asyncio

class CSpotify:

    url = 'https://accounts.spotify.com/api/token'

    def __init__(self):
        self.token = asyncio.run(self.generate_token())

    async def generate_token(self):
        string = configs.CLIENT_ID + ":" + configs.CLIENT_SECRET
        string = string.encode("ascii")
        headers = "Basic " + base64.b64encode(string).decode("ascii")
        data = {
            'grant_type': 'client_credentials'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers={'Authorization': headers}, data=data) as response:
                response = await response.json()
                return response['access_token']

    async def get_album(self, album_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.spotify.com/v1/albums/{album_id}', headers={'Authorization': 'Bearer ' + self.token}) as response:
                return await response.json()

    async def get_playlist_link(self, playlist_id):
        link = f'https://api.spotify.com/v1/playlists/{playlist_id}' + '?market=PL'
        param = {
            'market': 'PL'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers={'Authorization': 'Bearer ' + self.token}, params=param) as response:
                return await response.json()

    async def get_playlist_name(self, playlist_name):
        params = {
            'q': playlist_name,
            'type': 'playlist',
            'market': 'ES'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.spotify.com/v1/search', headers={'Authorization': 'Bearer ' + self.token}, params=params) as response:
                search_response = await response.json()
                playlist_id = search_response['playlists']['items'][0]['id']
                return await self.get_playlist_link(playlist_id)
