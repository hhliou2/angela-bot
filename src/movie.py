import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import datetime
from discord.ext import commands

movies = {}
scheduler = AsyncIOScheduler()
scheduler.start()
movierole = 'Clubhouse Member'


class Movie(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    async def moviescheduler(self, ctx, selection):
        print(f'Begin scheduled movie {selection}')
        if selection not in movies:
            print(f'WARN: Movie {selection} in scheduler no longer exists!')
            return
        else:
            tomention = []
            for user in movies[selection]['users'].keys():
                tomention.append(f'<@{user}>\n')
            if tomention:
                await ctx.channel.send(f"It's movie night everybody! Come on and watch **{selection}** with:")
                users = '\n'.join(user for user in tomention)
                await ctx.channel.send(f'\n{users}')
                del movies[selection]
            else:
                print(f'Error: tomention is empty {tomention}')

    @commands.command(aliases=['mn'])
    @commands.has_role(movierole)
    async def movienight(self, ctx):
        mlist = []
        if movies:
            for film in movies:
                mlist.append(f'**{movies[film]["title"]}** at **{movies[film]["date"]}**')              # Add all movies to our list
            embed = discord.Embed(title='**Available Movies:**', description=f'\n'.join(film for film in mlist))      # Send movie list
            await ctx.channel.send(embed=embed)
            embed = discord.Embed(title='**To sign up to watch a movie:**', description=f'Type `!watch <moviename>`')
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title='**No Movies Available!**', description=f'To add a movie, type `!newmovie`')
            await ctx.channel.send(embed=embed)

    @commands.command(aliases=[])
    @commands.has_role(movierole)
    async def watch(self, ctx, *, signup):
        lp = True
        movtemp = None
        while lp:
            # signup = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            for film in movies:
                if str(signup).lower() in movies[film]['title'].lower():      # Check if movie exists
                    movtemp = film
                    if ctx.author.id in movies[movtemp]['users']:
                        await ctx.channel.send('''You are already seeing this movie. \n
                        Would you like to be taken off the list? (Y/N)''')
                        ans = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if ans.content.lower() == 'y' or ans.content.lower() == 'yes':
                            movies[movtemp]['users'].pop(ctx.author.id)                   # Remove user from movie list
                            await ctx.channel.send('Removed from list')
                            print(f'{ctx.author.name} removed from {movtemp}')
                        lp = False
                        break

                    else:
                        movies[movtemp]['users'][ctx.author.id] = ctx.author.name       # Add user to movie list
                        print(f'{ctx.author.name} added to {movtemp}')
                        await ctx.channel.send(f'Added you to the list for **{movtemp}**')
                        lp = False
                        break

            if str(signup) == 'cancel':
                await ctx.channel.send('Operation Canceled')
                lp = False
            elif not movtemp:
                await ctx.channel.send('Invalid Selection')
                lp = False

    @commands.command(aliases=['ww'])
    @commands.has_role(movierole)
    async def whoswatching(self, ctx, *, choice):
        watching = []
        movtemp = None
        for film in movies:
            if choice.lower() in movies[film]['title'].lower():
                movtemp = film
                for user in movies[movtemp]['users']:
                    watching.append(f'**{movies[movtemp]["users"][user]}** \n')
        if watching:
            embed = discord.Embed(title=f'Users watching **{movtemp}**:', description=f'\n'.join(user for user in watching))     # embed every user
            await ctx.channel.send(embed=embed)
        elif not watching and movtemp:
            embed = discord.Embed(title=f'No users watching **{movtemp}**')
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send(f'Invalid Selection')

    @commands.command(aliases=['nm'])
    @commands.has_role(movierole)
    async def newmovie(self, ctx):
        await ctx.channel.send("Alright! What's the title of the movie?")
        title = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await ctx.channel.send('''What date/time will the movie be on? (EST)\n
        Format: YYYY-MM-DD HH:MM''')
        while True:
            mdtemp = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            try:
                moviedate = datetime.datetime.fromisoformat(str(mdtemp.content))        # check if date/time is formatted properly
                print(f'movietime is {moviedate}')
                break
            except Exception as e:
                await ctx.channel.send(f'''ERR: Bad Date Format! \n{e}\n
                Format must be: YYYY-MM-DD HH:MM''')

        await ctx.channel.send(f'Okay! You want to watch **{title.content}** on **{mdtemp.content}**? (Y/n)')
        ans = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if ans.content.lower() == 'y' or ans.content.lower() == 'yes':
            execdate = scheduler.add_job(self.moviescheduler, 'date', run_date=moviedate, args=[ctx, title.content])     # add movie data to scheduler
            movies[title.content] = {
                'title': title.content,
                'date': moviedate,
                'users': {},
                'scheduler': execdate
            }
            print(f'Added {movies[title.content]}')
            await ctx.channel.send('\nMovie added! Type `!watch` to sign up.')
        else:
            await ctx.channel.send('Canceled operations')

    @commands.command(aliases=['rmv'])
    @commands.has_permissions(administrator=True)
    async def removemovie(self, ctx, *, choice):
        delete = None
        for film in movies:
            if choice.lower() in movies[film]['title'].lower():
                await ctx.channel.send(f'Removed **{film}**')
                delete = film
                break
        if delete:
            del movies[delete]
        else:
            await ctx.channel.send(f'Invalid Selection')


async def setup(bot):
    await bot.add_cog(Movie(bot))
