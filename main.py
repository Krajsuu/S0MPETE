import discord # Import the discord.py module
from discord.ext import commands # Import the commands extension
from configs import DISCORD_TOKEN # Import the discord token from the configs.py file
import os
import AudioFunc
import asyncio
import SpotifyFunc
import time
import DatabaseScript
import random
import json
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents = intents) # Create a new bot instance
SpotifyFunc = SpotifyFunc.CSpotify()
database = DatabaseScript.Database()

async def check_queue(ctx):
    '''
    Function that checks if the queue is empty and if not plays the next song
    :param ctx:
    :return:
    '''
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    while voice.is_playing():
        await asyncio.sleep(7)
    if await database.check_loop(ctx.guild.id):
        name = await database.get_current_song(ctx.guild.id)
        await play(ctx,name)
    elif await database.queue_length(ctx.guild.id) > 0:
        name = await database.pop_top_queue(ctx.guild.id)
        await playSong(ctx, name)

async def memory_cleaner(directory = "Audio", age_in_seconds = 900):
    '''
    Function that removes files from the directory that are older than age_in_seconds
    :param directory:
    :param age_in_seconds:
    :return:
    '''
    now = time.time()
    tasks = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > age_in_seconds:
                tasks.append(check_and_remove(file, file_path))

    await asyncio.gather(*tasks)

async def check_and_remove(file, file_path):
    if not await database.check_loop(file):
        os.remove(file_path)

async def background_cleaner():
    """
    Function that runs in the background and cleans the memory every 15 minutes
    :return:
    """
    await client.wait_until_ready()
    while not client.is_closed():
        await memory_cleaner()
        await asyncio.sleep(900)


async def background_auth_generating():
    """
    Function that runs in the background and generates the auth token every 59 minutes
    :return:
    """
    await client.wait_until_ready()
    while not client.is_closed():
        await SpotifyFunc.generate_token()
        await asyncio.sleep(3540)

@client.event
async def on_ready():
    """
    Function that runs when the bot is ready
    :return:
    """
    print("Bot ON")
    await database.connect()
    await setup_hook()

@client.event
async def on_guild_join(guild):
    await database.insert_new_user(guild.id)

@client.event
async def on_guild_remove(guild):
    await database.remove_user(guild.id)

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
        await database.reset_current_song(ctx.guild.id)
        await database.unloop_song(ctx.guild.id)
    else :
        ctx.send("~~Nothing is playing~~")

@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_playing() and ctx.author.voice):
        voice.pause()
    else :
        ctx.send("~~Nothing is playing~~")

@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice.is_paused() and ctx.author.voice):
        voice.resume()
    else :
        ctx.send("~~Nothing is paused~~")

@client.command(pass_context=True)
async def skip(ctx):
    if await database.check_loop(ctx.guild.id):
        await ctx.send("Can't skip looped song")
    elif ctx.author.voice:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        voice.stop()
        await check_queue(ctx)

@client.command(pass_context=True)
async def play(ctx, *args):
    if ctx.author.voice:
        name = "_".join(args)
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
        await playSong(ctx, name)
    else :
        await ctx.send("You are not in a voice channel")

async def playSong(ctx, song):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if f'{song}.wav' not in os.listdir('Audio'):
        await AudioFunc.download_song(song)
    voice.play(discord.FFmpegPCMAudio(f'Audio/{song}.wav'), after=lambda e: asyncio.run_coroutine_threadsafe(check_queue(ctx), client.loop))
    await database.change_current_song(ctx.guild.id, song)

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
    if ctx.author.voice:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
        name = await database.pop_top_queue(ctx.guild.id)
        await play(ctx, name)

@client.command(pass_context=True)
async def change_playlist(ctx, playlist_id):
    if("https://open.spotify.com/playlist/" not in playlist_id):
        await ctx.send("Wrong link!")
    else:
        await database.change_playlist(ctx.guild.id, playlist_id)
        await ctx.send("Playlist changed")

@client.command(pass_context=True)
async def play_playlist(ctx):
    if ctx.author.voice:
        response = database.get_playlist(ctx.guild.id)
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if response and database.check_loop(ctx.guild.id) and not voice.is_playing():
            playlist = response.split("/")[-1]
            playlist = await SpotifyFunc.get_playlist_link(playlist)
            for song in playlist['tracks']['items']:
                await database.add_to_queue(ctx.guild.id, song['track']['name'])
            await play_queue(ctx)
        else:
            await ctx.send("Can't play playlist")

async def create_file(players, guildID):
    with open(f"Game_{guildID}.json", "w") as file:
        for player in players:
            file.write(f"{player}\n")


@client.command(pass_context=True)
async def test(ctx):
    def check_message(message):
        print("test")
        print(message)
        print(type(message.author.name))
        print(dir(message))
        print(message.content)
        print(message.author.name)
    try:
        message = await client.wait_for('message', timeout=35, check=check_message)
    except:
        print("Time is up")

@client.command(pass_context=True)
async def startgame(ctx, NumOfSongs = 10):
    if ctx.author.voice:
        voice_channel = ctx.message.author.voice.channel
        text_channel = ctx.message.channel
        amount_of_members = len(voice_channel.members)
        if amount_of_members < 3:
            await ctx.send("Not enough players")
            return
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            await database.reset_current_song(ctx.guild.id)
            await database.unloop_song(ctx.guild.id)
        players = []
        for member in voice_channel.members:
            players.append(member.name)
        songs = []
        playlist = await database.get_playlist(ctx.guild.id)
        playlist = playlist.split("/")[-1]
        playlist = await SpotifyFunc.get_playlist_link(playlist)
        playlist_length = len(playlist['tracks']['items'])
        if playlist_length < NumOfSongs:
            NumOfSongs = playlist_length
        AvailableSongs = [True] * playlist_length
        for song in range(NumOfSongs):
            RandomSong = random.randint(0, playlist_length - 1)
            if AvailableSongs[RandomSong]:
                author = playlist['tracks']['items'][RandomSong]['track']['artists'][0]['name'].replace(' ','_')
                title = playlist['tracks']['items'][RandomSong]['track']['name'].replace(' ','_')
                songs.append(f"{author.lower}-{title.lower}")
                AvailableSongs[RandomSong] = False
        await database.save_game_info(ctx.guild.id, songs,players, text_channel)
        players = dict.fromkeys(players, 0)
        with open(f"Game_{ctx.guild.id}.json", "w") as file:
            json.dump(players, file)
        await ctx.send("Game started")
        await game(ctx)

async def game(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    response = await database.next_game_round(ctx.guild.id)
    channel = database.get_game_channel(ctx.guild.id)
    result = {3: [], 1: []}
    resultAvability = {"Full": True, "Artist": True, "Song": True}
    def check_message(message):
        with open(f"Game_{ctx.guild.id}.json", "r") as file:
            result = json.load(file)
        players = list(result.keys())
        if message.channel == channel and message.author.name in players:
            message = message.lower().split()
            if resultAvability["Full"] == True:
                for word in name:
                    if word in message:
                        if resultAvability["Full"] == True and resultAvability["Artist"] == True:
                            if message.author in result[1]:
                                resultAvability["Full"] = False
                                result[1] = []
                                result[3].append(message.author)
                            else:
                                resultAvability["Artist"] = False
                                result[1].append(message.author)
                        break
                for word in title:
                    if word in message:
                        if resultAvability["Song"] == False and message.author in result[1]:
                            resultAvability["Full"] = False
                            result[3].append(message.author)


    while response :
        song = database.get_game_song(ctx.guild.id)
        name = song.split("-")[0]
        title = song.split("-")[1]
        full_title = name + "_" + title
        len = await AudioFunc.song_duration(song)
        if len > 60:
            start = random.randint(12, len - 40)
        else:
            start = 0
        if f'Audio/{full_title}.wav' not in os.listdir('Audio'):
            await AudioFunc.download_song(full_title)
        await voice.play(discord.FFmpegPCMAudio(f'Audio/{full_title}.wav', before_options=f"-ss {start} -t 30"))
        try:
            message = await client.wait_for('message', timeout=35, check = check_message)

        except:
            await ctx.send(f"Time is up! The song was {title} by {name}")
            await database.next_game_round(ctx.guild.id)
            continue
        for points in result:
            for player in result[points]:
                with open(f"Game_{ctx.guild.id}.json", "r") as file:
                    players = json.load(file)
                players[player] += points
                with open(f"Game_{ctx.guild.id}.json", "w") as file:
                    json.dump(players, file)

        response = await database.next_game_round(ctx.guild.id)
        result = {3:[],1:[]}
        resultAvability = {"Full": True, "Artist": True, "Song": True}
    await ctx.send("Game ended")
    await database.end_game(ctx.guild.id)
    with open(f"Game_{ctx.guild.id}.json", "r") as file:
        players = json.load(file)
    players = sorted(players)
    message = "The end! Congratulation players! The final score is:\n"
    for player in players:
        message += f"{player}: {players[player]}\n"





    
@client.command()
async def loop(ctx):
    if not await database.check_loop(ctx.guild.id) and ctx.author.voice:
        await database.loop_song(ctx.guild.id)
        await ctx.send("Looped")
    elif ctx.author.voice:
        await database.unloop_song(ctx.guild.id)
        await ctx.send("Unlooped")

client.run(DISCORD_TOKEN)
