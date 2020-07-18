import discord
from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

        self.allowed_chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b",
                              "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
                              "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                              "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-",
                              "_", "+", "=", "[", "]", "{", "}", ";", ":", "|", "/", ".",
                              "?", ">", "<", ",",)

    @commands.group(name="config", aliases=["settings", "set", "conf"])
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=await self.bot.cc())
            embed.set_author(name="Bot Configuration", icon_url=str(self.bot.user.avatar_url_as(static_format="png")))
            embed.add_field(name="Prefix", value=f"``{ctx.prefix}config prefix <prefix>``")
            await ctx.send(embed=embed)

    @config.command(name="prefix", aliases=["pp", "p", "commandprefix"])
    async def config_prefix(self, ctx, prefix: str = None):
        if ctx.guild is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description="This command can't be used in dms or group chats."))
            return

        if prefix is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"The current prefix is: ``{await self.db.get_prefix(ctx.guild.id)}``"))
        else:
            for car in prefix:
                if car.lower() not in self.allowed_chars:
                    await ctx.send(
                        embed=discord.Embed(color=await self.bot.cc(),
                                            description="That prefix contains invalid characters!"))
                    return
            await self.db.set_prefix(ctx.guild.id, prefix[:10])
            s = ""
            if prefix[:10] != prefix:
                s = "\n*Also, your prefix was too long, so we shortened it!*"
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"Changed the prefix from **``{ctx.prefix}``** to **``{prefix}``**{s}"))

    @config.command(name="color", aliases=["changecolor"])
    async def config_color(self, ctx, color: str = None):
        if color is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"The current embed color is {await self.db.get_color(ctx.author.id)}"))


def setup(bot):
    bot.add_cog(Settings(bot))
