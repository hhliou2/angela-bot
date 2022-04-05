# import dependencies
import discord
from discord.ext import commands
import asyncio
import json

msg = None
reactions = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
ndict = {}
cdict = {}
userreact = None
# client = discord.client


with open("./config/colours.json") as f:
    colours = json.load(f)

with open("./config/nsfw.json") as f:
    nsfw = json.load(f)


class Roles(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="new member")
        await member.add_roles(role)

    @commands.command(aliases=['color', 'colors', 'colours'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def colour(self, ctx):
        print('printing colour message')
        await ctx.message.delete()
        global msg
        global cdict
        while ctx.author.id in cdict.keys():
            print(f'user {ctx.author} already has request opened')
            cdict.pop(ctx.author.id)
        cdict[ctx.author.id] = await ctx.channel.send('React to me to choose your colour!')
        for colour in colours:
            await cdict[ctx.author.id].add_reaction(colour[0])
        await asyncio.sleep(60)
        await cdict[ctx.author.id].delete()

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def nsfw(self, ctx):
        print('printing nsfw message')
        await ctx.message.delete()
        global msg
        global ndict
        while ctx.author.id in ndict.keys():
            print(f'user {ctx.author} already has request opened')
            ndict.pop(ctx.author.id)
        ndict[ctx.author.id] = await ctx.channel.send('React to me to choose your NSFW role!')
        for i in nsfw:
            await ndict[ctx.author.id].add_reaction(i[0])
        await asyncio.sleep(60)
        await cdict[ctx.author.id].delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or user.id not in cdict.keys() and user.id not in ndict.keys():
            return
        if reaction.emoji in colours and reaction.message == cdict[user.id]:
            await self.colour_react(reaction, user)
        if reaction.emoji in nsfw and reaction.message == ndict[user.id]:
            await self.nsfw_react(reaction, user)

    async def colour_react(self, reaction, user):
        role = None
        if reaction.emoji in colours:
            role = discord.utils.get(user.guild.roles, name=colours[reaction.emoji])    # get role name from reaction
        if reaction.message == cdict[user.id]:
            for userrole in user.roles:
                if userrole.name in colours.values():
                    await user.remove_roles(userrole)
                    print(f'remove_role success {userrole}')
            await user.add_roles(role)
            print(f'add_role success {role}')
            await asyncio.sleep(1)
            if user.id in cdict.keys():
                await cdict[user.id].delete()
                cdict.pop(user.id)

    async def nsfw_react(self, reaction, user):
        role = None
        if reaction.emoji in nsfw:
            role = discord.utils.get(user.guild.roles, name=nsfw[reaction.emoji])
        if reaction.message == ndict[user.id]:
            for userrole in user.roles:
                if userrole.name in nsfw.values():
                    await user.remove_roles(userrole)
                    print(f'remove_role success {userrole}')
            await user.add_roles(role)
            print(f'add_role success {role}')
            await asyncio.sleep(1)
            if user.id in ndict.keys():
                await ndict[user.id].delete()
                ndict.pop(user.id)

    @colour.error                         # stop the bot from throwing an error when it tries to delete a message twice
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            print('already deleted :)')

    @nsfw.error                           # ditto
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            print('already deleted :)')


def setup(bot):
    bot.add_cog(Roles(bot))
