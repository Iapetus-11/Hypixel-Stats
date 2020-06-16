import aiohttp
import aiopypixel
import asyncio
import discord
from discord.ext import commands


class Cache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def reset_continuous(self):
        while self.bot.is_ready():
            await asyncio.sleep(1)
            while len(self.valid_names_and_uuids) > len(self.bot.guilds) * 3:  # reset valid names + uuids
                self.valid_names_and_uuids.pop(0)

    async def reset_10_minutes(self):
        while self.bot.is_ready():
            await asyncio.sleep(60 * 10)
            self.player_object_cache = {}

    async def reset_1_hour(self):
        while self.bot.is_ready():
            await asyncio.sleep(60 * 60)
            self.player_guild_cache = {}

    async def reset_2_hours(self):
        while self.bot.is_ready():
            await asyncio.sleep(60 * 60 * 2)
            self.player_friends_cache = {}
            self.guild_cache = {}
            self.guild_id_name_cache = {}

    async def reset_6_hours(self):
        while self.bot.is_ready():
            await asyncio.sleep(60 * 60 * 6)
            self.name_uuid_cache = {}
            self.uuid_name_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1)
        self.bot.loop.create_task(self.reset_continuous())
        self.bot.loop.create_task(self.reset_10_minutes())
        self.bot.loop.create_task(self.reset_1_hour())
        self.bot.loop.create_task(self.reset_2_hours())
        self.bot.loop.create_task(self.reset_6_hours())

    async def get_player_uuid(self, player):
        if len(player) > 16:
            if player in self.valid_names_and_uuids:
                return player

        uuid = self.name_uuid_cache.get(player)

        if uuid is None:
            uuid = await self.hypixel.usernameToUUID(player)
            self.name_uuid_cache[player] = uuid

        if uuid not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(uuid)
        return uuid

    async def get_player_name(self, player):
        if len(player) <= 16:
            if player in self.valid_names_and_uuids:
                return player

        name = self.uuid_name_cache.get(player)

        if name is None:
            name = await self.hypixel.UUIDToUsername(player)
            self.uuid_name_cache[player] = name

        if name not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(name)
        return name

    async def rate_limit_wait(self, to_be_awaited):
        try_again = True
        self.waiting += 1
        while try_again:
            try:
                awaited = await to_be_awaited
                try_again = False
            except aiopypixel.exceptions.exceptions.RateLimitError:
                await asyncio.sleep(self.bot.ratelimited)
        self.waiting -= 1
        return awaited

    async def get_player(self, player):  # uuid preferred
        player = await self.get_player_uuid(player)

        player_object = self.player_object_cache.get(player)

        if player_object is None:
            player_object = await self.rate_limit_wait(self.hypixel.getPlayer(player))
            self.player_object_cache[player] = player_object
        return player_object

    async def get_player_friends(self, player):
        player = await self.get_player_uuid(player)  # ensure it's a uuid for best caching results

        friends = self.player_friends_cache.get(player)

        if friends is None:
            friends = await self.rate_limit_wait(self.hypixel.getPlayerFriends(player))
            self.player_friends_cache[player] = friends
        return friends

    async def get_player_guild(self, player):
        player = await self.get_player_uuid(player)

        guild_id = self.player_guild_cache.get(player)

        if guild_id is None:
            guild_id = await self.rate_limit_wait(self.hypixel.getPlayerGuild(player))
            self.player_guild_cache[player] = guild_id
        return guild_id

    async def get_player_head(self, player):
        player = await self.get_player_uuid(player)
        return f"https://crafatar.com/avatars/{player}"

    async def get_guild_name_from_id(self, guild_id):
        guild_name = self.guild_id_name_cache.get(guild_id)

        if guild_name is None:
            guild_name = await self.rate_limit_wait(self.hypixel.getGuildNameByID(guild_id))
            self.guild_id_name_cache[guild_id] = guild_name
        return guild_name

    async def get_guild_id_from_name(self, guild_name):
        guild_id = self.guild_id_name_cache.get(guild_name)

        if guild_id is None:
            guild_id = await self.rate_limit_wait(self.hypixel.getGuildIDByName(guild_name))
            self.guild_id_name_cache[guild_name] = guild_id
        return guild_id

    async def get_guild(self, guild_id):
        guild = self.guild_cache.get(guild_id)

        if guild is None:
            guild = await self.rate_limit_wait(self.hypixel.getGuildData(guild_id))
            self.guild_cache[guild_id] = guild
        return guild


def setup(bot):
    bot.add_cog(Cache(bot))
