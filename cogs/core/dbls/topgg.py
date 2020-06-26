import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.dblpy = dbl.DBLClient(self.bot, self.bot.dbl_keys[0],
                                   webhook_path="/dbl_webhook_hypstats",
                                   webhook_auth=self.bot.dbl_keys[1],
                                   webhook_port=5000, autopost=True)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        pass
