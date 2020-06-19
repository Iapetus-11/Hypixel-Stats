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

    @commands.command(name="guildmembers", aliases=["gmembers", "guildplayers", "gms", "members"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def guild_members(self, ctx, *, guild_name):
        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        await ctx.send(guild_id)
        g = await self.cache.get_guild(guild_id)
        await ctx.send(g)
        members = g.MEMBERS

        if len(members) > 1024:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(g.NAME)}** has too many members to show! :cry:"))
            return

        async with ctx.typing():
            names = [await self.cache.get_player_name(uuid) for uuid in members]

            chonks = [names[i:i + 10] for i in range(0, len(names), 10)]  # groups of 10 of the usernames

        try:
            stop = False
            page = 0
            max_pages = ceil(len(chonks) / 3)

            while True:
                page += 1

                if not stop and len(chonks) > 3:
                    embed = discord.Embed(color=self.bot.cc,
                                          title=f"Members of **{discord.utils.escape_markdown(g.NAME)}** ({len(members)} total!)",
                                          description="Type ``more`` for more!")
                else:
                    embed = discord.Embed(color=self.bot.cc,
                                          title=f"Members of **{discord.utils.escape_markdown(g.NAME)}** ({len(members)} total!)")

                embed.set_footer(text=f"[Page {page}/{max_pages}]")

                for i in range(0, 3, 1):
                    try:
                        embed.add_field(name="\uFEFF",
                                        value=discord.utils.escape_markdown("\n\n".join(chonks.pop(0))))
                    except IndexError:
                        pass

                await ctx.send(embed=embed)

                if stop or len(members) < 31:
                    return

                if len(chonks) - 3 < 1:
                    stop = True

                def check(m):
                    return m.author.id == ctx.author.id and m.content == "more"

                await self.bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
            pass


def setup(bot):
    bot.add_cog(Guild(bot))
