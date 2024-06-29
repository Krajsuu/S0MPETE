import os
import yt_dlp
import requests
from configs import YOUTUBE_API_KEY
def find_song(name):
    #name = name.replace(" ", "_")
    search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={name}&type=video&key={YOUTUBE_API_KEY}'
    response = requests.get(search_url)
    response = response.json()
    url = f'https://www.youtube.com/watch?v={response["items"][0]["id"]["videoId"]}'
    return url

def download_song(name, path = "Audio"):
    if "https://www.youtube.com" not in name :
        try :
            url = find_song(name)
        except :
            return "Song not found : Wrong Name"
    else :
        url = name
    yt_configs = {
        'format' : 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'{path}/{name}',
    }
    with yt_dlp.YoutubeDL(yt_configs) as ydl:
        ydl.download([url])

def delete_song(name, path = "Audio", extension = "wav"):
    os.remove(f'{path}/{name}.{extension}')

def delete_all_songs(path = "Audio"):
    for file in os.listdir(path):
        os.remove(f'{path}/{file}')
