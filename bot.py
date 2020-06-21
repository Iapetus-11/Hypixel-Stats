"""
bot.py
basic initialization and configuration of hypixel-stats
- loads external files - .env, .json
- creates database connection pool
- loads cogs
- creates bot instance
"""

import asyncio
import asyncpg
import discord
import json
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
from random import randint, choice

# loads environment variables
load_dotenv()
TOKEN = os.getenv('discord_token')
DB_PASSWORD = os.getenv('db_password')
HYPIXEL = os.getenv('hypixel_key')

# sets up logging methods
logging.basicConfig(level=logging.INFO)  # Should be logging.WARNING in the future, like this for debug purposes ig
logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Hide those annoying errors

tips = [
    "Need more help? Check out the [support server](https://discord.gg/MZ2cXxF)!",
    "Hey! Check out one of our other bots, [vidio](https://top.gg/bot/689210550680682560), a YouTube sim/roleplay bot!",
    "Hey! Check out another of our bots, [Villager Bot!](https://top.gg/bot/639498607632056321), a Minecraft themed bot with a ton of features!"
]


async def get_prefix(_bot, message):
    """fetches the custom prefix for the provided server"""

    if message.guild is not None:
        prefix = await _bot.db.fetchrow("SELECT prefix FROM prefixes WHERE gid=$1",
                                        message.guild.id)
        if prefix is not None:
            return prefix

    return "H!" if message.content.startswith("H!") else "h!"


bot = commands.AutoShardedBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    help_command=None,
    max_messages=512
)

# Don't even think about it Hg
bot.cc = discord.Color.gold()  # color of the embeds
bot.guild_invite_code = "MZ2cXxF"
bot.error_channel_id = 718983583779520541
bot.start_time = None  # Will be set later in cogs.core.events
bot.timeout_message = "You took too long to answer, the command was canceled."
bot.ratelimited_wait_time = .75  # seconds, obviously
bot.hypixel_key = HYPIXEL
bot.cmd_count = 0

with open('data/emojis.json') as EMOJIS:
    bot.EMOJIS = json.load(EMOJIS)


async def setup_db():
    """Sets up the database pool connection"""

    bot.db = await asyncpg.create_pool(
        host="localhost",
        database="hypixel-stats-bot",
        user="pi",
        password=DB_PASSWORD
    )


asyncio.get_event_loop().run_until_complete(setup_db())


bot.cog_list = [
    "cogs.core.errors",
    "cogs.core.database",
    "cogs.core.events",
    "cogs.core.cache",
    "cogs.cmds.owner",
    "cogs.cmds.useful",
    "cogs.cmds.settings",
    "cogs.cmds.basic_mc",
    "cogs.cmds.hypixel.player",
    "cogs.cmds.hypixel.guild",
    "cogs.cmds.hypixel.games",
    "cogs.cmds.hypixel.skyblock"
]

for cog in bot.cog_list:
    bot.load_extension(cog)


@bot.check
async def bot_check(ctx):
    bot.cmd_count += 1

    if not bot.is_ready():
        embed = discord.Embed(
            color=bot.cc,
            description="Hold on! We're starting up!"
        )
        await ctx.send(embed=embed)
        return False

    if randint(0, 45) == 15:
        await ctx.send(embed=discord.Embed(color=bot.cc,
                                           description=f"**{choice(['Handy Dandy Tip:', 'Cool Tip:', 'Pro Tip:'])}** {choice(tips)}"))

    return not ctx.author.bot


bot.run(TOKEN, bot=True)
