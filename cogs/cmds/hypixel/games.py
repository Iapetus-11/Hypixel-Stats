import aiopypixel
import arrow
import asyncio
import discord
from discord.ext import commands
from math import floor, ceil


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

        self.embed = discord.Embed(color=self.bot.cc)

    @commands.command(name="arcade", aliases=["hypixelarcade", "hypixel_arcade", "ak"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def arcade(self, ctx, *, player):
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arcade Stats", icon_url=await self.cache.get_player_head(p.UUID))

        arcade = p.STATS["Arcade"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Arena Stats", icon_url=await self.cache.get_player_head(p.UUID))

        arena = p.STATS["Arena"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Battleground Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        battle = p.STATS["Battleground"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Hungergames Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        hunger = p.STATS["HungerGames"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Paintball Stats", icon_url=await self.cache.get_player_head(p.UUID))

        paint = p.STATS["Paintball"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Quake Stats", icon_url=await self.cache.get_player_head(p.UUID))

        quake = p.STATS["Quake"]

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

    @commands.command(name="uhc", aliases=["ultrahc", "ultrahardcore", "uhardcore"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def uhc(self, ctx, *, player):
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s UHC Stats", icon_url=await self.cache.get_player_head(p.UUID))

        uhc = p.STATS["UHC"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s VampireZ Stats", icon_url=await self.cache.get_player_head(p.UUID))

        vampire = p.STATS["VampireZ"]

        embed.add_field(name="Coins", value=vampire.get("coins"), inline=False)

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Walls Stats", icon_url=await self.cache.get_player_head(p.UUID))

        walls = p.STATS["Walls"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Turbo Kart Racer Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        bread = p.STATS["GingerBread"]  # WHAT THE FUCK HYPIXEL DEVS

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Sky Wars Stats", icon_url=await self.cache.get_player_head(p.UUID))

        sky = p.STATS["SkyWars"]

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
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Speed UHC Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        suhc = p.STATS["SpeedUHC"]

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

        embed.add_field(name="Killstreak", value=suhc.get("killstreak"), inline=False)
        embed.add_field(name="Players Survived", value=suhc.get("survived_players"), inline=False)
        embed.add_field(name="Blocks Broken", value=suhc.get("blocks_broken"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="bedwars", aliases=["bed_wars", "bed", "bedw"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def bedwars(self, ctx, *, player):
        p = await self.cache.get_player(player)

        embed = self.embed.copy()

        embed.set_author(name=f"{p.DISPLAY_NAME}'s Bedwars Stats",
                         icon_url=await self.cache.get_player_head(p.UUID))

        bedwars = p.STATS["Bedwars"]

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


def setup(bot):
    bot.add_cog(Games(bot))
