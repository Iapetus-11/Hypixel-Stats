import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.dblpy = dbl.DBLClient(self.bot)
