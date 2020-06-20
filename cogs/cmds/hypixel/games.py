import aiopypixel
import arrow
import asyncio
import discord
import math
from discord.ext import commands
from math import floor, ceil
from typing import Any


class NoStatError(Exception):
    """Raised when a given player doesn't have a certain statistic"""

    def __init__(self):
        self.msg = "This user doesn't have that stat!"

    def __str__(self):
        return self.msg


class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

        self.embed = discord.Embed(color=self.bot.cc)

        self.games = [  # Don't forget to add sky block!
            'arcade', 'arena', 'battleground', 'hungergames', 'paintball', 'quake', 'uhc', 'vampirez', 'walls',
            'turbokartracer', 'skywars', 'speeduhc', 'buildbattle', 'bedwars', 'truecombat', 'tntgames', 'supersmash',
            'murdermystery', 'copsandcrims', 'skyclash', 'duels', 'pit'
        ]

    @commands.command(name="stats", aliases=["playerstats", "pstats", "player_stats"])
    async def player_stats(self, ctx):
        embed = discord.Embed(color=self.bot.cc,
                              title=":chart_with_upwards_trend: Available Statistics :chart_with_downwards_trend:",
                              description=f"`{'`, `'.join(self.games)}`\n\nDo `{ctx.prefix}<stat> <player>` to view a certain stat!")
        embed.set_footer(text="Made by Iapetus11 & TrustedMercury")
        await ctx.send(embed=embed)

    @commands.command(name="arcade", aliases=["hypixelarcade", "hypixel_arcade", "ak"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def arcade(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            arcade = p.STATS["Arcade"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arcade Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="All Time Coins", value=floor(arcade.get("coins")), inline=False)
        embed.add_field(name="Coins This Month",
                        value=arcade.get("monthly_coins_a"),
                        inline=False)
        embed.add_field(name="Coins This Week", value=arcade.get("weekly_coins_a"),
                        inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="arena", aliases=["hypixelarena", "hypixel_arena", "ar"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def arena(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            arena = p.STATS["Arena"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arena Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=arena.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins Spent", value=arena.get("coins_spent"), inline=True)

        kills = sum({k: v for k, v in arena.items() if "kills_" in k}.values())
        deaths = sum({k: v for k, v in arena.items() if "deaths_" in k}.values())
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        games = sum({k: v for k, v in arena.items() if "games_" in k}.values())
        wins = arena.get("wins")
        losses = sum({k: v for k, v in arena.items() if "losses_" in k}.values())
        embed.add_field(name="Games", value=games, inline=True)
        embed.add_field(name="Wins", value=wins if wins is not None else 0, inline=True)
        embed.add_field(name="Losses", value=losses, inline=True)

        total_dmg = sum({k: v for k, v in arena.items() if "games_" in k}.values())
        embed.add_field(name="Total Damage", value=total_dmg, inline=True)
        embed.add_field(name="Rating", value=round(arena.get("rating", 0), 2), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="battleground", aliases=["battle ground", "battlegrounds", "battle_ground", "bg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def battleground(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            battle = p.STATS["Battleground"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Battleground Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=battle.get("coins"), inline=True)
        embed.add_field(name="Wins", value=battle.get("wins"), inline=True)
        embed.add_field(name="Losses", value=battle.get("losses"), inline=True)

        kills = battle.get("kills", 0)
        deaths = battle.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Damage Inflicted", value=battle.get("damage"))
        embed.add_field(name="Damage Taken", value=battle.get("damage_taken"))
        embed.add_field(name="Life Leeched", value=battle.get("life_leeched"))

        await ctx.send(embed=embed)

    @commands.command(name="hungergames", aliases=["hungergame", "hunger_games", "hg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hunger_games(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            hunger = p.STATS["HungerGames"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Hungergames Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=hunger.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=hunger.get("wins"), inline=True)

        kills = hunger.get("kills", 0)
        deaths = hunger.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="paintball", aliases=["paint_ball", "pb"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def paintball(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            paint = p.STATS["Paintball"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Paintball Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=paint.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=paint.get("wins"), inline=True)

        kills = paint.get("kills", 0)
        deaths = paint.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Shots Fired", value=paint.get("shots_fired"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="quake", aliases=["qk"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def quake(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            quake = p.STATS["Quake"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Quake Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=quake.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=quake.get("wins"), inline=True)

        kills = quake.get("kills", 0)
        deaths = quake.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Shots Fired", value=quake.get("shots_fired"), inline=True)
        embed.add_field(name="Headshots", value=quake.get("headshots"), inline=True)

        embed.add_field(name="Highest Killstreak", value=quake.get("highest_killstreak"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="skyblock", aliases=["sb"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def skyblock(self, ctx, *, player):
        """command to display skyblock stats of the mentioned player"""

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

        for profile in profiles:
            profile_names += f'``{profiles.index(profile) + 1}.`` **{skyblock["profiles"][profile].get("cute_name")}** ' \
                             f'``({skyblock["profiles"][profile].get("profile_id")})``\n'
        picker_embed = discord.Embed(color=self.bot.cc, description=profile_names)
        picker_embed.set_author(name=f"{p.DISPLAY_NAME}'s SkyBlock Islands:", icon_url=head)
        picker_embed.set_footer(text="Just send one of the above numbers!")
        await ctx.send(embed=picker_embed)

        index = await self.bot.wait_for('message', check=author_check, timeout=20)

        try:
            index = int(index.content)
        except ValueError:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That's not a valid index!"))
            return

        if int(index) > len(profiles) or int(index) <= 0:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That's not a valid index!"))
            return

        profile = skyblock['profiles'][profiles[index]]["profile_id"]

        await ctx.send(profile)

        stats = await self.cache.get_skyblock_stats(profile)

        if stats["profile_id"] == profile:
            coop = True
        else:
            coop = False

        members = []

        for member in stats.get('members', []).keys():
            if member == profile:
                members.append(f"**{self.cache.get_player_name(member)}**")
            else:
                members.append(self.cache.get_player_name(member))

        user_stats = stats["members"].get(p.UUID)

        firstJoin = user_stats.get("first_join")
        kills = user_stats['stats'].get('kills')
        deaths = user_stats.get('deaths')
        voidDeaths = user_stats['stats'].get('deaths_void')
        coinPurse = ceil(user_stats.get('coin_purse'))
        lastDeath = user_stats.get('last_death')
        fairySouls = user_stats.get('fairy_souls')
        fairySoulsCollected = user_stats.get('fairy_souls_collected')

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Skyblock Stats", icon_url=head)

        embed.description = f'**Skyblock - {skyblock["profiles"][profiles[index]].get("cute_name")}** - ``{profile}``'

        embed.add_field(name="Co-Op",
                        value=coop)
        embed.add_field(name="Members",
                        value=', '.join(members))
        embed.add_field(name="First Join",
                        value=f"{firstJoin}")
        embed.add_field(name="Coin Purse",
                        value=f"{coinPurse}")
        embed.add_field(name="Kills",
                        value=f"{kills}")
        embed.add_field(name="Deaths",
                        value=f"{deaths}{f' | {voidDeaths}' if voidDeaths else ''}")
        embed.add_field(name="Fairy Souls",
                        value=f"{fairySouls}")
        embed.add_field(name="Fairy Souls Collected",
                        value=f"{fairySoulsCollected}")
        embed.add_field(name="Last Death",
                        value=f"{lastDeath}")

        await ctx.send(embed)

    @commands.command(name="uhc", aliases=["ultrahc", "ultrahardcore", "uhardcore"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def uhc(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            uhc = p.STATS["UHC"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s UHC Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=uhc.get("coins"), inline=True)
        embed.add_field(name="Wins", value=uhc.get("wins"), inline=True)
        embed.add_field(name="Score", value=uhc.get("score"), inline=True)

        kills = uhc.get("kills", 0)
        deaths = uhc.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Heads Eaten", value=uhc.get("heads_eaten"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="vampirez", aliases=["vampiresandzombies", "vz", "vampirezombies", "vampire_zombies"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def vampirez(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            vampire = p.STATS["VampireZ"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s VampireZ Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=vampire.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(nname="Gold Bought", value=vampire.get("gold_bought"), inline=True)

        human_kills = vampire.get("human_kills", 0)
        vampire_kills = vampire.get("vampire_kills", 0)
        zombie_kills = vampire.get("zombie_kills", 0)
        embed.add_field(name="Human Kills", value=human_kills, inline=True)
        embed.add_field(name="Vampire Kills", value=vampire_kills, inline=True)
        embed.add_field(name="Zombie Kills", value=zombie_kills, inline=True)

        human_deaths = vampire.get("human_deaths", 0)
        vampire_deaths = vampire.get("vampire_deaths", 0)
        embed.add_field(name="Human Deaths", value=human_deaths, inline=True)
        embed.add_field(name="Vampire Deaths", value=vampire_deaths, inline=True)
        embed.add_field(name="Zombie Deaths", value="N/A", inline=True)

        embed.add_field(name="Human KDR", value=round((human_kills + .00001) / (human_deaths + .00001), 2),
                        inline=True)
        embed.add_field(name="Vampire KDR", value=round((vampire_kills + .00001) / (vampire_deaths + .00001), 2),
                        inline=True)
        embed.add_field(name="Zombie KDR", value="N/A", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="walls", aliases=["ww", "hypixel_walls"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def walls(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            walls = p.STATS["Walls"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Walls Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=walls.get("coins"), inline=True)
        embed.add_field(name="Wins", value=walls.get("wins"), inline=True)
        embed.add_field(name="Losses", value=walls.get("losses"), inline=True)

        kills = walls.get("kills", 0)
        deaths = walls.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="turbokartracer", aliases=["karts", "racing", "tkr", "tbkr", "turbokarts", "turboracer"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def turbo_kart_racer(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            bread = p.STATS["GingerBread"]  # WHAT THE FUCK HYPIXEL DEVS
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Turbo Kart Racer Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=bread.get("coins"), inline=True)
        embed.add_field(name="Wins", value=bread.get("wins"), inline=True)
        embed.add_field(name="Laps", value=bread.get("laps_completed"), inline=True)

        embed.add_field(name="Gold Trophies", value=bread.get("gold_trophy"), inline=True)
        embed.add_field(name="Silver Trophies", value=bread.get("silver_trophy"), inline=True)
        embed.add_field(name="Bronze Trophies", value=bread.get("bronze_trophy"), inline=True)

        embed.add_field(name="Boxes Picked Up", value=bread.get("box_pickups"), inline=True)
        embed.add_field(name="Coins Picked Up", value=bread.get("coins_picked_up"), inline=True)
        embed.add_field(name="Bananas Hit", value=bread.get("banana_hits_received"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="skywars", aliases=["skywar", "skw"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def skywars(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            sky = p.STATS["SkyWars"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Sky Wars Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=sky.get("coins"), inline=True)
        embed.add_field(name="Games", value=sky.get("games"), inline=True)
        embed.add_field(name="Quits", value=sky.get("quits"), inline=True)

        embed.add_field(name="Wins", value=sky.get("wins"), inline=True)
        embed.add_field(name="Winstreak", value=sky.get("win_streak"), inline=True)
        embed.add_field(name="Losses", value=sky.get("losses"), inline=True)

        kills = sky.get("kills", 0)
        deaths = sky.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Bow Shots", value=sky.get("arrows_shot"), inline=True)
        embed.add_field(name="Bow Hits", value=sky.get("arrows_hit"), inline=True)

        embed.add_field(name="Eggs Thrown", value=sky.get("egg_thrown"), inline=False)

        embed.add_field(name="Killstreak", value=sky.get("killstreak"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="speeduhc", aliases=["suhc", "speedultrahardcore", "succ"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def speed_uhc(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            suhc = p.STATS["SpeedUHC"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Speed UHC Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=suhc.get("coins"), inline=True)
        embed.add_field(name="Games", value=suhc.get("games"), inline=True)
        embed.add_field(name="Quits", value=suhc.get("quits"), inline=True)

        embed.add_field(name="Wins", value=suhc.get("wins"), inline=True)
        embed.add_field(name="Winstreak", value=suhc.get("win_streak"), inline=True)
        embed.add_field(name="Losses", value=suhc.get("losses"), inline=True)

        kills = suhc.get("kills", 0)
        deaths = suhc.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Killstreak", value=suhc.get("killstreak"), inline=True)
        embed.add_field(name="Players Survived", value=suhc.get("survived_players"), inline=True)
        embed.add_field(name="Blocks Broken", value=suhc.get("blocks_broken"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="buildbattle", aliases=["buildbattles", "blingblingboy", "bb"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def build_battle(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            bb = p.STATS["BuildBattle"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Build Battle Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=bb.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(name="Score", value=bb.get("score"), inline=True)

        embed.add_field(name="Games", value=bb.get("games_played"), inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(name="Wins", value=bb.get("wins"), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="bedwars", aliases=["bed_wars", "bed", "bedw", "bw"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def bedwars(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            bedwars = p.STATS["Bedwars"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Bedwars Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="XP", value=bedwars.get("Experience"))
        embed.add_field(name="Coins", value=bedwars.get("coins"))
        embed.add_field(name="Stars", value=p.ACHIEVEMENTS.get("bedwars_level"), inline=True)

        embed.add_field(name="Losses", value=bedwars.get("beds_lost_bedwars"))
        embed.add_field(name="Wins", value=bedwars.get("wins_bedwars"))
        embed.add_field(name="Winstreak", value=bedwars.get("winstreak"))

        kills = bedwars.get("kills_bedwars", 0)
        deaths = bedwars.get("deaths_bedwars", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Beds Broken", value=bedwars.get("beds_broken_bedwars"), inline=True)
        embed.add_field(name="Total Games",
                        value=sum({k: v for k, v in bedwars.items() if "games_played" in k}.values()))

        await ctx.send(embed=embed)

    @commands.command(name="truecombat", aliases=["tc", "true_combat"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def true_combat(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            truecombat = p.STATS["TrueCombat"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s\nTrue Combat Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins", value=truecombat.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")

        await ctx.send(embed=embed)

    @commands.command(name="tntgames", aliases=["tntgame", "tnt", "tntg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tnt_games(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            tntgames = p.STATS["TNTGames"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s TNT Games Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=tntgames.get("coins"))
        embed.add_field(name="Wins", value=tntgames.get("wins"))
        embed.add_field(name="Winstreak", value=tntgames.get("winstreak"))

        kills = sum({k: v for k, v in tntgames.items() if "kills" in k}.values())
        deaths = sum({k: v for k, v in tntgames.items() if "deaths" in k}.values())
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="TNT Run Record", value=tntgames.get("record_tntrun"), inline=True)
        embed.add_field(name="PvP Run Record", value=tntgames.get("record_pvprun"), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="supersmash", aliases=["supasmash", "super_smash", "ss"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def super_smash(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            supersmash = p.STATS["SuperSmash"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s\nSuper Smash Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins", value=supersmash.get("coins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")

        await ctx.send(embed=embed)

    @commands.command(name="murdermystery", aliases=["murder_mystery", "mm"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def murder_mystery(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            mystery = p.STATS["MurderMystery"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Murder Mystery Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=mystery.get("coins"), inline=True)
        embed.add_field(name="Deaths", value=mystery.get("deaths", 0), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF", inline=True)

        embed.add_field(name="Games", value=mystery.get("games"), inline=True)
        embed.add_field(name="Wins", value=mystery.get("wins"), inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF", inline=True)

        embed.add_field(name="Coins Picked Up", value=mystery.get("coins_pickedup"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="copsandcrims", aliases=["mcgo", "copsandcriminals", "copsnrobbers", "copsncrims"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def cops_and_criminals(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            mcgo = p.STATS["MCGO"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Cops & Crims Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=mcgo.get("coins"), inline=True)
        embed.add_field(name="Wins", value=mcgo.get("game_wins"), inline=True)
        embed.add_field(name="Round Wins", value=mcgo.get("round_wins"), inline=True)

        kills = mcgo.get("kills", 0)
        deaths = mcgo.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Shots Fired", value=mcgo.get("shots_fired"), inline=False)
        embed.add_field(name="Cop Kills", value=mcgo.get("cop_kills"), inline=False)
        embed.add_field(name="Criminal Kills", value=mcgo.get("criminal_kills"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="skyclash", aliases=["skc", "sky_clash"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def sky_clash(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            clash = p.STATS["SkyClash"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Sky Clash Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=clash.get("coins"), inline=True)
        embed.add_field(name="Wins", value=clash.get("wins"), inline=True)
        embed.add_field(name="Losses", value=clash.get("losses"), inline=True)

        kills = clash.get("kills", 0)
        deaths = clash.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Kill Streak", value=clash.get("killstreak"), inline=True)
        embed.add_field(name="Win Streak", value=clash.get("win_streak"), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="duels", aliases=["hypixel_duels", "dd"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def duels(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            duels = p.STATS["Duels"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Duels Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Games", value=duels.get("wins", 0) + duels.get("losses", 0), inline=True)
        embed.add_field(name="Wins", value=duels.get("wins"), inline=True)
        embed.add_field(name="Losses", value=duels.get("losses"), inline=True)

        kills = duels.get("kills", 0)
        deaths = duels.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        bow_shots = duels.get("bow_shots", 0)
        bow_hits = duels.get("bow_hits", 0)
        embed.add_field(name="Bow Shots", value=bow_shots, inline=True)
        embed.add_field(name="Bow Hits", value=bow_shots, inline=True)
        embed.add_field(name="Accuracy", value=f"{round((bow_hits + .00001) / (bow_shots + .00001), 2) * 100}%")

        melee_swings = duels.get("melee_swings", 0)
        melee_hits = duels.get("melee_hits", 0)
        embed.add_field(name="Melee Swings", value=melee_swings, inline=True)
        embed.add_field(name="Melee Hits", value=melee_hits, inline=True)
        embed.add_field(name="Accuracy",
                        value=f"{round((melee_hits + .00001) / (melee_swings + .00001), 2) * 100}%")
        
        embed.add_field(name="Total Coins", value=duels.get("coins"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="pit", aliases=["hypixelpit", "hp", "hypixel_pit", "thepit"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hypixel_pit(self, ctx, *, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        try:
            armpit = p.STATS["Pit"]["pit_stats_ptl"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Hypixel Pit Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Cash", value=armpit.get("cash_earned"), inline=True)
        embed.add_field(name="Joins", value=armpit.get("joins"), inline=True)
        embed.add_field(name="Playtime", value=f"{armpit.get('playtime_minutes')} minutes")

        kills = armpit.get("kills", 0)
        deaths = armpit.get("deaths", 0)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Deaths", value=deaths, inline=True)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        bow_shots = armpit.get("arrows_fired", 0)
        bow_hits = armpit.get("arrow_hits", 0)
        embed.add_field(name="Bow Shots", value=bow_shots, inline=True)
        embed.add_field(name="Bow Hits", value=bow_hits, inline=True)
        embed.add_field(name="Accuracy", value=f"{round((bow_hits + .00001) / (bow_shots + .00001), 2) * 100}%")

        embed.add_field(name="Damage Dealt", value=armpit.get("damage_dealt"), inline=True)
        embed.add_field(name="Damage Received", value=armpit.get("damage_received"), inline=True)

        embed.add_field(name="Blocks Placed", value=armpit.get("blocks_placed"), inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
