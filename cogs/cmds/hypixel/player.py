import aiopypixel
import arrow
import discord
from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.group(name="player", aliases=["profile", "pp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player(self, ctx, player):
        embed = discord.Embed(color=self.bot.cc)

        p = await self.cache.get_player(player)

        online = f"{self.bot.emojis['offline_status']} offline"
        last_online = arrow.Arrow.fromtimestamp(p.LAST_LOGIN / 1000).humanize()  # I love arrow
        if p.LAST_LOGIN > p.LAST_LOGOUT:
            online = f"{self.bot.emojis['online_status']} online"
            last_online = "now"  # bc this value is obtained from last_login

        player_pfp = await self.cache.get_player_head(p.UUID)

        player_guild = p.GUILD
        if player_guild is None:
            player_guild = "none"
        else:
            player_guild = await self.cache.get_guild_name_from_id(p.GUILD)

        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Profile", icon_url=player_pfp)
        embed.add_field(name="Status", value=online)
        embed.add_field(name="Last Online", value=f"{last_online}")
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="XP", value=f"{p.EXP}", inline=True)
        embed.add_field(name="Achievements", value=f"{len(p.ONE_TIME_ACHIEVEMENTS)}", inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Guild", value=f"{player_guild}", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="friends", aliases=["pf", "pfriends", "playerfriends", "friendsof"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        await ctx.trigger_typing()

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"{discord.utils.escape_markdown(player)} doesn't have any friends! :cry:"))
            return

        embed = discord.Embed(color=self.bot.cc, title=f"``{discord.utils.escape_markdown(player)}``'s friends ({len(player_friends)} total!)")

        body = ""
        count = 0
        embed_count = 0
        for friend in player_friends:
            try:
                name = await self.cache.get_player_name(friend)
            except aiopypixel.exceptions.exceptions.InvalidPlayerError:
                name = "Unknown User"
            body += f"{discord.utils.escape_markdown(name)}\n\n"
            if count > 20:
                embed.add_field(name="\uFEFF", value=body)
                embed_count += 1
                count = 0
                body = ""
            count += 1
        if count > 0:
            embed.add_field(name="\uFEFF", value=body)
            embed_count += 1

        if len(embed) > 5095 or embed_count > 35:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description=f"{discord.utils.escape_markdown(player)} has too many friends to show!"))
            return

        await ctx.send(embed=embed)

    @commands.command(name="playerguild", aliases=["pg", "playerg", "pguild", "guildofplayer"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_guild(self, ctx, player):
        await ctx.trigger_typing()

        player_guild = await self.cache.get_player_guild(player)

        if player_guild is None:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"{discord.utils.escape_markdown(player)} isn't in a guild!"))
            return

        player_guild = await self.cache.get_guild_name_from_id(player_guild)

        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"**{discord.utils.escape_markdown(player)}** is in the guild: {discord.utils.escape_markdown(player_guild)}"))


def setup(bot):
    bot.add_cog(Player(bot))
