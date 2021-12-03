from decouple import config
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.messages = True

client = commands.Bot(command_prefix=('m.', 'miku ', 'Miku ', 'M.'), case_insensitive=True, intents=intents)

def load_cogs():
  for file in os.listdir("./cogs"):
    if file.endswith(".py") and not file.startswith("_"):
      client.load_extension(f"cogs.{file[:-3]}")

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"BlackBear!"))
  load_cogs()
  print(">> Cogs loaded.")
  print(f">> Logged in as : {client.user.name} \n>> ID : {client.user.id}")
  print(f">> Total Servers : {len(client.guilds)}")
  print('>> Kanna is Online.')

token = config("TOKEN")
client.run(token)