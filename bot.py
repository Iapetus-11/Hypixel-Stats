import asyncio
import asyncpg
import discord
import json
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('discord_token')
DB_PASSWORD = os.getenv('db_password')
HYPIXEL = os.getenv('hypixel_key')

logging.basicConfig(level=logging.INFO)  # Should be logging.WARNING in the future, like this for debug purposes ig
logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Hide those annoying errors


async def get_prefix(_bot, message):
    if message.guild is not None:
        prefix = await _bot.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1",
                                        message.guild.id)
        if prefix is not None:
            return prefix

    return "h!"


bot = commands.AutoShardedBot(shard_count=1, command_prefix=get_prefix, case_insensitive=True)

with open('data/emojis.json') as EMOJIS:
    bot.EMOJIS = json.load(EMOJIS)

bot.cc = discord.Color.gold()
bot.guild_invite_code = "MZ2cXxF"
bot.error_channel_id = 718983583779520541

bot.ratelimited_wait_time = .5  # seconds, obviously

bot.hypixel_key = HYPIXEL


async def setup_db():
    bot.db = await asyncpg.create_pool(
        host="localhost",
        database="hypixel-stats-bot",
        user="pi",
        password=DB_PASSWORD)


asyncio.get_event_loop().run_until_complete(setup_db())


bot.cog_list = ["cogs.core.errors",
                "cogs.core.events",
                "cogs.core.database",
                "cogs.core.cache",
                "cogs.cmds.useful",
                "cogs.cmds.settings",
                "cogs.cmds.basic_mc",
                "cogs.cmds.hypixel.player"]

for cog in bot.cog_list:
    bot.load_extension(cog)


@bot.check
async def bot_check(ctx):

    if not bot.is_ready():
        await ctx.send(embed=discord.Embed(color=bot.cmd_c, description="Hold on! We're starting up!"))
        return False

    return not ctx.author.bot


bot.run(TOKEN, bot=True)
