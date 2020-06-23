import aiohttp
import aiopypixel
import asyncio
import discord
from discord.ext import commands


class InvalidDiscordUser(Exception):
    def __init__(self):
        self.msg = "Invalid Discord user was supplied."

    def __str__(self):
        return self.msg


class Cache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

        self.hypixel = aiopypixel.Client(self.bot.hypixel_key)

        self.session = aiohttp.ClientSession()

        self.waiting = 0

        self.valid_names_and_uuids = []
        self.name_uuid_cache = {}  # {name: uuid}
        self.uuid_name_cache = {}  # {uuid: name}
        self.player_friends_cache = {}  # {uuid: [friends...]}
        self.player_guild_cache = {}  # {uuid: guild}
        self.guild_id_name_cache = {}  # {id: name or name: id}
        self.player_object_cache = {}  # {uuid: Player}
        self.guild_cache = {}  # {id: Guild}
        self.armor_cache = {}  # {uuid: armor_str}
        self.skyblock_cache = {}  # {profile_str: data}
        self.watchdog_cached = None

        self.stop_loops = False

        self.bot.loop.create_task(self.reset_continuous())
        self.bot.loop.create_task(self.reset_10_minutes())
        self.bot.loop.create_task(self.reset_1_hour())
        self.bot.loop.create_task(self.reset_2_hours())
        self.bot.loop.create_task(self.reset_6_hours())

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

        self.stop_loops = True

    async def reset_continuous(self):
        while True:
            await asyncio.sleep(.5)
            while len(self.valid_names_and_uuids) > len(self.bot.guilds) * 3:  # reset valid names + uuids
                self.valid_names_and_uuids.pop(0)

    async def reset_10_minutes(self):
        while True:
            for i in range(0, 60 * 10, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return

            self.player_object_cache = {}

    async def reset_1_hour(self):
        while True:
            for i in range(0, 60 * 60, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return

            self.player_guild_cache = {}
            self.armor_cache = {}
            self.watchdog_cached = None
            self.skyblock_cache = {}

    async def reset_2_hours(self):
        while True:
            for i in range(0, 60 * 60 * 2, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return

            self.player_friends_cache = {}
            self.guild_cache = {}
            self.guild_id_name_cache = {}

    async def reset_6_hours(self):
        while True:
            for i in range(0, 60 * 60 * 6, 1):
                await asyncio.sleep(1)
                if self.stop_loops:
                    return

            self.name_uuid_cache = {}
            self.uuid_name_cache = {}

    @commands.command(name="clearcache", aliases=["resetcache"])
    async def clearcache(self, ctx):
        self.waiting = 0
        self.valid_names_and_uuids = []
        self.name_uuid_cache = {}
        self.uuid_name_cache = {}
        self.player_friends_cache = {}
        self.player_guild_cache = {}
        self.guild_id_name_cache = {}
        self.player_object_cache = {}
        self.guild_cache = {}
        self.armor_cache = {}
        self.skyblock_cache = {}
        self.watchdog_cached = None
        await ctx.send(embed=discord.Embed(color=self.bot.cc, description="Reset the all caches."))

    async def get_player_uuid(self, player):
        """Fetches a player's uuid via their username"""

        if discord.utils.escape_mentions(player).startswith("<@​!"):
            try:
                uuid = await self.db.get_linked_account_via_id(int(player[3:-1]))
            except ValueError:
                raise InvalidDiscordUser
            if uuid is None:
                raise InvalidDiscordUser
            return uuid[1]

        if len(player) > 16:
            if player in self.valid_names_and_uuids:
                return player

        # By this point, player must be a username
        uuid = self.name_uuid_cache.get(player)

        if uuid is None:
            uuid = await self.hypixel.usernameToUUID(player)
            self.name_uuid_cache[player] = uuid

        if uuid not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(uuid)
        return uuid

    async def get_player_name(self, player):
        """Fetches a player's username via their mc uuid"""

        if len(player) <= 16:
            if player in self.valid_names_and_uuids:
                return player

        # By this point, player is a uuid
        name = self.uuid_name_cache.get(player)

        if name is None:
            name = await self.hypixel.UUIDToUsername(player)
            self.uuid_name_cache[player] = name.lower()

        if name not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(name.lower())

        return name

    async def rate_limit_wait(self, to_be_awaited):
        """Gets something from the api and if ratelimited, waits and tries again"""

        try_again = True
        self.waiting += 1
        while try_again:
            try:
                awaited = await to_be_awaited
                try_again = False
            except aiopypixel.exceptions.exceptions.RateLimitError:
                await asyncio.sleep(self.bot.ratelimited_wait_time)
        self.waiting -= 1
        return awaited

    async def get_player(self, player):  # uuid preferred
        """Gets a player object via uuid or username, prefers a uuid"""

        player = await self.get_player_uuid(player)

        player_object = self.player_object_cache.get(player)

        if player_object is None:
            player_object = await self.rate_limit_wait(self.hypixel.getPlayer(player))
            self.player_object_cache[player] = player_object
        return player_object

    async def get_player_friends(self, player):
        """Fetches the friends of a given player via name or uuid, prefers a uuid"""

        player = await self.get_player_uuid(player)  # ensure it's a uuid for best caching results

        friends = self.player_friends_cache.get(player)

        if friends is None:
            friends = await self.rate_limit_wait(self.hypixel.getPlayerFriends(player))
            self.player_friends_cache[player] = friends
        return friends

    async def get_player_guild(self, player):
        """Gets the guild of a player via name or uuid, prefers a uuid"""

        player = await self.get_player_uuid(player)

        guild_id = self.player_guild_cache.get(player)

        if guild_id is None:
            guild_id = await self.rate_limit_wait(self.hypixel.getPlayerGuild(player))
            self.player_guild_cache[player] = guild_id
        return guild_id

    async def get_player_head(self, player):
        """Returns a valid craftatar url for a player's head, prefers uuid"""
        print(player)
        player = await self.get_player_uuid(player)
        return f"https://crafatar.com/avatars/{player}"

    async def get_guild_name_from_id(self, guild_id):
        """Fetches a hypixel guild's name via a hypixel guild id"""

        guild_name = self.guild_id_name_cache.get(guild_id)

        if guild_name is None:
            guild_name = await self.rate_limit_wait(self.hypixel.getGuildNameByID(guild_id))
            self.guild_id_name_cache[guild_id] = guild_name
        return guild_name

    async def get_guild_id_from_name(self, guild_name):
        """Fetches a hypixel guild id from a hypixel guild's name"""

        guild_id = self.guild_id_name_cache.get(guild_name)

        if guild_id is None:
            guild_id = await self.rate_limit_wait(self.hypixel.getGuildIDByName(guild_name))
            self.guild_id_name_cache[guild_name] = guild_id
        return guild_id

    async def get_guild(self, guild_id):
        """"Returns an aiopypixel guild object from a hypixel guild id"""

        guild = self.guild_cache.get(guild_id)

        if guild is None:
            guild = await self.rate_limit_wait(self.hypixel.getGuildData(guild_id))
            self.guild_cache[guild_id] = guild
        return guild

    async def get_skyblock_stats(self, profile: str) -> dict:
        """gets skyblock statistics of the provided profile"""

        sb = self.skyblock_cache.get(profile)

        if sb is None:
            sb = await self.rate_limit_wait(self.hypixel.getSkyblockStats(profile))
            self.skyblock_cache[profile] = sb

        return sb

    async def get_watchdog_stats(self):
        """returns watchdog stats"""

        if self.watchdog_cached is None:
            return await self.hypixel.getWatchdogStats()
        return self.watchdog_cached

    async def get_key_data(self, key: str):
        """returns data for a given key"""

        return await self.hypixel.getKeyData(key)  # See? Not storing the keys ty very much


def setup(bot):
    bot.add_cog(Cache(bot))
