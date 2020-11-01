import asyncpg
import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.dblpy = dbl.DBLClient(self.bot, self.bot.dbl_keys[0],
                                   webhook_path="/updoot_topgg",
                                   webhook_auth=self.bot.dbl_keys[1],
                                   webhook_port=3209, autopost=True)

        # self.db_vb = self.bot.db_villager_bot

    def cog_unload(self):
        self.bot.loop.create_task(self.dblpy.close())

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        print("\u001b[35m DBL WEBHOOK TEST \u001b[0m")
        channel = self.bot.get_channel(718983583779520540)
        await channel.send(embed=discord.Embed(color=await self.bot.cc(), description="DBL WEBHOOK TEST"))

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user_id = int(data["user"])
        print(f"\u001b[32;1m {user_id} VOTED ON TOP.GG \u001b[0m")
        #
        # user = self.bot.get_user(user_id)
        #
        # amount = 32
        # prem_minutes = 15
        # if await self.dblpy.get_weekend_status():
        #     amount *= 2
        #     prem_minutes *= 2
        #
        # u_db_bal = await self.db_vb.fetchrow("SELECT amount FROM currency WHERE id = $1", user_id)
        #
        # if u_db_bal is not None:
        #     if user is not None:
        #         msg = f"Thank you for voting! You've received `{amount} emeralds` in Villager Bot " \
        #               f"and `{prem_minutes} minutes` of Hypixel Stats **Premium**!"
        #         await user.send(embed=discord.Embed(color=await self.bot.cc(user_id), description=msg))
        #
        #     async with self.db_vb.acquire() as con:
        #         await con.execute("UPDATE currency SET amount = $1 WHERE id = $2", u_db_bal[0] + amount, user_id)
        # else:
        #     if user is not None:
        #         msg = f"Thank you for voting! You've received `{prem_minutes} minutes` of Hypixel Stats **Premium**!"
        #         await user.send(embed=discord.Embed(color=await self.bot.cc(user_id), description=msg))
        #
        #         timestamp_ends = arrow.utcnow().shift(minutes=+prem_minutes).timestamp
        #         await self.db.add_premium(user_id, timestamp_ends)


def setup(bot):
    bot.add_cog(TopGG(bot))
