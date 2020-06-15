import arrow
import discord
from discord.ext import commands
from math import ceil


class Guild(commands.Cog):

    def __init__(self, bot: commands.Bot):
        """basic initalization of the guild cog"""

        self.bot = bot
        self.cache = self.bot.get_cog("Cache")

    @commands.command(name="guild", aliases=["g"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def guild(self, ctx, *, guild_name):
        await ctx.trigger_typing()

        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        g = await self.cache.get_guild(guild_id)

        author = discord.utils.escape_markdown(g.NAME)

        desc = g.DESCRIPTION
        if desc is None:
            embed = discord.Embed(color=self.bot.cc)
        else:
            length = len(author) + 2
            length = length if length > 30 else 30
            embed = discord.Embed(color=self.bot.cc,
                                  description='\n'.join(
                                      desc[i:i + length] for i in
                                      range(0, len(desc), length)))

        member_count = len(g.MEMBERS)
        coins = g.COINS
        xp = g.EXP
        tag = g.TAG
        created = arrow.Arrow.fromtimestamp(g.CREATED / 1000).humanize()

        embed.set_author(name=author)

        embed.add_field(name="Members", value=member_count, inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Tag", value=tag, inline=True)

        embed.add_field(name="Coins", value=coins, inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="XP", value=xp, inline=True)

        embed.add_field(name="Created", value=created, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="guildmembers",
                      aliases=["gmembers", "guildplayers", "gms", "members"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def guild_members(self, ctx, *, guild_name):
        await ctx.trigger_typing()

        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        g = await self.cache.get_guild(guild_id)
        members = g.MEMBERS

        embed = discord.Embed(color=self.bot.cc,
                              title=f"Members of **{discord.utils.escape_markdown(g.NAME)}** ({len(members)} total!)")

        body = ""
        count = 0
        embed_count = 0
        for member in members:
            member = member["uuid"]
            try:
                name = await self.cache.get_player_name(member)
            except aiopypixel.exceptions.exceptions.InvalidPlayerError:
                name = "Unknown Member"
            body += f"{discord.utils.escape_markdown(name)}\n\n"
            if count > ceil(len(members) / 2) if len(members) < 20 else 20:
                embed.add_field(name="\uFEFF", value=body)
                embed_count += 1
                count = 0
                body = ""
            count += 1
        if count > 0:
            embed.add_field(name="\uFEFF", value=body)
            embed_count += 1

        if len(embed) > 5095 or embed_count > 35:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"{discord.utils.escape_markdown(g.NAME)} has too many members to show!"))
            return

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guild(bot))
