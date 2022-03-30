# Import Dependencies
import sqlite3

import discord
from discord.ext import commands

class Quotes(commands.Cog):
    
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_any_role("Yummy Admins", "Yummy Mods")
    async def addQuote(self, ctx):

        await ctx.channel.send("Please tell me the quote.")
        quote = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.channel.send("Who said this?")
        user = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        embed = discord.Embed(description = quote.content, color=0xf1c40f)
        embed.set_footer(text = "-" + user.content)

        await ctx.channel.send("Here is a preview of your quote. Is this OK? (Y/N)")
        await ctx.channel.send(embed=embed)
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        
        if answer.content.upper() == "Y":
            await ctx.channel.send("OK. Writing to database")

            conn = sqlite3.connect("yga.db")
            cursor = conn.cursor()
            query = f"INSERT INTO QUOTES VALUES ('{quote.content}', '{user.content}', datetime('now'))"
            cursor.execute(query)
            conn.commit()
            conn.close()
        else:
            await ctx.channel.send("OK. Deleting")


# Give main bot all commands in this file
def setup(bot):
    bot.add_cog(Quotes(bot))

