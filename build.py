# import dependencies
import os
import logging
import json
import time
import sqlite3

import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

# Define bot intents:
# - Give/Revoke Roles
# - Make/Read Reactions
# - Read/Post/Delete Messages
# - Join/Speak in Voice Chat
intents = discord.Intents.all()
intents.members = True

# Declare bot configs
with open ("./config/commands.json") as f:
    cfg = json.load(f)

with open ("./config/database.json") as f:
    database_cfg = json.load(f)

class AngelaBot(commands.Bot):

    def __init__(self):
        super().__init__(
                command_prefix = cfg["command_prefix"],
                intents = intents,
                application_id = cfg["application_id"]
                )


    async def setup_hook(self):

        await self.load_extension(f"src.messaging")
        await self.load_extension(f"src.roles")
        await self.load_extension(f"src.quotes")
        await self.load_extension(f"src.music")
        await bot.tree.sync(guild = discord.Object(id = cfg["server_id"]))
        

    async def on_ready(self):

        print("Bot going online")
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
    bot = AngelaBot()
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print(f"Error. Check bot token. {e}")
    time.sleep(5)
    exit(1)

