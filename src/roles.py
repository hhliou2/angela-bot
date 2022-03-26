# import dependencies

import discord
from discord.ext import commands


class Roles(commands.Cog):
    # Upon instantiation, set local variable bot to bot entity
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send("Welcome, fren :D")
        role = discord.utils.get(member.guild.roles, name="new member")
        await member.add_roles(role)


def setup(bot):
    bot.add_cog(Roles(bot))
