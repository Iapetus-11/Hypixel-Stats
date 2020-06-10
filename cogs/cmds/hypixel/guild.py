import discord
from discord.ext import commands


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.command(name="guild", aliases=["g"])
    async def guild(self, ctx, guild_name):
        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        g = await self.cache.get_guild(guild_id)

        desc = g.DESCRIPTION
        member_count = len(g.MEMBERS)
        coins = g.COINS
        xp = g.EXP
        tag = g.TAG  # idk
        created = arrow.Arrow.fromtimestamp(g.CREATED / 1000).humanize()

        embed = discord.Embed(color=self.bot.cc, description=desc)
        embed.set_author(name=g.NAME, inline=True)
        embed.add_field(name="Members", value=member_count, inline=True)
        embed.add_field(name="Coins", value=coins, inline=True)
        embed.add_field(name="XP", value=xp, inline=True)
        embed.add_field(name="Tag", value=tag, inline=True)
        embed.add_field(name="Created", value=created, inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guild(bot))
