import discord # Import the discord.py module
from discord.ext import commands # Import the commands extension
from configs import DISCORD_TOKEN # Import the discord token from the configs.py file
import os
import AudioFunc
import asyncio
import SpotifyFunc
import time
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents = intents) # Create a new bot instance

queues = {}
SpotifyFunc = SpotifyFunc.CSpotify()

def check_queue(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if len(queues[ctx.guild.id]) > 0:
        voice.play(queues[ctx.guild.id].pop(0))

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
    await setup_hook()

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
        ctx.send("I left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")

@client.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing()):
        voice.stop()
    else :
        ctx.senc("~~Nothing is playing~~")

@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing()):
        voice.pause()
    else :
        ctx.senc("~~Nothing is playing~~")

@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_paused()):
        voice.resume()
    else :
        ctx.senc("~~Nothing is paused~~")

@client.command(pass_context=True)
async def play_song(ctx, name):
    name = " ".join(name)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    if f'Audio/{name}.wav' not in os.listdir('Audio'):
        AudioFunc.download_song(name)
    voice.play(discord.FFmpegPCMAudio(f'Audio/{name}.wav'), after = lambda e: check_queue(ctx))

@client.command(pass_context=True)
async def queue(ctx,name):
    name = " ".join(name)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if f'Audio/{name}.wav' in os.listdir('Audio'):
        queues[ctx.guild.id].append(name)
    source = discord.FFmpegPCMAudio(f'Audio/{name}.wav')

    guild_id = ctx.message.guild.id

    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id] = [source]

    await ctx.send(f'{name} added to queue')

async def setup_hook():
    client.loop.create_task(background_cleaner())
    client.loop.create_task(background_auth_generating())

client.run(DISCORD_TOKEN)
