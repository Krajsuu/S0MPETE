import discord # Import the discord.py module
from discord.ext import commands # Import the commands extension
from configs import DISCORD_TOKEN # Import the discord token from the configs.py file
import os
import AudioFunc
import asyncio
import SpotifyFunc
import time
import DatabaseScript
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents = intents) # Create a new bot instance

SpotifyFunc = SpotifyFunc.CSpotify()
database = DatabaseScript.Database()
async def check_queue(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    while voice.is_playing():
        await asyncio.sleep(7)
    if await database.queue_length(ctx.guild.id) > 0:
        name = await database.pop_top_queue(ctx.guild.id)
        await play_song(ctx, name)

def memory_cleaner(directory = "Audio", age_in_seconds = 900):
    now = time.time()
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > age_in_seconds:
                os.remove(file_path)

async def background_cleaner():
    await client.wait_until_ready()
    while not client.is_closed():
        memory_cleaner()
        await asyncio.sleep(900)

async def background_auth_generating():
    await client.wait_until_ready()
    while not client.is_closed():
        SpotifyFunc.generate_token()
        await asyncio.sleep(3540)

@client.event
async def on_ready():
    print("Bot ON")
    await database.connect()
    await setup_hook()

@client.event
async def on_guild_join(guild):
    database.insert_new_user(guild.id)

@client.event
async def on_guild_remove(guild):
    database.remove_user(guild.id)

@client.command()
async def explain_game(ctx):
    await ctx.send("```The game 'What's the song?' is a game where you have to guess the song that is playing.\nTo start the game type !start_game <number_of_songs>\nThe bot will play a number of songs you choose otherwise it will play 10 songs.\nTo stop the game type !stop_game\nTo guess the song type !guess <song_name>/<artist_name>\nTo skip the song type !skip\nThe player receive 1 point for correct name of the song and 1 point for correct name of the artist.\nIf the player guess the song and the artist correctly he will receive 3 points.\nThe player who has the most points at the end of the game wins.```")
    await ctx.send("```yaml\nGOOD LUCK!\n```")

@client.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        ctx.send("You are not in a voice channel")

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")

@client.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing()):
        voice.stop()
        await restart_queue(ctx)
    else :
        ctx.send("~~Nothing is playing~~")

@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing()):
        voice.pause()
    else :
        ctx.send("~~Nothing is playing~~")

@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_paused()):
        voice.resume()
    else :
        ctx.send("~~Nothing is paused~~")

@client.command(pass_context=True)
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await check_queue(ctx)

@client.command(pass_context=True)
async def play_song(ctx, *args):
    name = "_".join(args)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    if f'Audio/{name}.wav' not in os.listdir('Audio'):
        AudioFunc.download_song(name)
    voice.play(discord.FFmpegPCMAudio(f'Audio/{name}.wav'),  after = lambda e: asyncio.run_coroutine_threadsafe(check_queue(ctx), client.loop))

@client.command(pass_context=True)
async def queue(ctx,*args):
    name = "_".join(args)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    guild_id = ctx.message.guild.id

    await database.add_to_queue(guild_id, name)

    await ctx.send(f'{name.replace("_"," ")} added to queue')

@client.command(pass_context=True)
async def restart_queue(ctx):
    await database.restart_queue(ctx.guild.id)
    await ctx.send("Queue restarted")

async def setup_hook():
    client.loop.create_task(background_cleaner())
    client.loop.create_task(background_auth_generating())

@client.command(pass_context=True)
async def play_queue(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    name = await database.pop_top_queue(ctx.guild.id)
    await play_song(ctx, name)

@client.command(pass_context=True)
async def play_playlist(ctx, playlist_id):
    if("album" in playlist_id):
        await ctx.send("Album is not an playlist! Use command !play_album")
    elif("https://open.spotify.com/playlist/" not in playlist_id):
        await ctx.send("Wrong link!")
    else:
        playlist = playlist_id.split("/")[-1]
        playlist = SpotifyFunc.get_playlist(playlist)
        for song in playlist['tracks']['items']:
            await database.add_to_queue(ctx.guild.id, song['track']['name'])
@client.command(pass_context=True)
async def play(ctx, songs = 10):
    pass

client.run(DISCORD_TOKEN)
