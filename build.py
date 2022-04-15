# import dependencies
import os
import logging
import json
import time
import sqlite3

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
intents = discord.Intents.all()
intents.members = True

# Declare bot
with open ("./config/commands.json") as f:
    cfg = json.load(f)

with open ("./config/database.json") as f:
    database_cfg = json.load(f)

bot = commands.Bot(command_prefix = cfg["command_prefix"], intents=intents)

# Let user know bot is online, get all commands
@bot.event
async def on_ready():
    print("Bot going online")
    src.messaging.setup(bot)
    src.roles.setup(bot)
    src.quotes.setup(bot)
    src.music.setup(bot)

    # Initialize SQL Database if not up
    try:
        c = sqlite3.connect(database_cfg['database_path'])
        cursor = c.cursor()
    except sqlite3.Error as error:
        print ('SQL Error - ', error)
        exit(1)

    table = """
            CREATE TABLE IF NOT EXISTS QUOTES (
            QUOTE TEXT,
            USERNAME VARCHAR(255),
            DATE TEXT
            );
            """
    cursor.execute(table)
    c.commit()
    c.close()

# Send bot online with token
try:
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print(f"Error. Check bot token. {e}")
    time.sleep(5)
    exit(1)

