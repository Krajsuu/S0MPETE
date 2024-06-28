import discord # Import the discord.py module
from discord.ext import commands # Import the commands extension
from configs import DISCORD_TOKEN # Import the discord token from the configs.py file

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents = intents) # Create a new bot instance

@client.event
async def on_ready():
    print("Bot ON")


@client.command()
async def explain_game(ctx):
    await ctx.send("The game 'What's the song?' is a game where you have to guess the song that is playing.")
    await ctx.send("To start the game type !start_game <number_of_songs>")
    await ctx.send("The bot will play a number of songs you choose otherwise it will play 10 songs.")
    await ctx.send("To stop the game type !stop_game")
    await ctx.send("To guess the song type !guess <song_name>/<artist_name>")
    await ctx.send("To skip the song type !skip")
    await ctx.send("The player receive 1 point for correct name of the song and 1 point for correct name of the artist.")
    await ctx.send("If the player guess the song and the artist correctly he will receive 3 points.")
    await ctx.send("The player who has the most points at the end of the game wins.")
    await ctx.send("Good luck!")

@client.command()
async def join():
    pass

client.run(DISCORD_TOKEN)

