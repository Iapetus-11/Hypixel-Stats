import arrow
import discord
from discord.ext import commands


class Useful(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await ctx.send(embed=discord.Embed(color=self.bot.CONFIG["cc"],
                                               description="Magnum Dong! \uFEFF ``69.00 ms``"))
            return
        await ctx.send(embed=discord.Embed(color=self.bot.CONFIG["cc"],
                                           description=f"{pp}! \uFEFF ``{round(self.bot.latency * 1000, 2)} ms``"))

    @commands.command(name="info", aliases=["information"])
    async def information(self, ctx):
        info_msg = discord.Embed(color=self.bot.CONFIG["cc"])
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
        diff = (p - self.bot.self.bot.CONFIG["start_time"])
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
        await ctx.send(embed=discord.Embed(color=self.bot.CONFIG["cc"],
                                           description=f"Bot has been online for {days} {dd}, {hours} {hh}, and {minutes} {mm}!"))


def setup(bot):
    bot.add_cog(Useful(bot))
