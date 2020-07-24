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

        self.colors = {
            "red": discord.Color.red(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.gold(),
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "purple": discord.Color.purple(),
            "blurple": discord.Color.blurple(),
            "grey": discord.Color.greyple(),
            "magenta": discord.Color.magenta(),
            "teal": discord.Color.teal()
        }

    @commands.group(name="config", aliases=["settings", "set", "conf"])
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=await self.bot.cc(ctx.author.id))
            embed.set_author(name="Bot Configuration", icon_url=str(self.bot.user.avatar_url_as(static_format="png")))
            embed.add_field(name="Prefix", value=f"`{ctx.prefix}config prefix <prefix>`")
            embed.add_field(name="Embed Color", value=f"`{ctx.prefix}config color <color>`")

            embed.add_field(name="\uFEFF", value="\uFEFF", inline=False)

            embed.add_field(name="Disable Channel", value=f"`{ctx.prefix}config disable <channel>`")
            embed.add_field(name="Enable Channel", value=f"`{ctx.prefix}config enable <channel>`")
            await ctx.send(embed=embed)

    @config.command(name="prefix", aliases=["pp", "p", "commandprefix"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config_prefix(self, ctx, prefix: str = None):
        if ctx.guild is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description="This command can't be used in dms or group chats."))
            return

        if prefix is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description=f"The current prefix is: ``{await self.db.get_prefix(ctx.guild.id)}``"))
        else:
            for car in prefix:
                if car.lower() not in self.allowed_chars:
                    await ctx.send(
                        embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                            description="That prefix contains invalid characters!"))
                    return
            await self.db.set_prefix(ctx.guild.id, prefix[:10])
            s = ""
            if prefix[:10] != prefix:
                s = "\n*Also, your prefix was too long, so we shortened it!*"
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description=f"Changed the prefix from **``{ctx.prefix}``** to **``{prefix}``**{s}"))

    @config.command(name="color", aliases=["changecolor"])
    async def config_color(self, ctx, color: str = None):
        if not await self.db.is_premium(ctx.author.id):
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description="This config option is for [premium](https://donatebot.io/checkout/718983582898585602) users only."))
            return
        if color is None:
            embed = discord.Embed(color=await self.bot.cc(ctx.author.id), title=f"The current embed color is:")
            # embed.set_image(url=f"http://singlecolorimage.com/get/{hex(await self.db.get_color(ctx.author.id)).replace('0x', '')}/200x75")
            embed.set_image(
                url=f"http://singlecolorimage.com/get/{hex(await self.db.get_color(ctx.author.id)).replace('0x', '')}/200x75")
            await ctx.send(embed=embed)
            return
        else:
            if color.lower() in list(self.colors):
                await self.db.set_color(ctx.author.id, self.colors.get(color.lower()).value)
                embed = discord.Embed(color=await self.bot.cc(ctx.author.id),
                                      title=f"The new embed color is:")
                embed.set_image(
                    url=f"http://singlecolorimage.com/get/{hex(self.colors.get(color.lower()).value).replace('0x', '')}/200x75")
                await ctx.send(embed=embed)
            else:
                valid_colors_text = "`" + "`, `".join(list(self.colors)) + "`"
                await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                                   description=f"\"{discord.utils.escape_markdown(color)}\""
                                                               f"is not an allowed/valid color.\n\n Valid colors: {valid_colors_text}"))

    @config.command(name="disable_channel",
                    aliases=["disablechannel", "disable", "enable", "reenable", "reenablechannel"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config_disable_channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        is_disabled = await self.db.is_channel_disabled(channel.id)

        if is_disabled:
            await self.db.undisable_channel(channel.id)
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description=f"Re-enabled commands in {channel.mention}."))
        else:
            await self.db.disable_channel(channel.id)
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id),
                                               description=f"Disabled commands in {channel.mention}."))


def setup(bot):
    bot.add_cog(Settings(bot))
