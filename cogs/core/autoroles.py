import asyncio
import discord
from discord.ext import commands


class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

        self.stop_loops = False
        self.bot.loop.create_task(self.premium_sweep())

    def cog_unload(self):
        self.stop_loops = True

    async def premium_sweep(self):
        while True:
            for member in self.bot.get_guild(self.bot.support_guild_id).members:
                if await self.db.is_premium(member.id):
                    try:
                        await member.add_roles(
                            self.bot.get_guild(self.bot.support_guild_id).get_role(732635033738674186))
                    except discord.HTTPException:
                        pass
                else:
                    try:
                        await member.remove_roles(
                            self.bot.get_guild(self.bot.support_guild_id).get_role(732635033738674186))
                    except discord.HTTPException:
                        pass

            for i in range(0, 60 * 10, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return


def setup(bot):
    bot.add_cog(AutoRoles(bot))
