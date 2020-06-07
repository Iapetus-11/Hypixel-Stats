from discord.ext import commands
import discord


class Friends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="friendsof", aliases=["getfriends", "getuserfriends", "friends"])
    async def friends_of(self, ctx, gamertag: str):
        pass


def setup(bot):
    bot.add_cog(Friends(bot))
