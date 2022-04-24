# Import Dependencies
import sqlite3
import json

import asyncio
import discord
from discord.ext import commands

with open("./config/admin.json") as f:
    admin_roles = json.load(f)

with open("./config/database.json") as f:
    database_cfg = json.load(f)

class Quotes(commands.Cog):
    
    ###################################################################### 
    # Upon instantiation, set local variable bot to bot entity
    ###################################################################### 
    def __init__(self, bot):
        self.bot = bot

    # Add quote to DB (Admin only)
    @commands.command(pass_context=True, aliases=["addquote"])
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

            conn = sqlite3.connect(database_cfg["database_path"])
            cursor = conn.cursor()
            final_quote = quote.content.replace("'", "''")
            query = f"INSERT INTO QUOTES VALUES ('{final_quote}', '{user.content}', strftime('%m/%d/%Y', date('now')));"
            cursor.execute(query)
            conn.commit()
            conn.close()

            await ctx.channel.send("OK. Written to database")
        # Cancelled: do nothing
        else:
            await ctx.channel.send("OK. Deleting")

    ###################################################################### 
    # Handling non-admins trying to use quote bot
    ###################################################################### 
    @addQuote.error
    async def addQuote_error(self, ctx: commands.Context, error: commands.CommandError):
        # Check if it is a role error type
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You cannot add quotes without mod privileges.", delete_after=5)
            await ctx.message.delete(delay=5)

    ###################################################################### 
    # View quotes based on query
    ###################################################################### 
    @commands.command(pass_context=True)
    async def quote(self, ctx, *, quote_snippet):

        # Edge case: no search term provided
        if quote_snippet == "":
            await ctx.send("Error: no search term provided. Please try again using `!quote [search_term]` (i.e. !quote van)", delete_after=5)
            await ctx.message.delete(delay=5)
            return
        
        # Check if Full Text Search (FTS) table exists
        conn = sqlite3.connect(database_cfg["database_path"])
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM SQLITE_MASTER WHERE TYPE='table' AND NAME='quotes_fts';"
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        # Create an FTS table if it doesn't exist, as well as insert/delete triggers
        if table_exists == 0:
            query = """
            CREATE VIRTUAL TABLE quotes_fts USING FTS5(quote, username, date);
            INSERT INTO quotes_fts (quote, username, date) SELECT quote, username, date FROM quotes;
            
            CREATE TRIGGER quotes_after_insert AFTER INSERT ON quotes
            BEGIN
                INSERT INTO quotes_fts (quote, username, date)
                VALUES (new.quote, new.username, new.date);
            END;

            CREATE TRIGGER quotes_after_delete AFTER DELETE ON quotes
            FOR EACH ROW
            BEGIN
                DELETE FROM quotes_fts WHERE (old.quote = quote);
            END;
            """
            cursor.executescript(query)
            conn.commit()

        # Get all matching quotes based on the user's query
        # Check if user was looking for quote by number
        if quote_snippet.isnumeric():
            query = f"""SELECT rowid, * FROM quotes_fts WHERE rowid = {quote_snippet}"""
            cursor.execute(query)
        else:
            quote_snippet_query = quote_snippet.replace("'", "''").replace('"', '""')
            query = f"""SELECT rowid, * FROM quotes_fts WHERE quote MATCH '"{quote_snippet_query}"' OR username MATCH '"{quote_snippet_query}"' ORDER BY rowid;"""
            cursor.execute(query)

        # Take 5 quotes at a time and embed
        matching_quotes = cursor.fetchall()

        # Edge case 1: User finds no quotes
        if len(matching_quotes) == 0:
            embed = discord.Embed(title="Error!", description="Sorry, I couldn't find a quote matching your search terms.")
            await ctx.send(embed=embed)
            conn.close()
            return

        # Edge case 2: User finds an exact match
        if len(matching_quotes) == 1:
            q = matching_quotes[0]
            embed = discord.Embed(title=f"#{q[0]}", description=q[1])
            embed.set_footer(text=f"-{q[2]}, {q[3]}")
            await ctx.send(embed=embed)
            conn.close()
            return
        
        # Main case: Multiple matches
        embeds = []
        embed = discord.Embed(title="Select Your Quote", description="Scroll through the matched quotes using the available reactions. When you find the quote you want, select it using the quote number, or cancel by typing `cancel`.")
        counter = 0
        for q in matching_quotes:
            # Make a new embed every 5 quotes
            if counter == 5:
                embeds.append(embed)
                embed = discord.Embed(title="Select Your Quote", description="Scroll through the matched quotes using the available reactions. When you find the quote you want, select it using the quote number, or cancel by typing `cancel`.")
                counter = 0

            embed.add_field(name=f"#{q[0]}", value=f"{q[1]}\n-{q[2]}", inline=False)
            counter+=1

        embeds.append(embed)

        # Set up and accept reactions to pages
        hasnt_picked_quote = True
        buttons = database_cfg["buttons"]
        current = 0
        msg = await ctx.send(embed=embeds[current])

        for button in buttons:
            await msg.add_reaction(button)

        try:
            while hasnt_picked_quote:
                done_tasks = None
                check1 = lambda reaction, user: user.id == ctx.author.id and reaction.emoji in buttons
                check2 = lambda message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
    
                pending_tasks = [self.bot.wait_for('reaction_add', check=check1, timeout=60.0), self.bot.wait_for('message', check=check2, timeout=60.0)]
                done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
    
                for task in done_tasks:
                    taskobj = await task
    
                    if isinstance(taskobj, discord.Message):
                        message = taskobj
                        if message.content == 'cancel':
                            await msg.delete()
                            await message.delete()
                            await ctx.message.delete()
                            await ctx.send("Ok, operation cancelled successfully.", delete_after=5)
                            conn.close()
                            return
    
                        try:
                            query = f"""SELECT rowid, * FROM quotes_fts WHERE rowid = {message.content}"""
                            cursor.execute(query)
                            q = cursor.fetchone()
    
                            if q is None:
                                await message.delete()
                                await ctx.send("Error: No such quote, please try again.", delete_after=5)
                                continue
    
                            await msg.delete()
                            await message.delete()
                            await ctx.message.delete()
    
                            embed = discord.Embed(title=f"#{q[0]}", description=q[1])
                            embed.set_footer(text=f"-{q[2]}, {q[3]}")
                            await ctx.send(embed=embed)
                            hasnt_picked_quote = False
                            
                        except sqlite3.OperationalError:
                            await message.delete()
                            await ctx.send("Error: No such quote, please try again.", delete_after=5)
    
                    else:
                        previous_page = current
                        reaction, user = taskobj
                        if reaction.emoji == buttons[0]:
                            current = 0
    
                        elif reaction.emoji == buttons[1]:
                            if current > 0:
                                current -= 1
    
                        elif reaction.emoji == buttons[2]:
                            if current < len(embeds)-1:
                                current  += 1
                        elif reaction.emoji == buttons[3]:
                            current = len(embeds)-1
    
                        if current != previous_page:
                            await msg.edit(embed = embeds[current])
                        for button in buttons:
                            await msg.remove_reaction(button, ctx.author)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
            await ctx.send("Request timed out.", delete_after=5)
            conn.close()
            return

        conn.close()


    ###################################################################### 
    # Handling an empty answer
    ###################################################################### 
    @quote.error
    async def quote_error(self, ctx: commands.Context, error: commands.CommandError):
        # Check if it is missing an argument
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Error: no search term provided. Please try again using `!quote [search_term]` (i.e. !quote van)", delete_after=5)
            await ctx.message.delete(delay=5)

async def setup(bot):
    await bot.add_cog(Quotes(bot))

