import aiopypixel
import arrow
import asyncio
import discord
from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.group(name="player", aliases=["profile", "pp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player(self, ctx, player):
        await ctx.trigger_typing()

        embed = discord.Embed(color=self.bot.cc)

        p = await self.cache.get_player(player)

        online = f"{self.bot.EMOJIS['offline_status']} offline"
        last_online = arrow.Arrow.fromtimestamp(p.LAST_LOGIN / 1000).humanize()  # I love arrow
        if p.LAST_LOGIN > p.LAST_LOGOUT:
            online = f"{self.bot.EMOJIS['online_status']} online"
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
        embed.add_field(name="Level", value=f"{await self.cache.hypixel.calcPlayerLevel(p.EXP)}", inline=True)
        embed.add_field(name="Achievements", value=f"{len(p.ONE_TIME_ACHIEVEMENTS)}", inline=False)
        embed.add_field(name="Guild", value=f"{player_guild}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="playerstats", aliases=["pstats", "ps"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_stats(self, ctx, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"Which game do you want to view stats for? ``{','.join(list(p.STATS))}``"))

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            stat = await self.bot.wait_for("message", check=check, timeout=20)
            stat = stat.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description=self.bot.TIMEOUT_MESSAGE))
            return

        embed = discord.Embed(color=self.bot.cc)
        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Profile",
                         icon_url=await self.cache.get_player_head(p.UUID))

        if stat == "bedwars":
            bedwars = p.STATS.get("Bedwars")
            if bedwars is None:
                await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                                   description=f"**{discord.utils.escape_markdown(player)}** has no Bedwars stats."))
            else:
                embed.add_field(name="XP", value=bedwars["Experience"])
                embed.add_field(name="Coins", value=bedwars["coins"])
                embed.add_field(name="Total Games",
                                value=sum({k: v for k, v in bedwars.items() if "games_played" in k}.values()))

                embed.add_field(name="Losses",
                                value=sum({k: v for k, v in bedwars.items() if "losses_bedwars" in k}.values()))
                embed.add_field(name="Wins",
                                value=sum({k: v for k, v in bedwars.items() if "wins_bedwars" in k}.values()))
                embed.add_field(name="Winstreak", value=bedwars["winstreak"])

                kills = sum({k: v for k, v in bedwars.items() if "kills_bedwars" in k}.values())
                deaths = sum({k: v for k, v in bedwars.items() if "deaths_bedwars" in k}.values())
                embed.add_field(name="Kills", value=kills)
                embed.add_field(name="Deaths", value=kills)
                embed.add_field(name="KDR", value=round(kills / deaths, 2))

                embed.add_field(name="Beds Broken",
                                value=sum({k: v for k, v in bedwars.items() if "beds_broken_bedwars" in k}.values()))
                await ctx.send(embed=embed)

    @commands.command(name="friends", aliases=["pf", "pfriends", "playerfriends", "friendsof"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        await ctx.trigger_typing()

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** doesn't have any friends! :cry:"))
            return

        embed = discord.Embed(color=self.bot.cc,
                              title=f"**{discord.utils.escape_markdown(player)}**'s friends ({len(player_friends)} total!)")

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
                                               description=f"**{discord.utils.escape_markdown(player)}** isn't in a guild!"))
            return

        player_guild = await self.cache.get_guild_name_from_id(player_guild)

        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"**{discord.utils.escape_markdown(player)}** is in the guild: {discord.utils.escape_markdown(player_guild)}"))


def setup(bot):
    bot.add_cog(Player(bot))
