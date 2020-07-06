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

    def cog_unload(self):
        self.bot.loop.create_task(self.dblpy.close())

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        self.logger.info("\u001b[35m DBL WEBHOOK TEST \u001b[0m")
        channel = self.bot.get_channel(718983583779520540)
        await channel.send(embed=discord.Embed(color=await self.bot.cc(), description="DBL WEBHOOK TEST"))

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user_id = int(data["user"])
        print(f"\u001b[32;1m {user_id} VOTED ON TOP.GG \u001b[0m")


def setup(bot):
    bot.add_cog(TopGG(bot))
