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


with open("./config/nsfw.json", encoding='utf-8') as f:
    nsfw = json.load(f)
with open("./config/other_roles.json", encoding='utf-8') as f:
    other_roles = json.load(f)


class Roles(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name=other_roles["new_member_name"])
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

    @commands.command(aliases=['buildcolors'])
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
            embed = discord.Embed(title='Colours:', description=f'\n'.join([role.mention for role in full_roles]))    # put colours into embed message
            await ctx.send(embed=embed)
            with open("./config/colours.txt", mode='w+') as outfile:
                for role in clist:
                    outfile.write('%s\n' % role)
            print('Colours built successfully!')
            print(clist)
        else:
            print('ERROR: No suitable roles. Colour roles must start with "[clr]"')

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
    @commands.has_permissions(administrator=True)
    async def nsfw(self, ctx):
        print('printing nsfw message')
        await ctx.message.delete()

        # Get last message sent to a "Welcome channel"
        welcome_channel = self.bot.get_channel(int(nsfw["channel_id"]))
        if welcome_channel is None:
            await ctx.send('Could not find that channel.')
            return

        message = [message async for message in welcome_channel.history(limit=1)][0]
        if message:
            for emote in nsfw['emotes'].keys():
                await message.add_reaction(emote)
        else:
            await ctx.send('Could not find any message in the specified channel')

        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if payload.emoji.name in nsfw['emotes'] and payload.channel_id == nsfw['channel_id']:
            await self.nsfw_react(payload)

    async def nsfw_react(self, payload):
        role = None
        if payload.emoji.name in nsfw['emotes']:
            role = discord.utils.get(payload.member.guild.roles, name=nsfw['emotes'][payload.emoji.name])
        for userrole in payload.member.roles:
            if userrole.name in nsfw['emotes'].values():
                await payload.member.remove_roles(userrole)
                print(f'remove_role success {userrole}, {payload.member.name}')
        await payload.member.add_roles(role)
        print(f'add_role success {role}, {payload.member.name}')

        welcome_channel = self.bot.get_channel(payload.channel_id)
        message = [message async for message in welcome_channel.history(limit=1)][0]
        for emote in nsfw['emotes'].keys():
            if emote != payload.emoji.name:
                await message.remove_reaction(emote, payload.member)
                await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(Roles(bot))
