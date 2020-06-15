import arrow
import discord
from discord.ext import commands


class Useful(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.need_more_halp = f"Need more help? Found a bug? Join the official [support server](https://discord.gg/{self.bot.guild_invite_code})!\n\uFEFF"

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
        info_msg.add_field(name="Website", value="None Yet!", inline=True)
        info_msg.add_field(name="Support", value="[Click Here](https://discord.gg/MZ2cXxF)", inline=True)
        info_msg.set_author(name="Hypixel Bot Information",
                            icon_url=str(self.bot.user.avatar_url_as(format="png", size=256)))
        await ctx.send(embed=info_msg)

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

    @commands.group(name="help", aliases=["helpme", "halp", "hlp"])
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.cc,
                title="Hypixel Stats Command Help",
                description=self.need_more_halp
            )

            embed.add_field(name=f"{self.bot.EMOJIS['coin']} Stats", value=f"``{ctx.prefix}help stats``", inline=True)
            embed.add_field(name=f":tools: Other", value=f"``{ctx.prefix}help other``", inline=True)
            embed.add_field(name=f":gear: Config", value=f"``{ctx.prefix}help config``", inline=True)

            embed.set_footer(text=f"\uFEFF\nMade by Iapetus11 & TrustedMercury!")

            await ctx.send(embed=embed)

    @help.command(name="stats", aliases=["info", "statistics"])
    async def help_stats(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f"{self.bot.EMOJIS['coin']} Stats/Info Commands",
            description=self.need_more_halp
        )

        p = ctx.prefix

        player_stats = f"``{p}profile <username>`` *shows some general information for that player*\n\n" \
                       f"``{p}playerstats <username>`` *shows stats for that user for each hypixel game*\n\n" \
                       f"``{p}friends <username>`` *shows that user's friends*\n\n" \
                       f"``{p}playerguild <username>`` *shows that player's guild*\n\uFEFF"
        embed.add_field(name="Player Stats", value=player_stats, inline=False)

        guild_stats = f"``{p}guild <guild name>`` *shows that hypixel guild*\n\n" \
                      f"``{p}members <guild name>`` *shows the members in that guild*\n\uFEFF"
        embed.add_field(name="Guild Stats", value=guild_stats, inline=False)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)

    @help.command(name="other", aliases=["utility"])
    async def help_utility(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f":tools: Other/Utility Commands",
            description=self.need_more_halp
        )

        p = ctx.prefix

        player_stats = f"``{p}stealskin <username>`` *steal another user's skin*\n\n" \
                       f"``{p}nametouuid <username>`` *turns a username into an mc uuid*\n\n" \
                       f"``{p}uuidtoname <mc uuid>`` *turns an mc uuid into a name*\n\n" \
                       f"``{p}colorcodes`` *shows a list of color codes you can use to color text in mc*\n\uFEFF"
        embed.add_field(name="Minecraft Commands", value=player_stats, inline=False)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)

    @help.command(name="config", aliases=["settings"])
    async def help_config(self, ctx):
        embed = discord.Embed(
            color=self.bot.cc,
            title=f":gear: Config Commands",
            description=self.need_more_halp
        )

        p = ctx.prefix

        player_stats = f"``{p}config`` *shows the different settings you can change*\n\n" \
                       f"``{p}config prefix <prefix>`` *changes the prefix of the server you're in*\n\uFEFF"
        embed.add_field(name="General Config", value=player_stats, inline=False)

        embed.set_footer(text=f"Made by Iapetus11 & TrustedMercury!")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Useful(bot))
