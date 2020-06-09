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
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description="<a:ping:692401875001278494> Magnum Dong! \uFEFF ``69.00 ms``"))
            return
        await ctx.send(embed=discord.Embed(color=self.bot.cc, description=f"<a:ping:692401875001278494> {pp}! \uFEFF ``{round(self.bot.latency*1000, 2)} ms``"))



def setup(bot):
    bot.add_cog(Useful(bot))