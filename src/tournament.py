import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import datetime
from discord.ext import commands

scheduler = AsyncIOScheduler()
scheduler.start()
tournament = {}
tournamentrole = 'Clubhouse Member'


class Tournament(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    async def tournamentscheduler(self, ctx, selection):
        print(f'Begin scheduled tournament {selection}')
        if selection not in tournament:
            print(f'WARN: Tournament {selection} in scheduler no longer exists!')
            return
        else:
            tomention = []
            for user in tournament[selection]['users'].keys():
                tomention.append(f'<@{user}>\n')
            if tomention:
                await ctx.channel.send(f"It's time to rrrrummmblllleeeee, come on and play some {selection} with:")
                users = '\n'.join(user for user in tomention)
                await ctx.channel.send(f'\n{users}')
                del tournament[selection]
            else:
                print(f'Error: tomention is empty {tomention}')

    @commands.command(aliases=[])
    @commands.has_role(tournamentrole)
    async def tournaments(self, ctx):
        tlist = []
        if tournament:
            for event in tournament:
                tlist.append(f'**{tournament[event]["title"]}** at **{tournament[event]["date"]}**')              # Add all tournament to our list
            embed = discord.Embed(title='**Available Tournaments:**', description=f'\n'.join(event for event in tlist))      # Send movie list
            await ctx.channel.send(embed=embed)
            embed = discord.Embed(title='**To sign up to play:**', description=f'Type `!enter <game>`')
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title='**No Tournaments Available!**', description=f'To add a tournament, type `!enter`')
            await ctx.channel.send(embed=embed)
            
    @commands.command(aliases=[])
    @commands.has_role(tournamentrole)
    async def whosplaying(self, ctx, *, choice):
        playing = []
        trntemp = None
        for event in tournament:
            if choice.lower() in tournament[event]['title'].lower():
                trntemp = event
                for user in tournament[trntemp]['users']:
                    playing.append(f'**{tournament[trntemp]["users"][user]}** \n')
        if playing:
            embed = discord.Embed(title=f'Users playing **{trntemp}**:', description=f'\n'.join(user for user in playing))  # embed every user
            await ctx.channel.send(embed=embed)
        elif not playing and trntemp:
            embed = discord.Embed(title=f'No users playing **{trntemp}**')
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send(f'Invalid Selection')

    @commands.command(aliases=['nt'])
    @commands.has_role(tournamentrole)
    async def newtournament(self, ctx):
        await ctx.channel.send("Alright! What game are you playing?")
        title = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if title.content.lower() == 'cancel':
            return
        await ctx.channel.send('''What date/time will the tournament be at? (EST)\n
                Format: YYYY-MM-DD HH:MM''')
        while True:
            tdtemp = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if tdtemp.content.lower() == 'cancel':
                return
            try:
                tournamentdate = datetime.datetime.fromisoformat(str(tdtemp.content))  # check if date/time is formatted properly
                print(f'tournamentdate is {tournamentdate}')
                break
            except Exception as e:
                await ctx.channel.send(f'''ERR: Bad Date Format! \n{e}\n
                        Format must be: YYYY-MM-DD HH:MM''')

        await ctx.channel.send(f'Okay! You want to play **{title.content}** on **{tdtemp.content}**? (Y/n)')
        ans = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if ans.content.lower() == 'y' or ans.content.lower() == 'yes':
            execdate = scheduler.add_job(self.tournamentscheduler, 'date', run_date=tournamentdate, args=[ctx, title.content])  # add data to scheduler
            tournament[title.content] = {
                'title': title.content,
                'date': tournamentdate,
                'users': {},
                'scheduler': execdate
            }
            print(f'Added {tournament[title.content]}')
            await ctx.channel.send('\nTournament added! Type `!enter <game>` to sign up.')
        else:
            await ctx.channel.send('Canceled operations')

    @commands.command(aliases=[])
    @commands.has_role(tournamentrole)
    async def enter(self, ctx, *, signup):
        lp = True
        trntemp = None
        while lp:
            # signup = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            for event in tournament:
                if str(signup).lower() in tournament[event]['title'].lower():  # Check if movie exists
                    trntemp = event
                    if ctx.author.id in tournament[trntemp]['users']:
                        await ctx.channel.send('''You are already in this tournament. \n
                                Would you like to be taken off the list? (Y/N)''')
                        ans = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if ans.content.lower() == 'y' or ans.content.lower() == 'yes':
                            tournament[trntemp]['users'].pop(ctx.author.id)  # Remove user from tournament list
                            await ctx.channel.send('Removed from tournament')
                            print(f'{ctx.author.name} removed from {trntemp}')
                        lp = False
                        break
    
                    else:
                        tournament[trntemp]['users'][ctx.author.id] = ctx.author.name  # Add user to tournament list
                        print(f'{ctx.author.name} added to {trntemp}')
                        await ctx.channel.send(f'Added you to the list for **{trntemp}**')
                        lp = False
                        break
    
            if str(signup) == 'cancel':
                await ctx.channel.send('Operation Canceled')
                lp = False
            elif not trntemp:
                await ctx.channel.send('Invalid Selection')
                lp = False

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removetournament(self, ctx, *, choice):
        delete = None
        for event in tournament:
            if choice.lower() in tournament[event]['title'].lower():
                await ctx.channel.send(f'Removed **{event}**')
                delete = event
                break
        if delete:
            del tournament[delete]
        else:
            await ctx.channel.send(f'Invalid Selection')

async def setup(bot):
    await bot.add_cog(Tournament(bot))