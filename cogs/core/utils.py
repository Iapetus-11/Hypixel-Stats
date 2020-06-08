from discord.ext import commands
import discord


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, location, message):
        await location.send(embed=discord.Embed(color=self.bot.cc, description=message))


def setup(bot):
    bot.add_cog(Utils(bot))
