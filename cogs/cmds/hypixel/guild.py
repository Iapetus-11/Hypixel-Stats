import arrow
import asyncio
import discord
from discord.ext import commands
from math import ceil


class Guild(commands.Cog):

    def __init__(self, bot: commands.Bot):
        """basic initalization of the guild cog"""

        self.bot = bot

        self.cache = self.bot.get_cog("Cache")
        self.db = self.bot.get_cog("Database")

    @commands.command(name="guild", aliases=["g"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def guild(self, ctx, *, guild_name):
        await ctx.trigger_typing()

        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        g = await self.cache.get_guild(guild_id)

        author = g.NAME

        desc = g.DESCRIPTION
        if desc is None:
            embed = discord.Embed(color=await self.bot.cc(),
                                  url=f"https://hypixel.net/guilds/{g.NAME}".replace(" ", "%20"))
        else:
            length = len(author) + 2
            length = length if length > 30 else 30
            embed = discord.Embed(color=await self.bot.cc(),
                                  url=f"https://hypixel.net/guilds/{g.NAME}".replace(" ", "%20"),
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

        embed.set_footer(text="Made by Iapetus11 & TrustedMercury")

        await ctx.send(embed=embed)

    async def edit_show_online(self, msg, prev_embed, chonks):
        embed = prev_embed.copy()
        embed.clear_fields()

        for i in range(0, 3, 1):
            try:
                body = "\uFEFF"
                users = chonks.pop(0)
                for user in users:
                    body += f"{await self.get_user_status(user)} {discord.utils.escape_markdown(user)}\n\n"
                embed.add_field(name="\uFEFF", value=body)
            except IndexError:
                pass

        await msg.edit(embed=embed)

    @commands.command(name="guildmembers", aliases=["gmembers", "guildplayers", "gms", "members"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def guild_members(self, ctx, *, guild_name):
        guild_id = await self.cache.get_guild_id_from_name(guild_name)
        g = await self.cache.get_guild(guild_id)

        guild_members = g.MEMBERS

        if not guild_members:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"**{discord.utils.escape_markdown(g.NAME)}** doesn't have any members! :cry:"))
            return

        if len(guild_members) > 1024:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"**{discord.utils.escape_markdown(g.NAME)}** has too many members to show! :cry:"))
            return

        embed = discord.Embed(color=await self.bot.cc())
        embed.set_author(name=f"Members of {g.NAME} ({len(guild_members)} total!)")

        premium = False if ctx.guild is None else await self.db.is_premium(ctx.guild.id)

        async with ctx.typing():
            names = []
            for m_uuid in [uuid for member.get("uuid") in guild_members]:
                try:
                    names.append(await self.cache.get_player_name(m_uuid))
                except Exception:
                    names.append("[Invalid User]")

            chonks = [names[i:i + 7] for i in range(0, len(names), 7)]  # groups of 10 of the usernames, 7 good 2

        try:
            stop = False
            page = 0
            max_pages = ceil(len(chonks) / 3)

            while True:
                page += 1

                if not stop and len(chonks) > 3:
                    embed = discord.Embed(color=await self.bot.cc(), description="Type ``more`` for more!")
                else:
                    embed = discord.Embed(color=await self.bot.cc())

                embed.set_author(name=f"Members of {g.NAME} ({len(guild_members)} total!)")
                embed.set_footer(text=f"[Page {page}/{max_pages}]")

                smol_chonks = []

                for i in range(0, 3, 1):
                    try:
                        smol_chonk = chonks.pop(0)
                        smol_chonks.append(smol_chonk)
                        embed.add_field(name="\uFEFF",
                                        value=discord.utils.escape_markdown("\n\n".join(smol_chonk)))
                    except IndexError:
                        pass

                sent = await ctx.send(embed=embed)

                if premium:
                    self.bot.loop.create_task(self.edit_show_online(sent, embed, smol_chonks))

                if stop or len(guild_members) <= 21:
                    return

                if len(chonks) - 3 < 1:
                    stop = True

                def check(m):
                    return m.content in ["more", "next", "nextpage", "showmore"]

                await self.bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            pass


def setup(bot):
    bot.add_cog(Guild(bot))
