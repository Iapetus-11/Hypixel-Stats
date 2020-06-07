from discord.ext import commands
from dotenv import load_dotenv
import discord
import logging
import asyncio
import asyncpg
import json
import os


load_dotenv()
TOKEN = os.getenv('bot_token')
USER = os.getenv('database_user')
DATABASE = os.getenv('database_name')
PASSWORD = os.getenv('database_password')
HOSTNAME = os.getenv('database_hostname')


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

with open('data/config.json') as CONFIG:
    bot.CONFIG = json.load(CONFIG)

with open('data/emojis.json') as EMOJIS:
    bot.EMOJIS = json.load(EMOJIS)

bot.cc = bot.CONFIG["color"]
bot.guild_invite_code = bot.CONFIG["guild_invite"]
bot.error_channel_id = bot.CONFIG["error_channel_is"]


async def setup_db():

    bot.db = await asyncpg.create_pool(
        host=HOSTNAME,
        database=DATABASE,
        user=USER,
        password=PASSWORD)


asyncio.get_event_loop().run_until_complete(setup_db())


bot.cog_list = ["cogs.core.errors",
                "cogs.core.events",
                "cogs.core.database",
                "cogs.cmds.basic_mc",
                "cogs.cmds.settings"]

for cog in bot.cog_list:
    bot.load_extension(cog)


@bot.check
async def bot_check(ctx):

    if not bot.is_ready():
        await ctx.send(embed=discord.Embed(color=bot.cmd_c, description="Hold on! We're starting up!"))
        return False

    return not ctx.author.bot


bot.run(TOKEN, bot=True)
