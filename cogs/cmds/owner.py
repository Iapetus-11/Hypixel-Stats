import discord
import os
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

    async def send(self, location, message):  # idk because it's easy ig
        try:
            await location.send(embed=discord.Embed(color=await self.bot.cc(location.author.id), description=message))
        except Exception:
            await location.send(embed=discord.Embed(color=await self.bot.cc(), description=message))

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
        if cog == "all" or cog == "everything" or cog == "al":
            await self.reload_all(ctx)
            return
        try:
            self.bot.reload_extension("cogs." + cog)
        except Exception as e:
            await self.send(ctx, f"Error while reloading extension: {cog}\n``{e}``")
            return
        await self.send(ctx, "Successfully reloaded cog: " + cog)

    @commands.command(name="reloadall")
    @commands.is_owner()
    async def reload_all(self, ctx):
        for cog in self.bot.cog_list:
            self.bot.reload_extension(cog)
        await self.send(ctx, f"Successfully reloaded {len(self.bot.cog_list)} cogs.")

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

    @commands.command(name="setpremium", aliases=["setprem", "premium"])
    @commands.is_owner()
    async def set_premium(self, ctx, user: discord.User, expires=-1):
        await self.db.set_premium(user.id, expires)
        await self.send(ctx, f"Gave {user} premium.")

    @commands.command(name="removepremium", aliases=["remprem", "removeprem"])
    @commands.is_owner()
    async def remove_premium(self, ctx, user: discord.User):
        await self.db.remove_premium(user.id)
        await self.send(ctx, f"Removed {user}'s premium.")

def setup(bot):
    bot.add_cog(Owner(bot))
