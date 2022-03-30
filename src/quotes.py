# Import Dependencies
import sqlite3
import json

import discord
from discord.ext import commands

with open("./config/admin.json") as f:
    admin_roles = json.load(f)

class Quotes(commands.Cog):
    
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    # Add quote to DB (Admin only)
    @commands.command(pass_context=True)
    @commands.has_any_role(admin_roles["admin"], admin_roles["mod"])
    async def addQuote(self, ctx):

        # First, have the admin add the quote itself
        await ctx.channel.send("Please tell me the quote.")
        quote = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        # Next, have the admin add the user who said the quote
        await ctx.channel.send("Who said this?")
        user = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        # Create example embed and ask user to confirm or cancel
        embed = discord.Embed(description = quote.content, color=0xf1c40f)
        embed.set_footer(text = "-" + user.content)

        await ctx.channel.send("Here is a preview of your quote. Is this OK? (Y/N)")
        await ctx.channel.send(embed=embed)
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        
        # Confirmed: write quote, user, and time to database
        if answer.content.upper() == "Y":
            await ctx.channel.send("OK. Writing to database")

            conn = sqlite3.connect("yga.db")
            cursor = conn.cursor()
            query = f"INSERT INTO QUOTES VALUES ('{quote.content}', '{user.content}', datetime('now'))"
            cursor.execute(query)
            conn.commit()
            conn.close()
        # Cancelled: do nothing
        else:
            await ctx.channel.send("OK. Deleting")

    # Handling non-admins trying to use quote bot
    @addQuote.error
    async def addQuote_error(self, ctx: commands.Context, error: commands.CommandError):
        # Check if it is a role error type
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You cannot add quotes without mod privileges.", delete_after=5)
            await ctx.message.delete(delay=5)


# Give main bot all commands in this file
def setup(bot):
    bot.add_cog(Quotes(bot))

