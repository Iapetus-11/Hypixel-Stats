import aiopypixel
import arrow
import asyncio
import discord
from discord.ext import commands
from math import floor, ceil


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")
        self.db = self.bot.get_cog("Database")

    async def filter_sections(self, pp):
        cleaned = ""
        for i in range(1, len(pp), 1):
            if pp[i - 1] != "§" and pp[i] != "§":
                cleaned += pp[i]
        return cleaned

    @commands.command(name="link", aliases=["discordlink", "linkmc", "mclink", "linkaccount", "linkacc"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def link_account(self, ctx, mc_username: str):
        linked = await self.db.get_linked_account_via_id(ctx.author.id)

        if linked is not None:
            await ctx.send("It appears you've already linked your account!")
            return

        uuid = await self.cache.get_player_uuid(mc_username)

        desc = "Login to Hypixel and type `/api` in the chat. Then, send that text here to link your account!"
        embed = discord.Embed(color=self.bot.cc, description=desc,
                              title=":link: Link your Discord and MC accounts :link:")
        embed.set_footer(text="API keys are NOT stored and are used purely for verification purposes.")
        await ctx.author.send(embed=embed)

        def author_check(m):
            return m.author.id == ctx.author.id and m.guild is None

        try:
            key = await self.bot.wait_for("message", check=author_check, timeout=(10 * 60))
        except asyncio.TimeoutError:
            await ctx.author.send(
                embed=discord.Embed(color=self.bot.cc, description="I stopped waiting for you to reply."))
            return

        try:
            key_owner_uuid = (await self.cache.get_key_data(key.content))["record"]["owner"]
        except Exception:
            await ctx.author.send(embed=discord.Embed(color=self.bot.cc,
                                                      description="Uh oh, that key appears to be invalid, are you sure it's right?"))
            return

        del key  # see?

        # Hypixel API sometimes returns uuids with dashes
        if uuid != key_owner_uuid and uuid != key_owner_uuid.replace("-", ""):
            await ctx.author.send(embed=discord.Embed(color=self.bot.cc,
                                                      description="Hmm that didn't work. Did you type the api key and your username correctly?"))
            return

        await self.db.link_account(ctx.author.id, uuid)  # Insert uuid and discord id into db
        await ctx.author.send(embed=discord.Embed(color=self.bot.cc, description="Account linked successfully!"))

    @commands.command(name="unlink", aliases=["unlinkacc", "unlinkaccount", "deletelink", "removeaccount"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def unlink_account(self, ctx):
        if await self.db.get_linked_account_via_id(ctx.author.id) is not None:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description="You don't have an account linked!"))
            return

        await self.db.drop_linked_account(ctx.author.id)
        await ctx.send(
            embed=discord.Embed(color=self.bot.cc, description="You have unlinked your account successfully."))

    @commands.group(name="playerprofile", aliases=["profile", "h", "player", "p", "pp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def player_profile(self, ctx, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        embed = discord.Embed(color=self.bot.cc, description=f"[`{p.UUID}`]")

        linked_acc = (await self.db.get_linked_account_via_uuid(p.UUID))[0]

        online = f"{self.bot.EMOJIS['offline_status']} offline"
        if p.LAST_LOGIN is not None and p.LAST_LOGOUT is not None:
            last_online = ["Last Online", arrow.Arrow.fromtimestamp(p.LAST_LOGOUT / 1000).humanize()]  # I love arrow
            if p.LAST_LOGIN > p.LAST_LOGOUT:
                online = f"{self.bot.EMOJIS['online_status']} online"
                last_online = ["Online Since", arrow.Arrow.fromtimestamp(
                    p.LAST_LOGIN / 1000).humanize()]  # bc this value is obtained from last_login
        else:
            last_online = "Never"

        print(p.UUID)

        player_pfp = await self.cache.get_player_head(p.UUID)

        guild = p.GUILD
        if guild is None:
            guild = "None"
        else:
            guild = await self.cache.get_guild_name_from_id(p.GUILD)
            guild = f"[{discord.utils.escape_markdown(guild)}]({f'https://hypixel.net/guilds/{guild}'.replace(''' ''', '''%20''')})"

        if p.PREFIX is None:
            prefix = ""
        else:
            prefix = await self.filter_sections(p.PREFIX) + " "

        rank = p.RANK

        if rank is None:
            if prefix != "":
                rank = prefix[1:len(prefix) - 2]
            else:
                rank = "None"
        else:
            if prefix == "":
                prefix = f"[{rank}] ".replace("_", "").replace("PLUS", "+")

        friends = await self.cache.get_player_friends(player)

        embed.set_author(name=f"{prefix}{p.DISPLAY_NAME}'s Profile",
                         url=f"https://hypixel.net/player/{p.DISPLAY_NAME}", icon_url=player_pfp)
        embed.add_field(name="Rank", value=rank.replace("_", "").replace("PLUS", "+"), inline=True)
        embed.add_field(name="Level",
                        value=f"{await self.cache.hypixel.calcPlayerLevel(p.EXP if p.EXP is not None else 0)}",
                        inline=True)
        embed.add_field(name="Karma", value=f"{p.KARMA}", inline=True)

        embed.add_field(name="Guild", value=guild, inline=True)
        embed.add_field(name="Status", value=online, inline=True)
        embed.add_field(name=last_online[0], value=last_online[1], inline=True)

        embed.add_field(name="Friends", value=len([] if friends is None else friends))
        embed.add_field(name="Discord", value=self.bot.get_user(linked_acc))
        embed.add_field(name="Achievements", value=f"{len(p.ONE_TIME_ACHIEVEMENTS)}")

        embed.set_footer(text="Made by Iapetus11 & TrustedMercury")

        await ctx.send(embed=embed)

    @commands.command(name="friends", aliases=["pf", "pfriends", "playerfriends", "friendsof", "player_friends"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        puuid = await self.cache.get_player_uuid(player)

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** doesn't have any friends! :cry:"))
            return

        if len(player_friends) > 1024:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** has too many friends to show! :cry:"))
            return

        head = await self.cache.get_player_head(puuid)

        embed = discord.Embed(color=self.bot.cc)
        embed.set_author(name=f"{player}'s friends ({len(player_friends)} total!)",
                         icon_url=head)

        async with ctx.typing():
            names = [await self.cache.get_player_name(uuid) for uuid in player_friends]

            chonks = [names[i:i + 10] for i in range(0, len(names), 10)]  # groups of 10 of the usernames

        try:
            stop = False
            page = 0
            max_pages = ceil(len(chonks) / 3)

            while True:
                page += 1

                if not stop and len(chonks) > 3:
                    embed = discord.Embed(color=self.bot.cc, description="Type ``more`` for more!")
                else:
                    embed = discord.Embed(color=self.bot.cc)

                embed.set_author(
                    name=f"{player}'s friends ({len(player_friends)} total!)",
                    icon_url=head)

                embed.set_footer(text=f"[Page {page}/{max_pages}]")

                for i in range(0, 3, 1):
                    try:
                        embed.add_field(name="\uFEFF",
                                        value=discord.utils.escape_markdown("\n\n".join(chonks.pop(0))))
                    except IndexError:
                        pass

                await ctx.send(embed=embed)

                if stop or len(player_friends) < 31:
                    return

                if len(chonks) - 3 < 1:
                    stop = True

                def check(m):
                    return m.author.id == ctx.author.id and m.content == "more"

                await self.bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="playerguild", aliases=["pg", "playerg", "pguild", "guildofplayer", "player_guild"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_guild(self, ctx, player):
        await ctx.trigger_typing()

        player_guild = await self.cache.get_player_guild(player)

        if player_guild is None:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** isn't in a guild!"))
            return

        g = await self.cache.get_guild(player_guild)

        author = f"{discord.utils.escape_markdown(player)}'s Guild ({discord.utils.escape_markdown(g.NAME)})"

        desc = g.DESCRIPTION
        if desc is None:
            embed = discord.Embed(color=self.bot.cc)
        else:
            length = len(author) + 2
            length = length if length > 30 else 30
            embed = discord.Embed(color=self.bot.cc,
                                  description='\n'.join(
                                      desc[i:i + length] for i in
                                      range(0, len(desc), length)))

        member_count = len(g.MEMBERS)
        coins = g.COINS
        xp = g.EXP
        tag = g.TAG
        created = arrow.Arrow.fromtimestamp(g.CREATED / 1000).humanize()

        embed.set_author(name=author)

        embed.add_field(name="Members", value=member_count, inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Tag", value=tag, inline=True)

        embed.add_field(name="Coins", value=coins, inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="XP", value=xp, inline=True)

        embed.add_field(name="Created", value=created, inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Player(bot))
