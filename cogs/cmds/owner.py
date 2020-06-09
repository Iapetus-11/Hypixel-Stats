import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, location, message):
        await location.send(embed=discord.Embed(color=self.bot.cc, description=message))

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
        except Exception as e:
            await self.send(ctx, f"Error while unloading extension: {cog}\n``{e}``")
            return
        await self.send(ctx, f"Successfully unloaded cog: " + cog)

    @commands.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await self.send(ctx, f"Error while loading extension: {cog}\n``{e}``")
            return
        await self.send(ctx, "Successfully loaded cog: " + cog)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            self.bot.reload_extension("cogs." + cog)
        except Exception as e:
            await self.send(ctx, f"Error while reloading extension: {cog}\n``{e}``")
            return
        await self.send(ctx, "Successfully reloaded cog: " + cog)

    @commands.command(name="eval", aliases=["ev"])
    @commands.is_owner()
    async def eval_message(self, ctx, *, msg):
        await self.send(ctx, f"{eval(msg)}\uFEFF")

    @commands.command(name="awaiteval", aliases=["await"])
    @commands.is_owner()
    async def await_eval_message(self, ctx, *, msg):
        await self.send(ctx, f"{await eval(msg)}\uFEFF")


def setup(bot):
    bot.add_cog(Owner(bot))
