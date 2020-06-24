import arrow
import discord
from discord.ext import commands


class Useful(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

        self.need_more_halp = f"Need more help? Found a bug? Join the official [support server](https://discord.gg/{self.bot.guild_invite_code})!"

    @commands.command(name="ping", aliases=["pong", "ding", "dong", "shing", "shling", "schlong"])
    async def ping(self, ctx):
        c = ctx.message.content.lower()
        if "pong" in c:
            pp = "Ping"
        elif "ping" in c:
            pp = "Pong"
        elif "ding" in c:
            pp = "Dong"
        elif "dong" in c:
            pp = "Ding"
        elif "shing" in c or "shling" in c:
            pp = "Schlong"
        elif "schlong" in c:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description="Magnum Dong! \uFEFF ``69.00 ms``"))
            return
        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"{pp}! \uFEFF ``{round(self.bot.latency * 1000, 2)} ms``"))

    @commands.command(name="info", aliases=["information"])
    async def information(self, ctx):
        info_msg = discord.Embed(color=self.bot.cc)

        info_msg.add_field(name="Bot Library", value="Discord.py", inline=True)
        info_msg.add_field(name="Command Prefix", value=ctx.prefix, inline=True)
        info_msg.add_field(name="Creators", value="Iapetus11#6821 &\n TrustedMercury#1953", inline=True)

        info_msg.add_field(name="Total Servers", value=str(len(self.bot.guilds)), inline=True)
        info_msg.add_field(name="Shards", value=str(self.bot.shard_count), inline=True)
        info_msg.add_field(name="Total Users", value=str(len(self.bot.users)), inline=True)

        info_msg.add_field(name="Top.gg Page", value="[Click Here](https://top.gg/bot/718523903147900998)", inline=True)
        info_msg.add_field(name="Website", value="[Click Here](https://villagerbot.xyz/hypixel-stats/)", inline=True)
        info_msg.add_field(name="Support", value="[Click Here](https://discord.gg/MZ2cXxF)", inline=True)

        info_msg.set_author(name="Hypixel Stats Information",
                            icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))

        await ctx.send(embed=info_msg)

    @commands.command(name="botstats", aliases=["botstatistics", "bs"])
    async def stats(self, ctx):
        embed = discord.Embed(color=self.bot.cc)

        embed.set_author(name="Hypixel Stats Statistics",
                         icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))

        general = f"Guild Count: ``{len(self.bot.guilds)}``\n" \
                  f"DM Channels ``{len(self.bot.private_channels)}``\n" \
                  f"User Count: ``{len(self.bot.users)}``\n" \
                  f"Shard Count: ``{self.bot.shard_count}``\n" \
                  f"CMD Count: ``{self.bot.cmd_count}``\n" \
                  f"Latency: ``{round(self.bot.latency * 1000, 2)} ms``\n"
        embed.add_field(name="General", value=general)

        caching = f"waiting api requests: ``{self.cache.waiting}``\n" \
                  f""f"valid names & uuids cache: ``{len(self.cache.valid_names_and_uuids)}``\n" \
                  f"name -> uuid cache: ``{len(self.cache.name_uuid_cache)}``\n" \
                  f"uuid -> name cache: ``{len(self.cache.uuid_name_cache)}``\n" \
                  f"skyblock endpoint cache: ``{len(self.cache.skyblock_cache)}``\n" \
                  f"skyblock armor cache: ``{len(self.cache.armor_cache)}``\n"

        caching2 = f"player's friends cache: ``{len(self.cache.player_friends_cache)}``\n" \
                   f"player's guild cache: ``{len(self.cache.player_guild_cache)}``\n" \
                   f"guild id -> guild name cache: ``{len(self.cache.guild_id_name_cache)}``\n" \
                   f"player object cache: ``{len(self.cache.player_object_cache)}``\n" \
                   f"guild object cache: ``{len(self.cache.guild_cache)}``\n"
        embed.add_field(name="Caching", value=caching)
        embed.add_field(name="Caching", value=caching2)

        await ctx.send(embed=embed)

    @commands.command(name="uptime")
    async def get_uptime(self, ctx):
        p = arrow.utcnow()
        diff = (p - self.bot.start_time)
        days = diff.days
        hours = int(diff.seconds / 3600)
        minutes = int(diff.seconds / 60) % 60
        if days == 1:
            dd = "day"
        else:
            dd = "days"
        if hours == 1:
            hh = "hour"
        else:
            hh = "hours"
        if minutes == 1:
            mm = "minute"
        else:
            mm = "minutes"
        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"Bot has been online for {days} {dd}, {hours} {hh}, and {minutes} {mm}!"))

    @commands.command(name="vote", aliases=["votelink"])
    async def vote_link(self, ctx):
        _vote_link = discord.Embed(description="[**Click Here!**](https://top.gg/bot/718523903147900998/vote)",
                                   color=self.bot.cc)
        _vote_link.set_author(name="Vote for Hypixel Stats!",
                              icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))
        await ctx.send(embed=_vote_link)

    @commands.command(name="invite", aliases=["invitelink"])
    async def invite_link(self, ctx):
        inv_l = discord.Embed(description="[**Click Here!**](https://bit.ly/3fAUmPV)", color=self.bot.cc)
        inv_l.set_author(name="Add Hypixel Stats to your server!",
                         icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))
        await ctx.send(embed=inv_l)

    @commands.command(name="discord", aliases=["support"])
    async def discord_link(self, ctx):
        inv_l = discord.Embed(description=f"[**Click Here!**](https://discord.gg/{self.bot.guild_invite_code})",
                              color=self.bot.cc)
        inv_l.set_author(name="Join the support server!",
                         icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))
        await ctx.send(embed=inv_l)

    @commands.group(name="help", aliases=["helpme", "halp", "hlp"])
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.cc,
                title="Hypixel Stats Command Help",
                description=self.need_more_halp + "\n\uFEFF"
            )

            embed.add_field(name=f":bar_chart: Stats", value=f"``{ctx.prefix}help stats``", inline=True)
            embed.add_field(name=f":tools: Other", value=f"``{ctx.prefix}help other``", inline=True)
            embed.add_field(name=f":gear: Config", value=f"``{ctx.prefix}help config``", inline=True)

            embed.set_footer(text=f"\uFEFF\nMade by Iapetus11 & TrustedMercury!")

            await ctx.send(embed=embed)

    @help.command(name="stats", aliases=["info", "statistics", "stat"])
    async def help_stats(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f":bar_chart: Stats/Info Commands",
            description=self.need_more_halp + "\n\uFEFF"
        )

        p = ctx.prefix

        player_stats = f"``{p}profile <username>`` *shows some general information for that player*\n\n" \
                       f"``{p}playerstats`` *lists player stats available*\n\n" \
                       f"``{p}friends <username>`` *shows that user's friends*\n\n" \
                       f"``{p}playerguild <username>`` *shows that player's guild*\n\uFEFF"
        embed.add_field(name="Player", value=player_stats, inline=False)

        guild_stats = f"``{p}guild <guild name>`` *shows that hypixel guild*\n\n" \
                      f"``{p}members <guild name>`` *shows the members in that guild*\n\uFEFF"
        embed.add_field(name="Guild", value=guild_stats, inline=False)

        other_stats = f"``{p}watchdog`` *shows watchdog stats*\n\uFEFF"
        embed.add_field(name="Other", value=other_stats)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)

    @help.command(name="other", aliases=["utility"])
    async def help_utility(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f":tools: Other/Utility Commands",
            description=self.need_more_halp + "\n\uFEFF"
        )

        p = ctx.prefix

        minecraft = f"``{p}stealskin <username>`` *steal another user's skin*\n\n" \
                    f"``{p}nametouuid <username>`` *turns a username into an mc uuid*\n\n" \
                    f"``{p}uuidtoname <mc uuid>`` *turns an mc uuid into a name*\n\n" \
                    f"``{p}colorcodes`` *shows a list of color codes you can use to color text in mc*\n\uFEFF"
        embed.add_field(name="Minecraft", value=minecraft, inline=False)

        other = f"``{p}help`` *shows a help message*\n\n" \
                f"``{p}ping`` *shows the latency between the bot and discord*\n\n" \
                f"``{p}uptime`` *shows the uptime of the bot*\n\n" \
                f"``{p}info`` *shows information about the bot*\n\n" \
                f"``{p}botstats`` *shows some bot statistics*\n\n" \
                f"``{p}invite`` *gives a link to invite the bot*\n\n" \
                f"``{p}vote`` *gives a link to vote for the bot*\n\n" \
                f"``{p}support`` *gives the invite link for the support server*\n\uFEFF"
        embed.add_field(name="Other", value=other, inline=False)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)

    @help.command(name="config", aliases=["settings"])
    async def help_config(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f":gear: Config Commands",
            description=self.need_more_halp + "\n\uFEFF"
        )

        p = ctx.prefix

        server_config = f"``{p}config`` *shows the different settings you can change*\n\n" \
                        f"``{p}config prefix <prefix>`` *changes the prefix of the server you're in*\n\uFEFF"
        embed.add_field(name="Server Config", value=server_config, inline=False)

        user_config = f"`{p}link <mc username>` *links your minecraft and discord accounts*\n\n" \
                      f"`{p}unlink` *unlinks your accounts*\n\uFEFF"
        embed.add_field(name="User Config", value=user_config, inline=False)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Useful(bot))
