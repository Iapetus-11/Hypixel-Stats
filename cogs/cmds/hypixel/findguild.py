from discord.ext import commands
import discord


class FindGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getuserguild", aliases=["userguild"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def get_user_guild(self, ctx, gamertag: str):
        pass

    @commands.command(name="getguild", aliases=["getguildbyname"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def get_guild(self, ctx, guild_name: str):
        pass


def setup(bot):
    bot.add_cog(FindGuild(bot))
