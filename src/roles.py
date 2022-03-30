# import dependencies
import discord
from discord.ext import commands
import asyncio
import json

msg = None
reactions = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
clist = []
cdict = {}
userreact = None
# client = discord.client


with open("./config/colours.json") as f:
    colours = json.load(f)


class Roles(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # await member.send("Welcome, fren :D")
        role = discord.utils.get(member.guild.roles, name="new member")
        await member.add_roles(role)

    # @commands.command(aliases=['color', 'colors', 'colours'])
    # async def colour(self, ctx):
    #     print('printing colour message')
    #     # channel = ctx.channel
    #     await ctx.message.delete()
    #     global msg
    #     global clist
    #     global userreact
    #     userreact = ctx.author
    #     print(userreact)
    #     clist.clear()
    #     msg = await ctx.channel.send('React to me to choose your colour!')
    #     for colour in colours:
    #         await msg.add_reaction(colour[0])       # react with all the colours in our dict
    #         clist.append(colours[colour])
    #     await asyncio.sleep(10)
    #     await msg.delete()
    #     try:
    #         await msg.delete()
    #     except discord.errors.NotFound:
    #         print('already deleted')

    @commands.command(aliases=['color', 'colors', 'colours'])
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
        # print(cdict)
        await asyncio.sleep(10)
        await cdict[ctx.author.id].delete()

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     global msg
    #     role = None
    #     if user.bot or user != userreact:
    #         return
    #     if reaction.emoji in colours:
    #         role = discord.utils.get(user.guild.roles, name=colours[reaction.emoji])
    #     # channel = reaction.channel
    #     if reaction.message == msg and role:
    #         for userrole in user.roles:
    #             if userrole.name in clist:
    #                 await user.remove_roles(userrole)
    #                 print('remove_role success', userrole)
    #         await user.add_roles(role)
    #         print('add_role success', role)
    #         await asyncio.sleep(1)
    #         if msg is not None:
    #             await msg.delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        role = None
        if user.bot or user.id not in cdict.keys():
            return
        if reaction.emoji in colours:
            role = discord.utils.get(user.guild.roles, name=colours[reaction.emoji])
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


    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        global msg
        role = None
        if reaction.emoji in colours:
            role = discord.utils.get(user.guild.roles, name=colours[reaction.emoji])
        if user.bot:
            return
        if reaction.message == msg and role:
            await user.remove_roles(role)
            print('remove_role success', role)

    @colour.error                         # stop the bot from throwing an error when it tries to delete a message twice
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            print('already deleted :)')


def setup(bot):
    bot.add_cog(Roles(bot))
