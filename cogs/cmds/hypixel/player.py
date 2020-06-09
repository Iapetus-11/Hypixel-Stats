import aiopypixel
import base64
import discord
from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.group(name="player", aliases=["profile", "pp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player(self, ctx, player):
        p = await self.cache.get_player(player)
        embed = discord.Embed(color=self.bot.cc)
        player_pfp = base64.decodeb64(await self.cache.get_player_pfp(p.UUID))
        embed.set_author(f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Profile")
        embed.add_field(name="XP", value=f"``{p.EXP}``")
        embed.add_field("Achievements", value=f"``{len(p.ONE_TIME_ACHIEVEMENTS)}``")
        embed.add_field("Guild", value=f"``{p.GUILD}``")
        embed.add_field()

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
