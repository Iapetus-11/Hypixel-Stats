import aiopypixel
import arrow
import asyncio
import discord
from discord.ext import commands
from math import floor, ceil


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
        self.db = self.bot.get_cog("Database")

        self.embed = discord.Embed(color=self.bot.cc)

        self.games = [
            'arcade', 'arena', 'battleground', 'hungergames', 'paintball', 'quake', 'uhc', 'vampirez', 'walls',
            'turbokartracer', 'skywars', 'speeduhc', 'buildbattle', 'bedwars', 'truecombat', 'tntgames', 'supersmash',
            'murdermystery', 'copsandcrims', 'skyclash', 'duels', 'pit', "skyblock"
        ]

    @commands.command(name="stats", aliases=["playerstats", "pstats", "player_stats", "games", "gamestats"])
    async def player_stats(self, ctx, user=None):
        if user is not None:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"Each game has its own command! You have to do `{ctx.prefix}<stat> <player>`"))
            return
        embed = discord.Embed(color=self.bot.cc,
                              title=":chart_with_upwards_trend: Available Statistics :chart_with_downwards_trend:",
                              description=f"`{'`, `'.join(self.games)}`\n\nDo `{ctx.prefix}<stat> <player>` to view a certain stat!")
        embed.set_footer(text="Made by Iapetus11 & TrustedMercury")
        await ctx.send(embed=embed)

    @commands.command(name="arcade", aliases=["hypixelarcade", "hypixel_arcade", "ak"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def arcade(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            arcade = p.STATS["Arcade"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arcade Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="All Time Coins", value=floor(arcade.get("coins", 0)))
        embed.add_field(name="Coins This Month", value=arcade.get("monthly_coins_a", 0))
        embed.add_field(name="Coins This Week", value=arcade.get("weekly_coins_a", 0))

        await ctx.send(embed=embed)

    @commands.command(name="arena", aliases=["hypixelarena", "hypixel_arena", "ar"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def arena(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            arena = p.STATS["Arena"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arena Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=arena.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins Spent", value=arena.get("coins_spent", 0))

        kills = sum({k: v for k, v in arena.items() if "kills_" in k}.values())
        deaths = sum({k: v for k, v in arena.items() if "deaths_" in k}.values())
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        games = sum({k: v for k, v in arena.items() if "games_" in k}.values())
        wins = arena.get("wins", 0)
        losses = sum({k: v for k, v in arena.items() if "losses_" in k}.values())
        embed.add_field(name="Games", value=games)
        embed.add_field(name="Wins", value=wins)
        embed.add_field(name="Losses", value=losses)

        total_dmg = sum({k: v for k, v in arena.items() if "games_" in k}.values())
        embed.add_field(name="Total Damage", value=total_dmg)
        embed.add_field(name="Rating", value=round(arena.get("rating", 0), 2))

        await ctx.send(embed=embed)

    @commands.command(name="battleground", aliases=["battle ground", "battlegrounds", "battle_ground", "bg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def battleground(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            battle = p.STATS["Battleground"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Battleground Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=battle.get("coins", 0))
        embed.add_field(name="Wins", value=battle.get("wins", 0))
        embed.add_field(name="Losses", value=battle.get("losses", 0))

        kills = battle.get("kills", 0)
        deaths = battle.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Damage Inflicted", value=battle.get("damage", 0))
        embed.add_field(name="Damage Taken", value=battle.get("damage_taken", 0))
        embed.add_field(name="Life Leeched", value=battle.get("life_leeched", 0))

        await ctx.send(embed=embed)

    @commands.command(name="hungergames", aliases=["hungergame", "hunger_games", "hg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hunger_games(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            hunger = p.STATS["HungerGames"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Hungergames Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=hunger.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=hunger.get("wins", 0))

        kills = hunger.get("kills", 0)
        deaths = hunger.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        await ctx.send(embed=embed)

    @commands.command(name="paintball", aliases=["paint_ball", "pb"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def paintball(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            paint = p.STATS["Paintball"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Paintball Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=paint.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=paint.get("wins", 0))

        kills = paint.get("kills", 0)
        deaths = paint.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Shots Fired", value=paint.get("shots_fired", 0), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="quake", aliases=["qk"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def quake(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            quake = p.STATS["Quake"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Quake Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=quake.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Wins", value=quake.get("wins", 0))

        kills = quake.get("kills", 0)
        deaths = quake.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round(
            (kills + .00001) / (deaths + .00001), 2),
                        inline=True)

        embed.add_field(name="Shots Fired", value=quake.get("shots_fired", 0))
        embed.add_field(name="Headshots", value=quake.get("headshots", 0))

        embed.add_field(name="Highest Killstreak", value=quake.get("highest_killstreak", 0), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="uhc", aliases=["ultrahc", "ultrahardcore", "uhardcore"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def uhc(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            uhc = p.STATS["UHC"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s UHC Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=uhc.get("coins", 0))
        embed.add_field(name="Wins", value=uhc.get("wins", 0))
        embed.add_field(name="Score", value=uhc.get("score", 0))

        kills = uhc.get("kills", 0)
        deaths = uhc.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Heads Eaten", value=uhc.get("heads_eaten", 0), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="vampirez", aliases=["vampiresandzombies", "vz", "vampirezombies", "vampire_zombies"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def vampirez(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            vampire = p.STATS["VampireZ"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s VampireZ Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=vampire.get("coins", 0))
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name="Gold Bought", value=vampire.get("gold_bought", 0))

        human_kills = vampire.get("human_kills", 0)
        vampire_kills = vampire.get("vampire_kills", 0)
        zombie_kills = vampire.get("zombie_kills", 0)
        embed.add_field(name="Human Kills", value=human_kills)
        embed.add_field(name="Vampire Kills", value=vampire_kills)
        embed.add_field(name="Zombie Kills", value=zombie_kills)

        human_deaths = vampire.get("human_deaths", 0)
        vampire_deaths = vampire.get("vampire_deaths", 0)
        embed.add_field(name="Human Deaths", value=human_deaths)
        embed.add_field(name="Vampire Deaths", value=vampire_deaths)
        embed.add_field(name="Zombie Deaths", value="N/A")

        embed.add_field(name="Human KDR", value=round((human_kills + .00001) / (human_deaths + .00001), 2))
        embed.add_field(name="Vampire KDR", value=round((vampire_kills + .00001) / (vampire_deaths + .00001), 2))
        embed.add_field(name="Zombie KDR", value="N/A")

        await ctx.send(embed=embed)

    @commands.command(name="walls", aliases=["ww", "hypixel_walls"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def walls(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            walls = p.STATS["Walls"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Walls Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=walls.get("coins", 0))
        embed.add_field(name="Wins", value=walls.get("wins", 0))
        embed.add_field(name="Losses", value=walls.get("losses", 0))

        kills = walls.get("kills", 0)
        deaths = walls.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        await ctx.send(embed=embed)

    @commands.command(name="turbokartracer", aliases=["karts", "racing", "tkr", "tbkr", "turbokarts", "turboracer"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def turbo_kart_racer(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            bread = p.STATS["GingerBread"]  # WHAT THE FUCK HYPIXEL DEVS
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Turbo Kart Racer Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=bread.get("coins", 0))
        embed.add_field(name="Wins", value=bread.get("wins", 0))
        embed.add_field(name="Laps", value=bread.get("laps_completed", 0))

        embed.add_field(name="Gold Trophies", value=bread.get("gold_trophy", 0))
        embed.add_field(name="Silver Trophies", value=bread.get("silver_trophy", 0))
        embed.add_field(name="Bronze Trophies", value=bread.get("bronze_trophy", 0))

        embed.add_field(name="Boxes Picked Up", value=bread.get("box_pickups", 0))
        embed.add_field(name="Coins Picked Up", value=bread.get("coins_picked_up", 0))
        embed.add_field(name="Bananas Hit", value=bread.get("banana_hits_received", 0))

        await ctx.send(embed=embed)

    @commands.command(name="skywars", aliases=["skywar", "skw", "sw"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def skywars(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            sky = p.STATS["SkyWars"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Skywars Stats", icon_url=await self.cache.get_player_head(p.UUID))

        games = sky.get("games", 0)
        embed.add_field(name="Coins", value=sky.get("coins", 0))
        embed.add_field(name="Games", value=games)
        embed.add_field(name="Quits", value=sky.get("quits", 0))

        embed.add_field(name="Wins", value=sky.get("wins", 0))
        embed.add_field(name="Winstreak", value=sky.get("win_streak", 0))
        embed.add_field(name="Losses", value=sky.get("losses", 0))

        kills = sky.get("kills", 0)
        deaths = sky.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        bow_shots = sky.get("arrows_shot", 0)
        bow_hits = sky.get("arrows_hit", 0)
        embed.add_field(name="Bow Shots", value=bow_shots)
        embed.add_field(name="Bow Hits", value=bow_hits)
        embed.add_field(name="Accuracy",
                        value=f"{round((bow_hits + .00001) / (bow_shots + .00001), 2) * 100 * (0 if bow_shots == 0 else 1)}%")

        assists = sky.get("assists", 0)
        embed.add_field(name="Killstreak", value=sky.get("killstreak", 0))
        embed.add_field(name="Assists", value=assists)
        embed.add_field(name="Players Survived", value=sky.get("survived_players", 0))

        embed.add_field(name="Avg. Deaths\nper Game", value=round((deaths + .00001) / (games + .00001), 2))
        embed.add_field(name="Avg. Kills\nper Game", value=round((kills + .00001) / (games + .00001), 2))
        embed.add_field(name="Avg. Assists\nper Game", value=round((assists + .00001) / (games + .00001), 2))

        await ctx.send(embed=embed)

    @commands.command(name="speeduhc", aliases=["suhc", "speedultrahardcore", "succ"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def speed_uhc(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            suhc = p.STATS["SpeedUHC"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Speed UHC Stats", icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=suhc.get("coins", 0))
        embed.add_field(name="Games", value=suhc.get("games", 0))
        embed.add_field(name="Quits", value=suhc.get("quits", 0))

        embed.add_field(name="Wins", value=suhc.get("wins", 0))
        embed.add_field(name="Winstreak", value=suhc.get("win_streak", 0))
        embed.add_field(name="Losses", value=suhc.get("losses", 0))

        kills = suhc.get("kills", 0)
        deaths = suhc.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Killstreak", value=suhc.get("killstreak", 0))
        embed.add_field(name="Players Survived", value=suhc.get("survived_players", 0))

        embed.add_field(name="Blocks Broken", value=suhc.get("blocks_broken", 0), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="buildbattle", aliases=["buildbattles", "blingblingboy", "bb"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def build_battle(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            bb = p.STATS["BuildBattle"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Build Battle Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=bb.get("coins", 0))
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name="Score", value=bb.get("score", 0))

        embed.add_field(name="Games", value=bb.get("games_played", 0))
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name="Wins", value=bb.get("wins", 0))

        await ctx.send(embed=embed)

    @commands.command(name="bedwars", aliases=["bed_wars", "bed", "bedw", "bw"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def bedwars(self, ctx, player=None, _type=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            bedwars = p.STATS["Bedwars"]
        except KeyError:
            raise NoStatError

        if _type in ["1", "1s", "solos", "solo", "singles"]:
            type_clean = "SOLO"
            actual_type = "eight_one_"
        elif _type in ["2", "doubles", "2s", "double"]:
            type_clean = "DOUBLES"
            actual_type = "eight_two_"
        elif _type in ["3", "threes", "3s", "3x3x3x3"]:
            type_clean = "3x3x3x3"
            actual_type = "four_three_"
        elif _type in ["4", "fours", "4s", "4x4x4x4"]:
            type_clean = "4x4x4x4"
            actual_type = "four_four_"
        elif _type in ["5", "fourvsfour", "4v4", "2x4", "4x4"]:
            type_clean = "4x4"
            actual_type = "two_four_"
        else:
            type_clean = "ALL"
            actual_type = ""

        embed = self.embed.copy()

        embed.description = f"You can specify which gamemode by doing\n`{ctx.prefix}bedwars <player> <gamemode>`"

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Bedwars Stats ({type_clean})",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="XP", value=bedwars.get("Experience", 0))
        embed.add_field(name="Coins", value=bedwars.get("coins", 0))
        embed.add_field(name="Level", value=p.ACHIEVEMENTS.get("bedwars_level", 0))

        embed.add_field(name="Wins", value=bedwars.get(f"{actual_type}wins_bedwars", 0))
        embed.add_field(name="Losses", value=bedwars.get(f"{actual_type}beds_lost_bedwars", 0))
        embed.add_field(name="Winstreak", value=bedwars.get(f"{actual_type}winstreak", 0))

        kills = bedwars.get(f"{actual_type}kills_bedwars", 0)
        deaths = bedwars.get(f"{actual_type}deaths_bedwars", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        final_kills = bedwars.get(f"{actual_type}final_kills_bedwars", 0)
        final_deaths = bedwars.get(f"{actual_type}final_deaths_bedwars", 0)
        embed.add_field(name="Final Kills", value=final_kills)
        embed.add_field(name="Final Deaths", value=final_deaths)
        embed.add_field(name="Final KDR", value=round((final_kills + .00001) / (final_deaths + .00001), 2))

        beds_broken = bedwars.get(f"{actual_type}beds_broken_bedwars", 0)
        total_games = bedwars.get(f"{actual_type}wins_bedwars", 0) + bedwars.get(f"{actual_type}beds_lost_bedwars", 0)
        embed.add_field(name="Void Deaths", value=bedwars.get(f"{actual_type}void_deaths_bedwars", 0))
        embed.add_field(name="Beds Broken", value=beds_broken)
        embed.add_field(name="Total Games", value=total_games)

        embed.add_field(name="Avg. Final Kills\nper Game",
                        value=round((final_kills + 0.00001) / (total_games + 0.00001)))
        embed.add_field(name="Avg. Deaths\nper Game", value=round((deaths + 0.00001) / (total_games + 0.00001), 2))
        embed.add_field(name="Avg. Beds Broken\nper Game",
                        value=round((beds_broken + 0.00001) / (total_games + 0.00001), 2))

        await ctx.send(embed=embed)

    @commands.command(name="truecombat", aliases=["tc", "true_combat"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def true_combat(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            truecombat = p.STATS["TrueCombat"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s\nTrue Combat Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins", value=truecombat.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")

        await ctx.send(embed=embed)

    @commands.command(name="tntgames", aliases=["tntgame", "tnt", "tntg"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tnt_games(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            tntgames = p.STATS["TNTGames"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s TNT Games Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=tntgames.get("coins", 0))
        embed.add_field(name="Wins", value=tntgames.get("wins", 0))
        embed.add_field(name="Winstreak", value=tntgames.get("winstreak"))

        kills = sum({k: v for k, v in tntgames.items() if "kills" in k}.values())
        deaths = sum({k: v for k, v in tntgames.items() if "deaths" in k}.values())
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="TNT Run Record", value=tntgames.get("record_tntrun"))
        embed.add_field(name="PvP Run Record", value=tntgames.get("record_pvprun"))

        await ctx.send(embed=embed)

    @commands.command(name="supersmash", aliases=["supasmash", "super_smash", "ss"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def super_smash(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            supersmash = p.STATS["SuperSmash"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s\nSuper Smash Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Coins", value=supersmash.get("coins", 0))
        embed.add_field(name="\uFEFF", value=f"\uFEFF")

        await ctx.send(embed=embed)

    @commands.command(name="murdermystery", aliases=["murder_mystery", "mm"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def murder_mystery(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            mystery = p.STATS["MurderMystery"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Murder Mystery Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=mystery.get("coins", 0))
        embed.add_field(name="Games", value=mystery.get("games", 0))
        embed.add_field(name="Wins", value=mystery.get("wins", 0))

        kills = mystery.get("kills", 0)
        deaths = mystery.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Coins Picked Up", value=mystery.get("coins_pickedup", 0), inline=False)
        embed.add_field(name="Total Time Survived", value=f"{mystery.get('total_time_survived_seconds', 0)} seconds")

        await ctx.send(embed=embed)

    @commands.command(name="copsandcrims", aliases=["mcgo", "copsandcriminals", "copsnrobbers", "copsncrims"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def cops_and_criminals(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            mcgo = p.STATS["MCGO"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Cops & Crims Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=mcgo.get("coins", 0))
        embed.add_field(name="Wins", value=mcgo.get("game_wins", 0))
        embed.add_field(name="Round Wins", value=mcgo.get("round_wins", 0))

        kills = mcgo.get("kills", 0)
        deaths = mcgo.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Shots Fired", value=mcgo.get("shots_fired", 0))
        embed.add_field(name="Cop Kills", value=mcgo.get("cop_kills", 0))
        embed.add_field(name="Criminal Kills", value=mcgo.get("criminal_kills", 0))

        await ctx.send(embed=embed)

    @commands.command(name="skyclash", aliases=["skc", "sky_clash"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def sky_clash(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            clash = p.STATS["SkyClash"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Sky Clash Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Coins", value=clash.get("coins", 0))
        embed.add_field(name="Wins", value=clash.get("wins", 0))
        embed.add_field(name="Losses", value=clash.get("losses", 0))

        kills = clash.get("kills", 0)
        deaths = clash.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        embed.add_field(name="Kill Streak", value=clash.get("killstreak", 0))
        embed.add_field(name="Win Streak", value=clash.get("win_streak", 0))

        await ctx.send(embed=embed)

    @commands.command(name="duels", aliases=["hypixel_duels", "dd"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def duels(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            duels = p.STATS["Duels"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Duels Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        total_games = duels.get("wins", 0) + duels.get("losses", 0)
        embed.add_field(name="Games", value=total_games)
        embed.add_field(name="Wins", value=duels.get("wins", 0))
        embed.add_field(name="Losses", value=duels.get("losses", 0))

        kills = duels.get("kills", 0)
        deaths = duels.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        bow_shots = duels.get("bow_shots", 0)
        bow_hits = duels.get("bow_hits", 0)
        embed.add_field(name="Bow Shots", value=bow_shots)
        embed.add_field(name="Bow Hits", value=bow_shots)
        embed.add_field(name="Accuracy",
                        value=f"{round((bow_hits + .00001) / (bow_shots + .00001), 2) * 100 * (0 if bow_shots == 0 else 1)}%")

        melee_swings = duels.get("melee_swings", 0)
        melee_hits = duels.get("melee_hits", 0)
        embed.add_field(name="Melee Swings", value=melee_swings)
        embed.add_field(name="Melee Hits", value=melee_hits)
        embed.add_field(name="Accuracy",
                        value=f"{round((melee_hits + .00001) / (melee_swings + .00001), 2) * 100 * 0 if melee_swings == 0 else 1}%")

        embed.add_field(name="Avg. Kills\nper Game",
                        value=round((kills + 0.00001) / (total_games + 0.00001)))
        embed.add_field(name="Avg. Deaths\nper Game", value=round((deaths + 0.00001) / (total_games + 0.00001), 2))
        embed.add_field(name="Total Coins", value=duels.get("coins", 0))

        await ctx.send(embed=embed)

    @commands.command(name="pit", aliases=["hypixelpit", "hp", "hypixel_pit", "thepit"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hypixel_pit(self, ctx, player=None):
        await ctx.trigger_typing()

        if player is None:
            player = await self.db.get_linked_account_via_id(ctx.author.id)
            if player is not None:
                player = player[1]
            else:
                await ctx.send(
                    embed=discord.Embed(color=self.bot.cc, description=f"You need to link your account to do this!\n"
                                                                       f"Do `{ctx.prefix}link <mc_username>` to link your account!"))
                return

        p = await self.cache.get_player(player)

        try:
            armpit = p.STATS["Pit"]["pit_stats_ptl"]
        except KeyError:
            raise NoStatError

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Hypixel Pit Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        embed.add_field(name="Cash", value=armpit.get("cash_earned", 0))
        embed.add_field(name="Joins", value=armpit.get("joins", 0))
        embed.add_field(name="Playtime", value=f"{armpit.get('playtime_minutes', 0)} minutes")

        kills = armpit.get("kills", 0)
        deaths = armpit.get("deaths", 0)
        embed.add_field(name="Kills", value=kills)
        embed.add_field(name="Deaths", value=deaths)
        embed.add_field(name="KDR", value=round((kills + .00001) / (deaths + .00001), 2))

        bow_shots = armpit.get("arrows_fired", 0)
        bow_hits = armpit.get("arrow_hits", 0)
        embed.add_field(name="Bow Shots", value=bow_shots)
        embed.add_field(name="Bow Hits", value=bow_hits)
        embed.add_field(name="Accuracy",
                        value=f"{round((bow_hits + .00001) / (bow_shots + .00001), 2) * 100 * (0 if bow_shots == 0 else 1)}%")

        embed.add_field(name="Damage Dealt", value=armpit.get("damage_dealt", 0))
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name="Damage Received", value=armpit.get("damage_received", 0))

        embed.add_field(name="Blocks Placed", value=armpit.get("blocks_placed", 0))
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name="Max Killstreak", value=armpit.get("max_streak", 0))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
