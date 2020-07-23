import arrow
import discord
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = bot.db

        self.stop_loops = False
        self.bot.loop.create_task(self.expiry_sweep())

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

    async def drop_linked_account(self, uid):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM accounts WHERE uid=$1", uid)

    async def get_color(self, uid):  # uid bigint, returns
        color = await self.db.fetchrow("SELECT * FROM color WHERE uid=$1", uid)
        return (await self.bot.cc()).value if color is None else color['color']  # intentionally left blank

    async def set_color(self, uid, color):  # bigint, varchar(10)
        if color == 15844367:  # discord.Color.gold().value
            async with self.db.acquire() as con:
                await con.execute("DELETE FROM color WHERE uid = $1", uid)
            return
        prev = await self.db.fetchrow("SELECT * FROM color WHERE uid=$1", uid)
        async with self.db.acquire() as con:
            if prev is not None:
                await con.execute("UPDATE COLOR SET color = $1 WHERE uid = $2", color, uid)
            else:
                await con.execute("INSERT INTO color VALUES ($1, $2)", uid, color)

    async def is_premium(self, uid):
        prem = await self.db.fetchrow("SELECT * FROM premium WHERE uid=$1", uid)
        return prem is not None

    async def add_premium(self, uid, expires):
        if not await self.is_premium(uid):
            async with self.db.acquire() as con:
                await con.execute("INSERT INTO premium VALUES ($1, $2)", uid, expires)

    async def remove_premium(self, uid):
        async with self.db.acquire() as con:
            await con.execute("DELETE FROM premium WHERE uid=$1", uid)

    async def expiry_sweep(self):
        while True:
            all = await self.db.fetch("SELECT * FROM premium")
            async with self.db.acquire() as con:
                for entry in all:
                    if arrow.utcnow().timestamp > entry[1] > 1:
                        await con.execute("DELETE FROM premium WHERE uid=$1", entry[0])
                        await self.set_color(entry[0], 15844367)

            for _ in range(0, 60 * 2.5, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return


def setup(bot):
    bot.add_cog(Database(bot))
