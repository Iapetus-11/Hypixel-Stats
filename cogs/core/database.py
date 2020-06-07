from discord.ext import commands
import discord


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.db = bot.db

    async def get_prefix(self, gid):
        pp = await self.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1", gid)
        if pp is None:
            return "h!"

    async def set_prefix(self, gid, prefix):
        pp = await self.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1", gid)
        async with self.db.acquire() as con:
            if pp is None:
                await con.execute("INSERT INTO prefixes VALUES ($1, $2)", gid, prefix)
            else:
                await con.execute("UPDATE prefixes SET prefix=$1 WHERE gid=$2", prefix, gid)

    async def drop_prefix(self, gid):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM prefixes WHERE gid=$1", gid)


def setup(bot):
    bot.add_cog(Database(bot))
