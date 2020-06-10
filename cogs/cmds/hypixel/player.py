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
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Last Online", value=f"{last_online}")
        embed.add_field(name="XP", value=f"{p.EXP}", inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Level", value=f"{await self.cache.hypixel.calcPlayerLevel(p.EXP)}", inline=True)
        embed.add_field(name="Achievements", value=f"{len(p.ONE_TIME_ACHIEVEMENTS)}", inline=False)
        embed.add_field(name="Guild", value=f"{player_guild}", inline=False)

        await ctx.send(embed=embed)

    @commands.gruop(name="playerstats", aliases=["pstats", "ps"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_stats(self, ctx, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        await ctx.send(embed=discord.Embed(color=self.bot.cc, description=f"Available stats for this player (send which one you want): ``{', '.join(list(p.STATS))}``"))

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            stat = await self.bot.wait_for("message", check=check, timeout=20)
            stat = stat.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description=self.bot.TIMEOUT_MESSAGE))
            return

        if stat not in [s.lower() for s in list(p.STATS)]:
            await ctx.send(f"{discord.utils.escape_markdown(p.DISPLAY_NAME)} doesn't have stats for that!")
            return

        embed = discord.Embed(color=self.bot.cc)

        if stat == "bedwars":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Bedwars Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            bedwars = p.STATS.get("Bedwars")

            embed.add_field(name="XP", value=bedwars["Experience"])
            embed.add_field(name="Coins", value=bedwars["coins"])
            embed.add_field(name="Total Games",
                            value=sum({k: v for k, v in bedwars.items() if "games_played" in k}.values()))

            embed.add_field(name="Losses", value=bedwars["beds_lost_bedwars"])
            embed.add_field(name="Wins", value=bedwars["wins_bedwars"])
            embed.add_field(name="Winstreak", value=bedwars["winstreak"])

            kills = bedwars["kills_bedwars"]
            deaths = bedwars["deaths_bedwars"]
            embed.add_field(name="Kills", value=kills)
            embed.add_field(name="Deaths", value=deaths)
            embed.add_field(name="KDR", value=round(kills / deaths, 2))

            embed.add_field(name="Beds Broken", value=bedwars.get("beds_broken_bedwars"))
            await ctx.send(embed=embed)
        elif stat == "arcade":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Arcade Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            arcade = p.STATS.get("Arcade")

            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            embed.add_field(name="Total Coins", value=arcade["coins"], inline=False)
            embed.add_field(name="\uFEFF", value=f"\uFEFF")

            embed.add_field(name="Coins This Month", value=arcade["monthly_coins_a"] + arcade["monthly_coins_b"],
                            inline=True)
            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            embed.add_field(name="Coins This Week", value=arcade["weekly_coins_a"] + arcade["weekly_coins_b"],
                            inline=True)
            await ctx.send(embed=embed)
        elif stat == "tntgames":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s TNT Games Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            tntgames = p.STATS.get("TNTGames")

            embed.add_field(name="Coins", value=tntgames["coins"])
            embed.add_field(name="Wins", value=tntgames["wins"])
            embed.add_field(name="Winstreak", value=tntgames["winstreak"])

            kills = sum({k: v for k, v in tntgames.items() if "kills" in k}.values())
            deaths = sum({k: v for k, v in tntgames.items() if "deaths" in k}.values())
            embed.add_field(name="Kills", value=kills)
            embed.add_field(name="Deaths", value=deaths)
            embed.add_field(name="KDR", value=round(kills/deaths, 2))

            embed.add_field(name="TNT Run Record", value=tntgames["record_tntrun"])
            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            embed.add_field(name="PvP Run Record", value=tntgames["record_pvprun"])
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

        g = await self.cache.get_guild(player_guild)

        author = f"{discord.utils.escape_markdown(player)}'s Guild ({discord.utils.escape_markdown(g.NAME)})"

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


def setup(bot):
    bot.add_cog(Player(bot))
