import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.command(name="watchdog", aliases=["watchdogstats", "bans"])
    async def watchdog(self, ctx):
        pass


def setup(bot):
    bot.add_cog(General(bot))
