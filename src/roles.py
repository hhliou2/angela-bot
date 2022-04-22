# import dependencies
import discord
from discord.ext import commands
import asyncio
import json

msg = None
reactions = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
ndict = {}
clist = []
userreact = None
timeout = 30    # time in seconds to wait before deleting message
# client = discord.client


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

    @commands.command(aliases=['reloadcolors'])
    @commands.has_permissions(administrator=True)
    async def reloadcolours(self, ctx):
        await ctx.message.delete()
        global clist
        clist.clear()
        with open("./config/colours.txt") as f:
            roleid = f.readline()
            while roleid:
                clist.append(int(roleid.strip()))
                roleid = f.readline()
        print(clist)


    @commands.command(aliases=['buildcolors'])      # TODO: save built colours to file
    @commands.has_permissions(administrator=True)
    async def buildcolours(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        global clist
        clist.clear()
        clist = [role.id for role in guild.roles if str(role).startswith('[clr]')]     # make sure only colour roles are included
        if clist:
            instructions = discord.Embed(title='To set your colour:', description=f'''
            Type "!setcolour" followed by the name of the colour you want. Colours are not case-sensitive. \n
            Example: !setcolour Gamer Girl''')
            await ctx.send(embed=instructions)
            full_roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in clist]
            embed = discord.Embed(title='Colours:', description=f'\n'.join([role.mention for role in full_roles]))     # put colours into embed message
            await ctx.send(embed=embed)
            with open("./config/colours.txt", mode='w+') as outfile:
                for role in clist:
                    outfile.write('%s\n' % role)
            print('Colours built successfully!')
            print(clist)
        else:
            print('ERROR: No suitable roles. Colour roles must start with "clr"')

    @commands.command(aliases=['setcolor'])
    async def setcolour(self, ctx, *, clr):
        newcolour = None
        if clist and clr:
            full_roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in clist]
            for role in full_roles:
                if clr.lower() in str(role.name).lower():
                    newcolour = role
                    break
        if newcolour:
            for role in ctx.author.roles:
                if str(role).startswith('[clr]'):
                    await ctx.author.remove_roles(role)
                    print(f'remove_role success! {role} {ctx.author.name}')
            await ctx.author.add_roles(newcolour)
            print(f'add_role success! {newcolour} {ctx.author.name}')
        else:
            print(f"ERROR: Colour {clr} doesn't exist")
        await ctx.message.delete()

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
        embed = discord.Embed(title='React to me to choose your NSFW role!', description=f'''
        🥉 = SFW \n
        🥈 = NSFW \n
        🥇 = NSFW + Rule34
        ''')
        ndict[ctx.author.id] = await ctx.channel.send(embed=embed)
        for i in nsfw:
            await ndict[ctx.author.id].add_reaction(i[0])
        await asyncio.sleep(timeout)
        if ctx.author.id in ndict.keys():
            await ndict[ctx.author.id].delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or user.id not in ndict.keys():
            return
        if reaction.emoji in nsfw and reaction.message == ndict[user.id]:
            await self.nsfw_react(reaction, user)

    async def nsfw_react(self, reaction, user):
        role = None
        if reaction.emoji in nsfw:
            role = discord.utils.get(user.guild.roles, name=nsfw[reaction.emoji])
        if reaction.message == ndict[user.id]:
            for userrole in user.roles:
                if userrole.name in nsfw.values():
                    await user.remove_roles(userrole)
                    print(f'remove_role success {userrole}, {user.name}')
            await user.add_roles(role)
            print(f'add_role success {role}, {user.name}')
            await asyncio.sleep(1)
            if user.id in ndict.keys():
                await ndict[user.id].delete()
                ndict.pop(user.id)


def setup(bot):
    bot.add_cog(Roles(bot))
