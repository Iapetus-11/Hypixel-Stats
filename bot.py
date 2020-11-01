"""
bot.py
basic initialization and configuration of hypixel-stats
- loads external files - .env, .json
- creates database connection pool
- loads cogs
- creates bot instance
"""

import arrow
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
DB_HOST = os.getenv("db_host")
DB_NAME = os.getenv("db_name")
DB_USER = os.getenv("db_user")
# DB_VB_PASSWORD = os.getenv('db_vb_password')
HYPIXEL = os.getenv('hypixel_key')
DBL = [os.getenv("dbl1"), os.getenv("dbl2")]
DONATEBOT_SECRET = os.getenv('donatebot_secret')

# sets up logging methods
logging.basicConfig(level=logging.WARNING)  # Should be logging.WARNING in the future, like INFO for debug purposes ig
logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Hide those annoying errors

tips = [
    "Need more help? Check out the [support server](https://discord.gg/MZ2cXxF)!",
    "Want to link your account? Do `h!link <mc_username>` to link it!",
    # "Want some fancy smancy premium features? Go [**here**](https://donatebot.io/checkout/718983582898585602)!",
    # "Hey, you should check out Hypixel Stats [**PREMIUM**]!(https://donatebot.io/checkout/718983582898585602)! You get a bunch of cool and useful features with it, and it's really cheap!"
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


async def cc(self, uid=None):
    if uid is None:
        return discord.Color.gold()
    else:
        color = await self.db.fetchrow("SELECT * FROM color WHERE uid=$1", uid)
        return discord.Color.gold() if color is None else color['color']


bot.cc = cc.__get__(bot)  # Bind the async cc() method to the bot class without subclassing commands.AutoShardedBot

# Don't even think about it Hg
# bot.cc = discord.Color.gold()  # color of the embeds
bot.guild_invite_code = "MZ2cXxF"
bot.support_guild_id = 718983582898585602
bot.error_channel_id = 718983583779520541
bot.start_time = None  # Will be set later in cogs.core.events
bot.timeout_message = "You took too long to answer, the command was canceled."
bot.ratelimited_wait_time = 1  # seconds, obviously
bot.hypixel_key = HYPIXEL
bot.cmd_count = 0
bot.start_time = arrow.utcnow()
bot.dbl_keys = DBL
bot.donatebot_auth_secret = DONATEBOT_SECRET
bot.api_trouble = False

with open('data/emojis.json') as EMOJIS:
    bot.EMOJIS = json.load(EMOJIS)


async def setup_dbs():
    """Sets up the database pool connection"""

    bot.db = await asyncpg.create_pool(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # bot.db_villager_bot = await asyncpg.create_pool(
    #     host="localhost",
    #     database="villagerbot",
    #     user="pi",
    #     password=DB_VB_PASSWORD
    # )


asyncio.get_event_loop().run_until_complete(setup_dbs())


bot.cog_list = [
    "cogs.core.errors",
    "cogs.core.database",
    "cogs.core.events",
    "cogs.core.cache",
    "cogs.core.autoroles",
    "cogs.core.dbls.topgg",
    "cogs.core.paymenthooks",
    "cogs.cmds.owner",
    "cogs.cmds.useful",
    "cogs.cmds.settings",
    "cogs.cmds.basic_mc",
    "cogs.cmds.hypixel.player",
    "cogs.cmds.hypixel.guild",
    "cogs.cmds.hypixel.games",
    "cogs.cmds.hypixel.skyblock",
    "cogs.cmds.hypixel.general"
]

for cog in bot.cog_list:
    bot.load_extension(cog)


@bot.check
async def bot_check(ctx):
    bot.cmd_count += 1

    if await bot.get_cog("Database").is_channel_disabled(ctx.channel.id):
        if ctx.command.cog.qualified_name not in ["Owner", "Settings"]:
            return

    if not bot.is_ready():
        embed = discord.Embed(
            color=await bot.cc(),
            description="Hold on! We're starting up!"
        )
        await ctx.send(embed=embed)
        return False

    if randint(0, 60) == 15:
        if not bot.api_trouble:
            if not await bot.get_cog("Database").is_premium(ctx.author.id):
                await ctx.send(embed=discord.Embed(color=await bot.cc(ctx.author.id),
                                                   description=f"**{choice(['Handy Dandy Tip:', 'Cool Tip:', 'Pro Tip:'])}** {choice(tips)}"))
        else:
            await ctx.send(embed=discord.Embed(color=await bot.cc(ctx.author.id),
                                               description=":warning: The Hypixel API seems to be having trouble right now, "
                                                           "that could be the reason for any errors or slow bot responses :warning:"))

    return not ctx.author.bot


bot.run(TOKEN, bot=True)
