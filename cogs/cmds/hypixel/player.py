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
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def link_account(self, ctx, mc_username: str = None):
        linked = await self.db.get_linked_account_via_id(ctx.author.id)

        if linked is not None:
            await ctx.send(
                embed=discord.Embed(color=await self.bot.cc(),
                                    description=f"It appears you've already linked your account!\n"
                                                f"If you'd like to unlink it, do `{ctx.prefix}unlink`"))
            return

        assumed = False
        if mc_username is None:
            assumed = True
            mc_username = ctx.author.name

        p_obj = await self.cache.get_player(mc_username)
        uuid = p_obj.UUID
        api_disc = p_obj.LINKED_ACCOUNTS.get("links", {}).get("DISCORD") if p_obj.LINKED_ACCOUNTS is not None else None
        if api_disc is not None:
            if api_disc == str(ctx.author):
                await self.db.link_account(ctx.author.id, uuid)
                await ctx.send(
                    embed=discord.Embed(color=await self.bot.cc(),
                                        description="You've successfully linked your account!"))
                return
            elif assumed:
                await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                                   description="Your Discord username and Minecraft username have to be the same to do this!"))
                return
        elif assumed:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"{discord.utils.escape_markdown(mc_username)} Doesn't have their Discord account linked to Hypixel. [Click here to link your account via Hypixel's website](https://hypixel.net/discord)"))
            return

        desc = "**Login to Hypixel** and type `/api` in the chat. Then, **send that text here** to link your account! Type `cancel` to cancel this process."
        embed = discord.Embed(color=await self.bot.cc(), description=desc,
                              title=":link: Link your Discord and MC accounts :link:")
        embed.set_footer(text="API keys are NOT stored and are used purely for verification purposes.")

        try:
            await ctx.author.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send(
                embed=discord.Embed(color=await self.bot.cc(), description="You have to let the bot dm you!"))
            return

        def author_check(m):
            return m.author.id == ctx.author.id and m.guild is None

        try:
            key = await self.bot.wait_for("message", check=author_check, timeout=(10 * 60))
        except asyncio.TimeoutError:
            await ctx.author.send(
                embed=discord.Embed(color=await self.bot.cc(), description=self.bot.timeout_message))
            return

        if key.content.lower() in ["cancel", "stop", "end"]:
            await ctx.author.send(
                embed=discord.Embed(color=await self.bot.cc(), description="Verification has been canceled."))
            return

        try:
            key_owner_uuid = (await self.cache.get_key_data(key.content))["record"]["owner"]
        except Exception:
            await ctx.author.send(embed=discord.Embed(color=await self.bot.cc(),
                                                      description="Uh oh, that key appears to be invalid, are you sure it's right?"))
            return

        del key  # see?

        # Hypixel API sometimes returns uuids with dashes
        if uuid != key_owner_uuid and uuid != key_owner_uuid.replace("-", ""):
            await ctx.author.send(embed=discord.Embed(color=await self.bot.cc(),
                                                      description="Hmm that didn't work. Did you type the api key and your username correctly?"))
            return

        await self.db.link_account(ctx.author.id, uuid)  # Insert uuid and discord id into db
        await ctx.author.send(
            embed=discord.Embed(color=await self.bot.cc(), description="Account linked successfully!"))

    @commands.command(name="unlink", aliases=["unlinkacc", "unlinkaccount", "deletelink", "removeaccount"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def unlink_account(self, ctx):
        if await self.db.get_linked_account_via_id(ctx.author.id) is None:
            await ctx.send(
                embed=discord.Embed(color=await self.bot.cc(), description="You don't have an account linked!\n"
                                                                           f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
            return

        await self.db.drop_linked_account(ctx.author.id)
        await ctx.send(
            embed=discord.Embed(color=await self.bot.cc(), description="You have unlinked your account successfully."))

    @commands.group(name="playerprofile", aliases=["profile", "h", "player", "p", "pp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def player_profile(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=await self.bot.cc(),
                                        description=f"You need to link your account to do this!\n"
                                                    f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        embed = discord.Embed(color=await self.bot.cc(), description=f"[`{p.UUID}`]")

        linked_acc = await self.db.get_linked_account_via_uuid(p.UUID)
        if linked_acc is not None: linked_acc = linked_acc[0]

        online = f"{self.bot.EMOJIS['offline_status']} offline"
        if p.LAST_LOGIN is not None and p.LAST_LOGOUT is not None:
            last_online = ["Last Online", arrow.Arrow.fromtimestamp(p.LAST_LOGOUT / 1000).humanize()]  # I love arrow
            if p.LAST_LOGIN > p.LAST_LOGOUT:
                online = f"{self.bot.EMOJIS['online_status']} online"
                last_online = ["Online Since", arrow.Arrow.fromtimestamp(
                    p.LAST_LOGIN / 1000).humanize()]  # bc this value is obtained from last_login
        else:
            last_online = "Never"

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

        monthly = p.MONTHLY_RANK
        if monthly is not None: monthly = monthly.replace("SUPERSTAR", "MVP_PLUS_PLUS")

        rank = monthly if monthly is not None else p.RANK

        if rank is None:
            if prefix != "":
                rank = prefix[1:len(prefix) - 2]
            else:
                rank = "None"
        else:
            if prefix == "" or "NONE" in prefix:
                prefix = f"[{rank}] ".replace("_", "").replace("PLUS", "+")

        if prefix.startswith("[NONE]"): prefix = ""

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

        embed.add_field(name="Achievement\nPoints",
                        value=f"{await self.cache.slothpixel_get_player_achievement_pts(p.DISPLAY_NAME)}")
        embed.add_field(name="Discord", value=self.bot.get_user(linked_acc) if linked_acc is not None else "Not Linked")
        embed.add_field(name="Friends", value=len([] if friends is None else friends))

        embed.set_footer(text="Made by Iapetus11 & TrustedMercury")

        await ctx.send(embed=embed)

    async def edit_show_online(self, msg, sent_users, page, max_pages, player_friends, stop, chonks, player, head):
        if not stop and len(chonks) > 3:
            embed = discord.Embed(color=await self.bot.cc(), description="Type ``more`` for more!")
        else:
            embed = discord.Embed(color=await self.bot.cc())

        embed.set_author(name=f"{player}'s friends ({len(player_friends)} total!)", icon_url=head)

        embed.set_footer(text=f"[Page {page}/{max_pages}]")

        for j in range(0, 3, 1):
            try:
                body = "\uFEFF"
                for i in range(0, len(sent_users), 1):
                    user = sent_users[0]
                    sent_users.pop(0)
                    p = None if " " in user else await self.cache.get_player(user)
                    online = self.bot.EMOJIS['offline_status']
                    if p is not None:
                        if p.LAST_LOGIN is not None and p.LAST_LOGOUT is not None:
                            if p.LAST_LOGIN > p.LAST_LOGOUT:
                                online = self.bot.EMOJIS['online_status']
                    body += f"{online} {discord.utils.escape_markdown(p.DISPLAY_NAME)}\n\n"
                embed.add_field(name="\uFEFF", value=body)  # "\n\n".join(sent_users)
            except IndexError:
                pass

        await msg.edit(embed=embed)

    @commands.command(name="friends", aliases=["pf", "pfriends", "playerfriends", "friendsof", "player_friends"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        puuid = await self.cache.get_player_uuid(player)

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"**{discord.utils.escape_markdown(player)}** doesn't have any friends! :cry:"))
            return

        if len(player_friends) > 1024:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"**{discord.utils.escape_markdown(player)}** has too many friends to show! :cry:"))
            return

        head = await self.cache.get_player_head(puuid)

        embed = discord.Embed(color=await self.bot.cc())
        embed.set_author(name=f"{player}'s friends ({len(player_friends)} total!)",
                         icon_url=head)

        premium = False if ctx.guild is None else await self.db.is_premium(ctx.guild.id)

        async with ctx.typing():
            names = []
            for f_uuid in player_friends:
                try:
                    names.append(await self.cache.get_player_name(f_uuid))
                except Exception:
                    names.append("[Invalid User]")

            chonks = [names[i:i + 10] for i in range(0, len(names), 10)]  # groups of 10 of the usernames

        try:
            stop = False
            page = 0
            max_pages = ceil(len(chonks) / 3)

            while True:
                page += 1

                if not stop and len(chonks) > 3:
                    embed = discord.Embed(color=await self.bot.cc(), description="Type ``more`` for more!")
                else:
                    embed = discord.Embed(color=await self.bot.cc())

                embed.set_author(
                    name=f"{player}'s friends ({len(player_friends)} total!)",
                    icon_url=head)

                embed.set_footer(text=f"[Page {page}/{max_pages}]")

                smol_chonks = []

                for i in range(0, 3, 1):
                    try:
                        smol_chonk = chonks.pop(0)
                        smol_chonks.extend(smol_chonk)
                        embed.add_field(name="\uFEFF",
                                        value=discord.utils.escape_markdown("\n\n".join(smol_chonk)))
                    except IndexError:
                        pass

                sent = await ctx.send(embed=embed)

                if premium:
                    await self.edit_show_online(sent, smol_chonks, page, max_pages, player_friends, stop, chonks,
                                                player, head)

                if stop or len(player_friends) < 31:
                    return

                if len(chonks) - 3 < 1:
                    stop = True

                def check(m):
                    return m.content in ["more", "next", "nextpage", "showmore"]

                await self.bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="playerguild", aliases=["pg", "playerg", "pguild", "guildofplayer", "player_guild"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_guild(self, ctx, player):
        await ctx.trigger_typing()

        player_guild = await self.cache.get_player_guild(player)

        if player_guild is None:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(),
                                               description=f"**{discord.utils.escape_markdown(player)}** isn't in a guild!"))
            return

        g = await self.cache.get_guild(player_guild)

        author = f"{discord.utils.escape_markdown(player)}'s Guild ({discord.utils.escape_markdown(g.NAME)})"

        desc = g.DESCRIPTION
        if desc is None:
            embed = discord.Embed(color=await self.bot.cc())
        else:
            length = len(author) + 2
            length = length if length > 30 else 30
            embed = discord.Embed(color=await self.bot.cc(),
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
