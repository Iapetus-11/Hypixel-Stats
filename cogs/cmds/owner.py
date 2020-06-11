import discord
import os
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, location, message):  # idk because it's easy ig
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

    @commands.command(name="reverselookup", aliases=["lookup"])
    @commands.is_owner()
    async def guild_lookup(self, ctx, user: discord.User):
        gds = ""
        for guild in self.bot.guilds:
            if guild.get_member(user.id) is not None:
                gds += str(guild) + " **|** " + str(guild.id) + "\n"
        if not gds == "":
            await ctx.send(gds)
        else:
            await self.send(ctx, "No results...")

    @commands.command(name="getlatest", aliases=["gitpull", "git_pull"])
    @commands.is_owner()
    async def get_latest(self, ctx):
        os.system("git pull > git_pull_log 2>&1")
        with open("git_pull_log", "r") as f:
            await self.send(ctx, f"```diff\n{f.read()}\n```")
        os.system("rm git_pull_log")


def setup(bot):
    bot.add_cog(Owner(bot))
