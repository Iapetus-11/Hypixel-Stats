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

        self.games_to_ignore = ["Walls3", "Legacy", "SkyBlock", "Housing"]

    @commands.group(name="playerprofile", aliases=["profile", "pp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_profile(self, ctx, player):
        await ctx.trigger_typing()

        embed = discord.Embed(color=self.bot.cc)

        p = await self.cache.get_player(player)

        online = f"{self.bot.EMOJIS['offline_status']} offline"
        last_online = arrow.Arrow.fromtimestamp(p.LAST_LOGIN / 1000).humanize()  # I love arrow
        if p.LAST_LOGIN is None or p.LAST_LOGOUT is None:
            online = "N/A"
            last_online = "N/A"
        elif p.LAST_LOGIN > p.LAST_LOGOUT:
            online = f"{self.bot.EMOJIS['online_status']} online"
            last_online = "now"  # bc this value is obtained from last_login

        player_pfp = await self.cache.get_player_head(p.UUID)

        player_guild = p.GUILD
        if player_guild is None:
            player_guild = "none"
        else:
            player_guild = await self.cache.get_guild_name_from_id(p.GUILD)

        embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Profile", icon_url=player_pfp)
        embed.add_field(name="Status", value=online)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Last Online", value=f"{last_online}")
        embed.add_field(name="XP", value=f"{p.EXP}", inline=True)
        embed.add_field(name="\uFEFF", value=f"\uFEFF")
        embed.add_field(name="Level",
                        value=f"{await self.cache.hypixel.calcPlayerLevel(p.EXP if p.EXP is not None else 0)}",
                        inline=True)
        embed.add_field(name="Achievements", value=f"{len(p.ONE_TIME_ACHIEVEMENTS)}", inline=False)
        embed.add_field(name="Guild", value=f"{player_guild}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="playerstats", aliases=["pstats", "ps", "player_stats", "stats"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_stats(self, ctx, player):
        await ctx.trigger_typing()

        p = await self.cache.get_player(player)

        for game in self.games_to_ignore:
            if game in p.STATS:
                p.STATS.pop(game)

        proper_spellings = {
            "HungerGames": "Hunger Games", "TNTGames": "TNT Games", "SkyWars": "Sky Wars",
            "TrueCombat": "True Combat", "SuperSmash": "Super Smash", "SpeedUHC": "Speed UHC",
            "SkyClash": "Sky Clash", "MurderMystery": "Murder Mystery", "BuildBattle": "Build Battle",
            "SkyBlock": "Sky Block", "GingerBread": "Turbo Kart Racer"
        }

        games = []

        for game in list(p.STATS):
            games.append(proper_spellings.get(game, game))

        await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                           description=f"Available stats for this player (send which one you want): ``{', '.join(games)}``"))

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            stat = await self.bot.wait_for("message", check=check, timeout=20)
            stat = stat.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description=self.bot.timeout_message))
            return

        if stat not in [s.lower() for s in games]:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)} doesn't have stats for that game!"))
            return

        embed = discord.Embed(color=self.bot.cc)

        if stat == "arcade":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Arcade Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            arcade = p.STATS["Arcade"]

            embed.add_field(name="All Time Coins", value=floor(arcade.get("coins")), inline=False)
            embed.add_field(name="Coins This Month",
                            value=arcade.get("monthly_coins_a"),
                            inline=False)
            embed.add_field(name="Coins This Week", value=arcade.get("weekly_coins_a"),
                            inline=False)
            await ctx.send(embed=embed)
        elif stat == "arena":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Arena Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
            embed.add_field(name="Rating", value=round(arena.get("rating"), 2), inline=True)
            await ctx.send(embed=embed)
        elif stat in ["battleground", "battlegrounds", "battle ground"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Battleground Stats",
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
        elif stat in ["hungergames", "hunger games", "hungergame", "hunger game"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Hungergames Stats",
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
        elif stat in ["paintball", "paint ball"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Paintball Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat == "quake":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Quake Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat in ["uhc", "ultrahc", "hardcore", "ultrahardcore", "hard core", "ultra hard core"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s UHC Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat in ["vampirez", "vampire z", "vampire and zombies", "vampirezombie"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s VampireZ Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat == "walls":
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Walls Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat in ["karts", "go karts", "tkr", "turbo kart racer", "turbo karts", "turbo kart", "turbo kart racers"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Turbo Kart Racer Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            bread = p.STATS["GingerBread"]

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
        elif stat in ["skywars", "sky wars", "sky war"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Sky Wars Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

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
        elif stat in ["speeduhc", "suhc", "speed uhc"]:
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
        elif stat in ["build battle", "buildbattle", "builds", "build battles"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Build Battle Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            bb = p.STATS["BuildBattle"]

            embed.add_field(name="Coins", value=bb.get("coins"), inline=True)
            embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
            embed.add_field(name="Score", value=bb.get("score"), inline=True)

            embed.add_field(name="Games", value=bb.get("games_played"), inline=True)
            embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
            embed.add_field(name="Wins", value=bb.get("wins"), inline=True)

            await ctx.send(embed=embed)
        elif stat in ["bedwars", "bed wars", "bedwar"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Bedwars Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            bedwars = p.STATS["Bedwars"]

            embed.add_field(name="XP", value=bedwars.get("Experience"))
            embed.add_field(name="Coins", value=bedwars.get("coins"))
            embed.add_field(name="Total Games",
                            value=sum({k: v for k, v in bedwars.items() if "games_played" in k}.values()))

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

            embed.add_field(name="Beds Broken", value=bedwars.get("beds_broken_bedwars"))
            await ctx.send(embed=embed)
        elif stat in ["truecombat", "true combat"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s\nTrue Combat Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            truecombat = p.STATS["TrueCombat"]

            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            embed.add_field(name="Coins", value=truecombat.get("coins"), inline=True)
            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            await ctx.send(embed=embed)
        elif stat in ["tntgames", "tnt games", "tnt game"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s TNT Games Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            tntgames = p.STATS["TNTGames"]

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
        elif stat in ["supersmash", "super smash"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s\nSuper Smash Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            supersmash = p.STATS["SuperSmash"]

            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            embed.add_field(name="Coins", value=supersmash.get("coins"), inline=True)
            embed.add_field(name="\uFEFF", value=f"\uFEFF")
            await ctx.send(embed=embed)
        elif stat in ["murdermystery", "murder mystery"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Murder Mystery Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            mystery = p.STATS["MurderMystery"]

            embed.add_field(name="Coins", value=mystery.get("coins"), inline=True)
            embed.add_field(name="Deaths", value=mystery.get("deaths", 0), inline=True)
            embed.add_field(name="\uFEFF", value=f"\uFEFF", inline=True)

            embed.add_field(name="Games", value=mystery.get("games"), inline=True)
            embed.add_field(name="Wins", value=mystery.get("wins"), inline=True)
            embed.add_field(name="\uFEFF", value=f"\uFEFF", inline=True)

            embed.add_field(name="Coins Picked Up", value=mystery.get("coins_pickedup"), inline=False)
            await ctx.send(embed=embed)
        elif stat in ["mcgo", "mc go", "cops and crims", "cops and criminals", "cops and robbers", "cops & crims",
                      "cops & criminals"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Cops & Crims Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            mcgo = p.STATS["MCGO"]

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
        elif stat in ["skyclash", "sky clash"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Sky Clash Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            clash = p.STATS["SkyClash"]

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
        elif stat in ["duels", "fights"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Duels Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            duels = p.STATS["Duels"]

            embed.add_field(name="Coins", value=duels.get("coins"), inline=False)

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

            melee_swings = duels.get("melee_swings")
            melee_hits = duels.get("melee_hits")
            embed.add_field(name="Melee Swings", value=melee_swings, inline=True)
            embed.add_field(name="Melee Hits", value=melee_hits, inline=True)
            embed.add_field(name="Accuracy",
                            value=f"{round((melee_hits + .00001) / (melee_swings + .00001), 2) * 100}%")

            await ctx.send(embed=embed)
        elif stat in ["pit", "hypixel pit", "the pit"]:
            embed.set_author(name=f"{discord.utils.escape_markdown(p.DISPLAY_NAME)}'s Hypixel Pit Stats",
                             icon_url=await self.cache.get_player_head(p.UUID))

            armpit = p.STATS["Pit"]["pit_stats_ptl"]

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
        else:
            embed.set_author(
                name=f"SH\*\*! Something went seriously wrong while sending {discord.utils.escape_markdown(p.DISPLAY_NAME)}'s stats, please report this!",
                icon_url=await self.cache.get_player_head(p.UUID))
            await ctx.send(embed=embed)

    @commands.command(name="friends", aliases=["pf", "pfriends", "playerfriends", "friendsof", "player_friends"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        await ctx.trigger_typing()

        puuid = await self.cache.get_player_uuid(player)

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** doesn't have any friends! :cry:"))
            return

        embed = discord.Embed(color=self.bot.cc)

        embed.set_author(name=f"{discord.utils.escape_markdown(player)}'s friends ({len(player_friends)} total!)",
                         icon_url=await self.cache.get_player_head(puuid))

        body = ""
        count = 0
        embed_count = 0
        for friend in player_friends:
            try:
                name = await self.cache.get_player_name(friend)
            except aiopypixel.exceptions.exceptions.InvalidPlayerError:
                name = "Unknown User"
            body += f"{discord.utils.escape_markdown(name)}\n\n"
            if count > 20:
                embed.add_field(name="\uFEFF", value=body)
                embed_count += 1
                count = 0
                body = ""
            count += 1
        if body != "":
            embed.add_field(name="\uFEFF", value=body)
            embed_count += 1

        if len(embed) > 5095 or embed_count > 35:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"{discord.utils.escape_markdown(player)} has too many friends to show!"))
            return

        await ctx.send(embed=embed)

    @commands.command(name="test_friends")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def test_player_friends(self, ctx, player):
        await ctx.trigger_typing()

        puuid = await self.cache.get_player_uuid(player)

        player_friends = await self.cache.get_player_friends(player)
        if not player_friends:
            await ctx.send(embed=discord.Embed(color=self.bot.cc,
                                               description=f"**{discord.utils.escape_markdown(player)}** doesn't have any friends! :cry:"))
            return

        embed = discord.Embed(color=self.bot.cc)
        embed.set_author(name=f"{discord.utils.escape_markdown(player)}'s friends ({len(player_friends)} total!)",
                         icon_url=await self.cache.get_player_head(puuid))

        chonks = [player_friends[i:i + 15] for i in range(0, len(player_friends), 15)]

        if len(chonks) <= 3:
            for chonk in chonks:
                embed.add_field(name="\uFEFF", value=discord.utils.escape_markdown(
                    "\n\n".join([await self.cache.get_player_name(pp) for pp in chonk])))

            await ctx.send(embed=embed)
        else:
            try:
                offset = 0
                e = None
                while offset < len(chonks):
                    embed = discord.Embed(color=self.bot.cc, description="Type ``more`` to see more!")

                    embed.set_author(
                        name=f"{discord.utils.escape_markdown(player)}'s friends ({len(player_friends)} total!)",
                        icon_url=await self.cache.get_player_head(puuid))

                    await ctx.send(len(chonks))

                    await ctx.send(f"DEBUG: {len(chonks[offset:offset + 3])}")

                    for chonk in chonks[offset:offset + 3]:
                        embed.add_field(name="\uFEFF", value=discord.utils.escape_markdown(
                            "\n\n".join([await self.cache.get_player_name(pp) for pp in chonk])))

                    if e is None:
                        e = await ctx.send(embed=embed)
                    else:
                        await e.edit(embed=embed)

                    def czech(m):
                        return m.author.id == ctx.author.id and m.content == "more"

                    await self.bot.wait_for("message", check=czech, timeout=20)
                    offset += 3
                await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That's all of em!"))
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
