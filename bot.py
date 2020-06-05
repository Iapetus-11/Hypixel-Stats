from discord.ext import commands
import discord
import logging
import asyncio
import asyncpg
import json

logging.basicConfig(level=logging.INFO) # Should be logging.WARNING in the future, like this for debug purposes ig
logging.getLogger("asyncio").setLevel(logging.CRITICAL) # Hide those annoying errors


with open("keys.json") as k
    keys = json.load(k)

async def get_prefix(bot, ctx):
    return "!"

bot = commands.AutoShardedBot(shard_count=1, command_prefix=get_prefix, help_command=None, case_insensitive=True, max_messages=512)

# Stuffs
bot.cmd_c = "0xFFAA00"

async def setup_db():
    bot.db = await asyncpg.create_pool(host="localhost", database="hypixel-bot", user="", password=keys["psql"], command_timeout=5)

asyncio.get_event_loop().run_until_complete(setup_db())

# Yes this bc !!reload *
bot.cog_list = []

for cog in bot.cog_list:
    bot.load_extension(cog)

@bot.check
async def _bot_check_thingy(ctx):
    if not bot.is_ready():
        await ctx.send(embed=discord.Embed(color=bot.cmd_c, description="Hold on! We're starting up!"))
        return False
    return not ctx.author.bot

bot.run(keys["discord"], bot=True)
