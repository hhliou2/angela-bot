# import dependencies
import os
import logging
import json
import time

import discord
from discord.ext import commands

from dotenv import load_dotenv

import src

load_dotenv()

# Define bot intents:
# - Give/Revoke Roles
# - Make/Read Reactions
# - Read/Post/Delete Messages
# - Join/Speak in Voice Chat
intents = discord.Intents.default()
intents.members = True

# Declare bot
with open ("./config/commands.json") as f:
    cfg = json.load(f)

bot = commands.Bot(command_prefix = cfg["command_prefix"], intents=intents)

# Let user know bot is online, get all commands
@bot.event
async def on_ready():
    print("Bot going online")
    src.messaging.setup(bot)

# Send bot online with token
try:
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print("Error. Check bot token.")
    time.sleep(5)
    exit(1)

