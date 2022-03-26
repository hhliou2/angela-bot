# Import Dependencies
import random

import discord
from discord.ext import commands

class Messaging(commands.Cog):
    
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    # Gives a user a Gayness rating of 0-100. Note that Baraboomba is defaulted to the 90-100 range.
    @commands.command()
    async def gay(self, ctx):
        if (ctx.author.id == 352964311423123458):
            gayness = random.randint(90,100)
        else:
            gayness = random.randint(0,100)

        # Write message as an embed
        embed = discord.Embed(description = f'**{ctx.author.name}** is ==> **{gayness}%** gay', color=11342935)
        await ctx.channel.send(embed=embed)

# Give main bot all commands in this file
def setup(bot):
    bot.add_cog(Messaging(bot))

