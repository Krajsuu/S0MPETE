import os
import yt_dlp
import requests
import asyncio
from configs import YOUTUBE_API_KEY
from mutagen.wave import WAVE
async def find_song(name):
    #name = name.replace(" ", "_")
    search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={name}&type=video&key={YOUTUBE_API_KEY}'
    response = requests.get(search_url)
    response = response.json()
    url = f'https://www.youtube.com/watch?v={response["items"][0]["id"]["videoId"]}'
    return url

async def download_song(name, path = "Audio"):
    if "https://www.youtube.com" not in name :
        try :
            name = name.replace("_", " ")
            url = await find_song(name)
            name = name.replace(" ", "_")
        except :
            return "Song not found : Wrong Name"
    else :
        url = name
    yt_configs = {
        'format' : 'bestaudio/best',
        'ffmpeg_location' : r'C:\ffmpeg',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'{path}/{name}',
    }
    with yt_dlp.YoutubeDL(yt_configs) as ydl:
        ydl.download([url])

async def delete_song(name, path = "Audio", extension = "wav"):
    os.remove(f'{path}/{name}.{extension}')

async def song_duration(name, path = "Audio"):
    audio = WAVE(f'{path}/{name}')
    return int(audio.info.length)

async def delete_all_songs(path = "Audio"):
    for file in os.listdir(path):
        os.remove(f'{path}/{file}')
