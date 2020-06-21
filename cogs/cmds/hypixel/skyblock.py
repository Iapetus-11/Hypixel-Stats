import arrow
import asyncio
import base64
import concurrent.futures
import discord
import gzip
from discord.ext import commands
from math import floor, ceil


class SkyBlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

        self.embed = discord.Embed(color=self.bot.cc)

    def unzip(self, data):
        b64 = data["inv_armor"]["data"]
        bytes = base64.b64decode(b64)
        print(bytes)
        print("\n\n\n\n\n\n")
        decomp = gzip.decompress(bytes)
        print(decomp)
        return decomp

    @commands.command(name="skyblock", aliases=["sb"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skyblock(self, ctx, *, player):
        def author_check(message):  # Basic check to make sure author and other stuff is proper right
            return message.author == ctx.message.author and ctx.guild == message.guild and ctx.channel == message.channel

        async with ctx.typing():  # Fetch player from cache or api
            p = await self.cache.get_player(player)

            head = await self.cache.get_player_head(player)

        try:
            skyblock = p.STATS["SkyBlock"]
        except KeyError:
            raise NoStatError

        profiles = list(skyblock.get("profiles"))

        profile_names = f"Choose one with the provided indexes:\n\n"

        for profile_id in profiles:
            profile_names += f'`{profiles.index(profile_id) + 1}.` **{skyblock["profiles"][profile_id].get("cute_name")}** ' \
                             f'[`{skyblock["profiles"][profile_id].get("profile_id")}`]\n'
        picker_embed = discord.Embed(color=self.bot.cc, description=profile_names)
        picker_embed.set_author(name=f"{p.DISPLAY_NAME}'s SkyBlock Islands:", icon_url=head)
        picker_embed.set_footer(text="Just send one of the above numbers!")
        await ctx.send(embed=picker_embed)

        valid = False

        try:
            for i in range(0, 3, 1):
                index = await self.bot.wait_for('message', check=author_check, timeout=20)

                try:
                    index = int(index.content)
                except ValueError:
                    await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That's not a valid index!"))
                else:
                    if index > len(profiles) or index <= 0:
                        await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That's not a valid index!"))
                    else:
                        valid = True
                        break
            if not valid:
                await ctx.send(embed=discord.Embed(color=self.bot.cc, description="The command was canceled."))
                return
        except asyncio.TimeoutError:
            return

        base = skyblock['profiles'][profiles[index - 1]]
        profile_id = base["profile_id"]

        stats = await self.cache.get_skyblock_stats(profile_id)

        if stats["profile_id"] == profile_id:
            coop = True
        else:
            coop = False

        members = []

        for member in list(stats.get('members', [])):
            if member == profile_id:
                members.append(f"**{discord.utils.escape_markdown(await self.cache.get_player_name(member))}**")
            else:
                members.append(discord.utils.escape_markdown(await self.cache.get_player_name(member)))

        if len(members) > 3:
            members = [f"**{p.DISPLAY_NAME}**", f"{len(members) - 1} others"]

        user_island_stats = stats["members"].get(p.UUID)

        if ctx.author.id == 536986067140608041:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                armor = await self.bot.loop.run_in_executor(pool, self.unzip, args=(user_island_stats,))

        first_join = user_island_stats.get("first_join", 0)
        kills = ceil(user_island_stats['stats'].get('kills', 0))
        deaths = floor(user_island_stats.get('deaths', 0))
        coin_purse = ceil(user_island_stats.get('coin_purse', 0))
        fairy_souls = user_island_stats.get('fairy_souls', 0)
        fairy_souls_collected = user_island_stats.get('fairy_souls_collected', 0)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Skyblock Stats", icon_url=head)

        embed.description = f'**{base.get("cute_name")}** - [``{profile_id}``]'

        embed.add_field(name="Co-Op", value=coop)
        embed.add_field(name="Members", value=', '.join(members))
        embed.add_field(name="First Join", value=arrow.Arrow.fromtimestamp(first_join / 1000).humanize())

        embed.add_field(name="Coin Purse", value=coin_purse)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)

        embed.add_field(name="Armor", value="Work in progress!")
        embed.add_field(name="Fairy Souls", value=fairy_souls)
        embed.add_field(name="Fairy Souls Collected", value=fairy_souls_collected)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SkyBlock(bot))
