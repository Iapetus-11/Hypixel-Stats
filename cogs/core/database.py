import arrow
import discord
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.db = bot.db

    async def get_prefix(self, gid):
        pp = await self.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1", gid)
        if pp is None:
            return "h!"

    async def set_prefix(self, gid, prefix):
        if prefix == "h!" or prefix == "H!":
            await self.drop_prefix(gid)
            return

        pp = await self.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1", gid)
        async with self.db.acquire() as con:
            if pp is None:
                await con.execute("INSERT INTO prefixes VALUES ($1, $2)", gid, prefix)
            else:
                await con.execute("UPDATE prefixes SET prefix=$1 WHERE gid=$2", prefix, gid)

    async def drop_prefix(self, gid):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM prefixes WHERE gid=$1", gid)

    async def link_account(self, id, uuid):
        async with self.db.acquire() as con:
            await con.execute("INSERT INTO accounts VALUES ($1, $2)", id, uuid)

    async def get_linked_account_via_id(self, id):
        return await self.db.fetchrow("SELECT * FROM accounts WHERE id=$1", id)

    async def get_linked_account_via_uuid(self, uuid):
        return await self.db.fetchrow("SELECT * FROM accounts WHERE uuid=$1", uuid)

    async def drop_linked_account(self, id):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM accounts WHERE id=$1", id)

    async def is_premium(self, id):
        prem = await self.db.fetchrow("SELECT * FROM premium WHERE id=$1", id)
        return prem is not None

    async def set_premium(self, id):
        if not await self.is_premium(id):
            async with self.db.acquire() as con:
                await con.execute("INSERT INTO premium VALUES ($1, $2)", id, arrow.utcnow().timestamp)

    async def remove_premium(self, id):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM premium WHERE id=$1", id)


def setup(bot):
    bot.add_cog(Database(bot))
