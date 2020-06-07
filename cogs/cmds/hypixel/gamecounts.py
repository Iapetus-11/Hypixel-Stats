from discord.ext import commands
import discord


class GameCounts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gamecount", aliases=["game"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def game_count(self, ctx, game: str):
        pass


def setup(bot):
    bot.add_cog(GameCounts(bot))