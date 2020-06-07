from discord.ext import commands
import discord


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.db.drop_prefix(guild.id)


def setup(bot):
    bot.add_cog(Events(bot))
