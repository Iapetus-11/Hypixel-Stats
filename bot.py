"""
bot.py
basic initialization and configuration of hypixel-stats
- loads external files - .env, .json
- creates database connection pool
- loads cogs and prefixes
- creates bot instance
"""

import os
import json
import asyncio
import asyncpg
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv


# loads environment variables
load_dotenv()
TOKEN = os.getenv('discord_token')
DB_PASSWORD = os.getenv('db_password')
HYPIXEL = os.getenv('hypixel_key')


# sets up logging methods
logging.basicConfig(level=logging.INFO)  # Should be logging.WARNING in the future, like this for debug purposes ig
logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Hide those annoying errors


async def get_prefix(_bot, message):
    """fetches the custom prefix for the provided server"""

    if message.guild is not None:
        prefix = await _bot.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1",
                                        message.guild.id)
        if prefix is not None:
            return prefix

    return "h!"


bot = commands.AutoShardedBot(
    command_prefix=get_prefix,
    case_insensitive=True
)


with open('data/emojis.json') as EMOJIS:
    bot.EMOJIS = json.load(EMOJIS)

with open('data/config.json') as CONFIG:
    bot.CONFIG = json.load(CONFIG)

bot.cc = discord.Color.gold()
bot.guild_invite_code = "MZ2cXxF"
bot.error_channel_id = 718983583779520541
bot.start_time = None
bot.TIMEOUT_MESSAGE = "You took too long to answer, the command was canceled."

bot.ratelimited_wait_time = .5  # seconds, obviously

bot.hypixel_key = HYPIXEL


async def setup_db():
    """Sets up the database pool connection"""

    bot.db = await asyncpg.create_pool(
        host="localhost",
        database="hypixel-stats-bot",
        user="pi",
        password=DB_PASSWORD)


asyncio.get_event_loop().run_until_complete(setup_db())


bot.cog_list = [
    "cogs.core.errors",
    "cogs.core.events",
    "cogs.core.database",
    "cogs.core.cache",
    "cogs.cmds.owner",
    "cogs.cmds.useful",
    "cogs.cmds.settings",
    "cogs.cmds.basic_mc",
    "cogs.cmds.hypixel.player",
    "cogs.cmds.hypixel.guild"
]

for cog in bot.cog_list:
    bot.load_extension(cog)


@bot.check
async def bot_check(ctx):

    if not bot.is_ready():
        embed = discord.Embed(
            color=bot.CONFIG["cc"],
            description="Hold on! We're starting up!"
        )
        await ctx.send(embed=embed)
        return False

    return not ctx.author.bot


bot.run(TOKEN, bot=True)
